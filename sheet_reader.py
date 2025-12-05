import os, json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def get_service():
    info = json.loads(os.environ["CLIENT_SECRET_JSON"])

    creds = Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    return build("sheets", "v4", credentials=creds)

def read_rows():
    service = get_service()
    sheet_id = os.environ["PROD_SHEET_ID"]
    tab = os.environ["PROD_TAB"]

    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=f"{tab}!A:Z"
    ).execute()

    return result.get("values", [])
