import json
import os

# Paste your full service account JSON as a python dict here
CLIENT_SECRET_JSON = {
    "type": "service_account",
    "project_id": "vepl-rfq",
    "private_key_id": "YOUR_KEY_ID",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n",
    "client_email": "level50-backend-final@vepl-rfq.iam.gserviceaccount.com",
    "client_id": "110687579827756007110",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/.../your-cert-url"
}

# NEW SHEET
PROD_SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
PROD_TAB = "RFQ TEST SHEET"

# Email settings
MAIL_TO = ["sales@ventilengineering.com"]
