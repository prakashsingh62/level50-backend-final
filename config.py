import os
import json

# ----------------------------------------
# Load Service Account JSON (as string)
# ----------------------------------------
CLIENT_SECRET_JSON = os.getenv("CLIENT_SECRET_JSON")
if not CLIENT_SECRET_JSON:
    raise RuntimeError("Missing env var: CLIENT_SECRET_JSON")

SERVICE_ACCOUNT_INFO = json.loads(CLIENT_SECRET_JSON)

# ----------------------------------------
# Email settings
# ----------------------------------------
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "")
RECIPIENT_LIST = [x.strip() for x in EMAIL_RECIPIENTS.split(",") if x.strip()]

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

if not SENDGRID_API_KEY:
    raise RuntimeError("Missing env var: SENDGRID_API_KEY")
if not SENDGRID_FROM_EMAIL:
    raise RuntimeError("Missing env var: SENDGRID_FROM_EMAIL")

# ----------------------------------------
# Sheet settings
# ----------------------------------------
PROD_SHEET_ID = os.getenv("PROD_SHEET_ID")
PROD_TAB = os.getenv("PROD_TAB")

if not PROD_SHEET_ID:
    raise RuntimeError("Missing env var: PROD_SHEET_ID")
if not PROD_TAB:
    raise RuntimeError("Missing env var: PROD_TAB")

# ----------------------------------------
# Mode (always PROD)
# ----------------------------------------
MODE = os.getenv("MODE", "PROD").upper()
if MODE not in ["PROD"]:
    raise RuntimeError("Invalid MODE env var. Allowed: PROD only")
