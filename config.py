import json
import os

# ------------------------------------------------------------
# GOOGLE SERVICE ACCOUNT
# ------------------------------------------------------------

CLIENT_SECRET_JSON = json.loads(os.getenv("CLIENT_SECRET_JSON", "{}"))

# ------------------------------------------------------------
# PRODUCTION SHEET (MAIN RFQ SHEET)
# ------------------------------------------------------------

PROD_SHEET_ID = os.getenv("PROD_SHEET_ID")
PROD_TAB = os.getenv("PROD_TAB")

# ------------------------------------------------------------
# AUDIT LOG SHEET (LEVEL 80)
# ------------------------------------------------------------

AUDIT_SHEET_ID = os.getenv(
    "AUDIT_SHEET_ID",
    "1g4BXp2wa6-vZPxSokAv3v8hwoFiR39fb2bmVNi_y0Mc"
)

AUDIT_TAB = os.getenv(
    "AUDIT_TAB",
    "LEVEL_80_AUDIT_LOG"
)

# ------------------------------------------------------------
# MODE
# ------------------------------------------------------------

MODE = os.getenv("MODE", "PROD")
