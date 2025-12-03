import os
import json

# READ SERVICE ACCOUNT JSON SAFELY
CLIENT_SECRET_JSON = os.getenv("CLIENT_SECRET_JSON")

if not CLIENT_SECRET_JSON:
    raise RuntimeError("Missing env var: CLIENT_SECRET_JSON")

SERVICE_ACCOUNT_INFO = json.loads(CLIENT_SECRET_JSON)

# GOOGLE SHEET CONFIG
SHEET_ID = os.getenv("PROD_SHEET_ID")
SHEET_TAB = os.getenv("PROD_TAB")

if not SHEET_ID:
    raise RuntimeError("Missing env var: PROD_SHEET_ID")

if not SHEET_TAB:
    raise RuntimeError("Missing env var: PROD_TAB")

# EMAIL CONFIG
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS")

if not SENDGRID_API_KEY:
    raise RuntimeError("Missing env var: SENDGRID_API_KEY")

if not SENDGRID_FROM_EMAIL:
    raise RuntimeError("Missing env var: SENDGRID_FROM_EMAIL")

if not EMAIL_RECIPIENTS:
    raise RuntimeError("Missing env var: EMAIL_RECIPIENTS")

# MODE IS ALWAYS PROD (NO TEST MODE ANYWHERE)
MODE = "PROD"
