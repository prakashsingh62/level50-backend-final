# ================================
# BEGIN PATCH — sheet_reader.py
# ================================

import json, os, time
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from config import MODE, TEST_SHEET_ID, TEST_TAB, PROD_SHEET_ID, PROD_TAB

# -------------------------------
# GLOBALS
# -------------------------------
local_cache = None
local_cache_timestamp = 0

CACHE_EXPIRY = 300              # 5 minutes
CACHE_FILE = "/tmp/rfq_cache.json"


# -------------------------------
# Persistent Cache Helpers
# -------------------------------
def load_persistent_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_persistent_cache(obj):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(obj, f)
    except:
        pass


def compute_checksum(data):
    """Very light checksum to detect data changes."""
    try:
        return hash(str(data))
    except:
        return 0


# -------------------------------
# GOOGLE SHEET CONNECTION
# -------------------------------
def get_ws():
    client_secret = os.getenv("CLIENT_SECRET_JSON")
    creds_dict = json.loads(client_secret)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    # Select sheet based on MODE
    if MODE == "TEST":
        return client.open_by_key(TEST_SHEET_ID).worksheet(TEST_TAB)
    else:
        return client.open_by_key(PROD_SHEET_ID).worksheet(PROD_TAB)


# -------------------------------
# MAIN FUNCTION: read_rows()
# -------------------------------
def read_rows():
    global local_cache, local_cache_timestamp

    now = time.time()

    # ----------------------------------------------------
    # 1) Use in-memory cache if fresh
    # ----------------------------------------------------
    if local_cache and (now - local_cache_timestamp) < CACHE_EXPIRY:
        return local_cache

    # ----------------------------------------------------
    # 2) Load persistent disk cache
    # ----------------------------------------------------
    disk_cache = load_persistent_cache()
    disk_values = disk_cache.get("values") or []
    disk_checksum = disk_cache.get("checksum", None)

    # ----------------------------------------------------
    # 3) Try reading Google Sheet (main source)
    # ----------------------------------------------------
    try:
        ws = get_ws()
        data = ws.get_all_records()

        # Assign _ROW numbers
        for i, r in enumerate(data, start=2):
            r["_ROW"] = i

        # Update memory cache
        local_cache = data
        local_cache_timestamp = time.time()

        # Update disk cache
        disk_cache = {
            "values": data,
            "checksum": compute_checksum(data)
        }
        save_persistent_cache(disk_cache)

        return data

    except Exception:
        # ----------------------------------------------------
        # 4) If Google API fails → use stable disk cache
        # ----------------------------------------------------
        if disk_values:
            return disk_values

        # ----------------------------------------------------
        # 5) If nothing available → return safe empty
        # ----------------------------------------------------
        return []


# ================================
# END PATCH — sheet_reader.py
# ================================
