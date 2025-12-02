import os
import json
from typing import List

def _env_required(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val

def _env_list(key: str, default_list: List[str] = None) -> List[str]:
    s = os.getenv(key)
    if s:
        return [x.strip() for x in s.split(",") if x.strip()]
    return default_list or []

# MODE: must be explicit. Default to TEST for safety in dev, but fail-fast if invalid.
MODE = os.getenv("MODE", "TEST").upper()
if MODE not in ("TEST", "PROD"):
    raise RuntimeError("Invalid MODE env var. Allowed: TEST or PROD")

# Sheets: require explicit sheet ids/tabs
PROD_SHEET_ID = os.getenv("PROD_SHEET_ID") or ""
PROD_TAB = os.getenv("PROD_TAB") or ""

# Optionally allow explicit test sheet; otherwise falls back to prod (explicit behavior).
TEST_SHEET_ID = os.getenv("TEST_SHEET_ID") or PROD_SHEET_ID
TEST_TAB = os.getenv("TEST_TAB") or PROD_TAB

# Validate critical sheet config early
if MODE == "PROD":
    if not PROD_SHEET_ID or not PROD_TAB:
        raise RuntimeError("PROD_SHEET_ID and PROD_TAB must be set when MODE=PROD")
else:
    # TEST mode: ensure at least one sheet is configured
    if not TEST_SHEET_ID or not TEST_TAB:
        raise RuntimeError("TEST_SHEET_ID and TEST_TAB must be set when MODE=TEST (or set PROD vars)")

# CLIENT_SECRET_JSON validation (used by sheet_reader)
CLIENT_SECRET_JSON = os.getenv("CLIENT_SECRET_JSON")
if not CLIENT_SECRET_JSON:
    raise RuntimeError("Missing CLIENT_SECRET_JSON environment variable (service account JSON).")
# quick sanity check for valid JSON
try:
    _ = json.loads(CLIENT_SECRET_JSON)
except Exception as e:
    raise RuntimeError("CLIENT_SECRET_JSON is not valid JSON: " + str(e))

# Recipients: prefer env override, fallback to in-code lists
TEST_RECIPIENTS = _env_list("TEST_RECIPIENTS", ["sales@ventilengineering.com"])
PROD_RECIPIENTS = _env_list("PROD_RECIPIENTS", ["sales@ventilengineering.com"])

# Optional: expose a convenience bool
IS_TEST = MODE == "TEST"
