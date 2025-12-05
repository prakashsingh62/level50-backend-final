import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


def get_service():
    # Load service account JSON from Railway variable (correct name)
    info = json.loads(os.environ["CLIENT_SECRET_JSON"])

    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    service = build("sheets", "v4", credentials=creds)
    return service


def read_rows():
    service = get_service()

    sheet_id = os.environ["PROD_SHEET_ID"]
    tab_name = os.environ["PROD_TAB"]

    try:
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"{tab_name}!A:Z")
            .execute()
        )

        rows = result.get("values", [])
        return rows

    except Exception as e:
        raise Exception(f"Google Sheet read failed: {e}")
