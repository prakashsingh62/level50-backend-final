import os
import json

CLIENT_SECRET_JSON = json.loads(os.getenv("CLIENT_SECRET_JSON", "{}"))

# MAIN SHEET
PROD_SHEET_ID = os.getenv("PROD_SHEET_ID")
PROD_TAB = os.getenv("PROD_TAB")

# LEGACY COMPAT (DO NOT TOUCH)
SHEET_ID = PROD_SHEET_ID

# ✅ SINGLE AUDIT SOURCE OF TRUTH
AUDIT_SHEET_ID = os.getenv(
    "AUDIT_SHEET_ID",
    "1g4BXp2wa6-vZPxSokAv3v8hwoFiR39fb2bmVNi_y0Mc"
)

AUDIT_TAB = "LEVEL_80_AUDIT_LOG"

MODE = os.getenv("MODE", "PROD")
