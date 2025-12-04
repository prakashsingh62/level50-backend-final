import json
import os

# Load service account JSON from Railway environment variable
CLIENT_SECRET_JSON = json.loads(os.getenv("CLIENT_SECRET_JSON"))

# Sheet configuration
PROD_SHEET_ID = os.getenv("PROD_SHEET_ID", "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo")
PROD_TAB = os.getenv("PROD_TAB", "RFQ TEST SHEET")

# Email settings
MAIL_TO = ["sales@ventilengineering.com"]
