import os, json

MODE = os.environ.get("MODE", "PROD")

SERVICE_JSON = json.loads(os.environ["CLIENT_SECRET_JSON"])
SHEET_ID = os.environ["PROD_SHEET_ID"]
TAB_NAME = os.environ["PROD_TAB"]
SENDGRID_KEY = os.environ["SENDGRID_API_KEY"]
