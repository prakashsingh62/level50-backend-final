import os

# -------------------------------------------------------------
# Level-50 FINAL CONFIG (NO TEST MODE)
# -------------------------------------------------------------

# Always use production mode for Level-50 live automation
MODE = "PROD"

# -------------------------------------------------------------
# Google Sheets Settings
# -------------------------------------------------------------
PROD_SHEET_ID = os.getenv("PROD_SHEET_ID")   # MUST be set in Railway
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")

if not PROD_SHEET_ID:
    raise RuntimeError("Missing env var: PROD_SHEET_ID")

if not SERVICE_ACCOUNT_JSON:
    raise RuntimeError("Missing env var: SERVICE_ACCOUNT_JSON")

# -------------------------------------------------------------
# SendGrid Settings
# -------------------------------------------------------------
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

if not SENDGRID_API_KEY:
    raise RuntimeError("Missing env var: SENDGRID_API_KEY")

# -------------------------------------------------------------
# Email recipients (comma separated in Railway)
# -------------------------------------------------------------
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "")
