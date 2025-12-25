import json
import os

# Load the service account JSON from Railway variable
CLIENT_SECRET_JSON = json.loads(os.getenv("CLIENT_SECRET_JSON", "{}"))

# Sheet settings
PROD_SHEET_ID = os.getenv("PROD_SHEET_ID")
PROD_TAB = os.getenv("PROD_TAB")

# Email settings
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "sales@ventilengineering.com")

# ------------------------------------------------------------
# GLOBAL CONFIG (FINAL)
# ------------------------------------------------------------

# Google Sheet ID (LEVEL_80_AUDIT_LOG)
SHEET_ID = "1g4BXp2wa6-vZPxSokAv3v8hwoFiR39fb2bmVNi_y0Mc"

# Mode (optional)
MODE = os.getenv("MODE", "PROD")
