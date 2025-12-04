import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SHEET_ID = os.getenv("PROD_SHEET_ID")
TAB_NAME = os.getenv("PROD_TAB")

def load_credentials():
    service_json = os.getenv("CLIENT_SECRET_JSON")
    data = json.loads(service_json)
    creds = Credentials.from_service_account_info(
        data,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return creds

def read_sheet():
    creds = load_credentials()
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets().values()

    result = sheet.get(
        spreadsheetId=SHEET_ID,
        range=f"{TAB_NAME}!A:Z"
    ).execute()

    return result.get("values", [])
