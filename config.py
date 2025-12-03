import os
import json

# ---------------------------------------------------------
#  READ SERVICE ACCOUNT JSON FROM ENV
# ---------------------------------------------------------
raw_json = os.getenv("CLIENT_SECRET_JSON")
if not raw_json:
    raise RuntimeError("Missing env var: CLIENT_SECRET_JSON")

try:
    SERVICE_ACCOUNT_INFO = json.loads(raw_json)
except Exception as e:
    raise RuntimeError(f"Invalid CLIENT_SECRET_JSON value: {e}")

# ---------------------------------------------------------
#  MODE — Only PROD is allowed
# ---------------------------------------------------------
MODE = "PROD"

# ---------------------------------------------------------
#  SHEET CONFIG (PROD ONLY)
# ---------------------------------------------------------
PROD_SHEET_ID = os.getenv("PROD_SHEET_ID")
PROD_TAB = os.getenv("PROD_TAB")

if not PROD_SHEET_ID:
    raise RuntimeError("Missing env var: PROD_SHEET_ID")

if not PROD_TAB:
    raise RuntimeError("Missing env var: PROD_TAB")

SHEET_ID = PROD_SHEET_ID
SHEET_TAB = PROD_TAB

# ---------------------------------------------------------
#  EMAIL SETTINGS
# ---------------------------------------------------------
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS")

if not SENDGRID_API_KEY:
    raise RuntimeError("Missing env var: SENDGRID_API_KEY")

if not SENDGRID_FROM_EMAIL:
    raise RuntimeError("Missing env var: SENDGRID_FROM_EMAIL")

if not EMAIL_RECIPIENTS:
    raise RuntimeError("Missing env var: EMAIL_RECIPIENTS")

EMAIL_RECIPIENTS = [email.strip() for email in EMAIL_RECIPIENTS.split(",") if email.strip()]
