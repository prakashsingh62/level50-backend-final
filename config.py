import os
import json

# ---------------------------------------------------------
# MODE
# ---------------------------------------------------------
MODE = os.getenv("MODE", "PROD").upper()
if MODE not in ("PROD", "TEST"):
    raise RuntimeError("Invalid MODE env var. Allowed: TEST or PROD")

# ---------------------------------------------------------
# GOOGLE SERVICE ACCOUNT CREDENTIALS
# ---------------------------------------------------------
CLIENT_SECRET_JSON_STR = os.getenv("CLIENT_SECRET_JSON")
if not CLIENT_SECRET_JSON_STR:
    raise RuntimeError("Missing env var: CLIENT_SECRET_JSON")

# Parsed dict version we will use everywhere
CLIENT_SECRET_JSON = json.loads(CLIENT_SECRET_JSON_STR)

# ---------------------------------------------------------
# SHEET SETTINGS
# ---------------------------------------------------------
PROD_SHEET_ID = os.getenv("PROD_SHEET_ID")
PROD_TAB = os.getenv("PROD_TAB")

if not PROD_SHEET_ID or not PROD_TAB:
    raise RuntimeError("Missing env vars: PROD_SHEET_ID or PROD_TAB")

# ---------------------------------------------------------
# EMAIL SETTINGS
# ---------------------------------------------------------
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

if not SENDGRID_API_KEY:
    raise RuntimeError("Missing env var: SENDGRID_API_KEY")

if not SENDGRID_FROM_EMAIL:
    raise RuntimeError("Missing env var: SENDGRID_FROM_EMAIL")
