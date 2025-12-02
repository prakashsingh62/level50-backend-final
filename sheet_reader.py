import os
import json
import time
import hashlib
import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError
from config import MODE, TEST_SHEET_ID, TEST_TAB, PROD_SHEET_ID, PROD_TAB

# =============================
# GLOBALS
# =============================
CACHE_FILE = "cache.json"
CACHE_EXPIRY = 30          # seconds — cached sheet valid for 30s
MAX_RETRIES = 5            # backoff retries before giving up
COOLDOWN_TIME = 60         # circuit breaker cooldown after quota errors
RANGE = "A:AT"             # Full sheet range

last_google_fail = 0       # timestamp of last quota block
local_cache = None         # memory cache
local_cache_timestamp = 0  # timestamp of last memory cache load


# =============================
# HELPER: Load cache.json
# =============================
def load_persistent_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return None


# =============================
# HELPER: Save cache.json
# =============================
def save_persistent_cache(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except:
        pass


# =============================
# HELPER: Create Google Client
# =============================
def get_client():
    global last_google_fail

    # Circuit breaker — if recently blocked, do NOT call Google
    if time.time() - last_google_fail < COOLDOWN_TIME:
        return None  # Use cache fallback

    try:
        creds_dict = json.loads(os.getenv("CLIENT_SECRET_JSON"))
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)

    except Exception as e:
        last_google_fail = time.time()
        return None


# =============================
# HELPER: Get Worksheet
# =============================
def get_ws(client):
    global last_google_fail

    if client is None:
        return None

    try:
        if MODE == "TEST":
            ss = client.open_by_key(TEST_SHEET_ID)
            return ss.worksheet(TEST_TAB)

        ss = client.open_by_key(PROD_SHEET_ID)
        return ss.worksheet(PROD_TAB)

    except Exception as e:
        # Google blocked metadata request
        last_google_fail = time.time()
        return None

# =============================
# HELPER: Read Google Sheet with Retry + Backoff
# =============================
def read_google_sheet(ws):
    global last_google_fail

    if ws is None:
        last_google_fail = time.time()
        return None

    backoff = 1
    for attempt in range(MAX_RETRIES):
        try:
            values = ws.get(RANGE)
            if values:
                return values
            return None

        except APIError as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                last_google_fail = time.time()  # trigger cooldown
                time.sleep(backoff)
                backoff *= 2
                continue

            return None

        except Exception:
            last_google_fail = time.time()
            return None

    return None


# =============================
# HELPER: Compute sheet checksum
# =============================
def compute_checksum(values):
    try:
        raw = json.dumps(values, sort_keys=True)
        return hashlib.md5(raw.encode()).hexdigest()
    except:
        return ""


# =============================
# MAIN FUNCTION: read_rows()
# =============================
def read_rows():
    global local_cache, local_cache_timestamp

    now = time.time()

    # =============================
    # 1) If memory cache fresh → return it
    # =============================
    if local_cache and (now - local_cache_timestamp) < CACHE_EXPIRY:
        return local_cache

    # =============================
    # 2) Load persistent cache if needed
    # =============================
    disk_cache = load_persistent_cache() or {}
    disk_values = disk_cache.get("values")
    disk_checksum = disk_cache.get("checksum")

    # =============================
    # 3) Try reading Google Sheet
    # =============================
    client = get_client()
    ws = get_ws(client)
    google_values = read_google_sheet(ws)

    # =============================
    # 4) If Google unavailable → fallback to persistent cache
    # =============================
    if google_values is None:
        if disk_values:
            local_cache = disk_values
            local_cache_timestamp = now
            return local_cache

        return []  # no data

    # =============================
    # 5) If Google data same as disk cache → reuse disk cache
    # =============================
    google_checksum = compute_checksum(google_values)

    if google_checksum == disk_checksum:
        local_cache = disk_values
        local_cache_timestamp = now
        return local_cache

    # =============================
    # 6) Convert Google values → dict rows
    # =============================
    header = google_values[0]
    rows = google_values[1:]

    final = []
    for i, row in enumerate(rows, start=2):
        record = {}
        for col_idx, col_value in enumerate(row):
            key = header[col_idx] if col_idx < len(header) else f"COL_{col_idx}"
            record[key] = col_value
        record["_ROW"] = i
        final.append(record)

    # =============================
    # 7) Save updated persistent cache
    # =============================
    save_persistent_cache({
        "values": final,
        "checksum": google_checksum,
        "timestamp": now
    })

    # =============================
    # 8) Save memory cache
    # =============================
    local_cache = final
    local_cache_timestamp = now
    return final
