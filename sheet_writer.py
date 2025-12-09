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

def write_test_row():
    creds = load_credentials()
    service = build("sheets", "v4", credentials=creds)

    values = [["TEST", "WRITE", "SUCCESS"]]

    body = {"values": values}

    result = service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=f"{TAB_NAME}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    return result
