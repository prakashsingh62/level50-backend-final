import json
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "1hKMwlnN3GAE4dxVGvq2WHT2-Om9SJ3P91L8cxioAeoo"
TAB_NAME = "RFQ TEST SHEET"

creds = Credentials.from_service_account_file(
    "client_secret.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID).worksheet(TAB_NAME)
rows = sheet.get_all_records()

with open("data_cache.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)

print("data_cache.json generated successfully!")
