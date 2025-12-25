import os
import json

# ============================================================
# GOOGLE SERVICE ACCOUNT
# ============================================================

# Loaded from Railway environment variable
CLIENT_SECRET_JSON = json.loads(os.getenv("CLIENT_SECRET_JSON", "{}"))

# ============================================================
# MAIN PRODUCTION SHEET (RFQ DATA)
# ============================================================

PROD_SHEET_ID = os.getenv("PROD_SHEET_ID")
PROD_TAB = os.getenv("PROD_TAB")

# ------------------------------------------------------------
# 🔒 LEGACY COMPATIBILITY (DO NOT REMOVE)
# Required by core/phase11_runner.py and older modules
# ------------------------------------------------------------

SHEET_ID = PROD_SHEET_ID

# ============================================================
# AUDIT LOG SHEET (LEVEL 80)
# ============================================================

AUDIT_SHEET_ID = os.getenv(
    "AUDIT_SHEET_ID",
    "1g4BXp2wa6-vZPxSokAv3v8hwoFiR39fb2bmVNi_y0Mc"
)

AUDIT_TAB = os.getenv(
    "AUDIT_TAB",
    "LEVEL_80_AUDIT_LOG"
)

# ============================================================
# MODE
# ============================================================

MODE = os.getenv("MODE", "PROD")
