# config.py — FINAL LEVEL-50 CONFIG (NO TEST MODE)

import os

# Google Sheet Configuration
SHEET_ID = os.getenv("PROD_SHEET_ID")
TAB_NAME = os.getenv("PROD_TAB")

# Email Recipients (comma-separated)
EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "")

# SendGrid Configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

# Service Account JSON
SERVICE_ACCOUNT_JSON = os.getenv("CLIENT_SECRET_JSON")

# MODE — always PROD (debug handled via ?debug=true in API)
MODE = "PROD"

# Validation checks
if not SHEET_ID:
    raise Exception("Missing environment variable: PROD_SHEET_ID")

if not TAB_NAME:
    raise Exception("Missing environment variable: PROD_TAB")

if not SENDGRID_API_KEY:
    raise Exception("Missing environment variable: SENDGRID_API_KEY")

if not SENDGRID_FROM_EMAIL:
    raise Exception("Missing environment variable: SENDGRID_FROM_EMAIL")

if not SERVICE_ACCOUNT_JSON:
    raise Exception("Missing environment variable: CLIENT_SECRET_JSON")
