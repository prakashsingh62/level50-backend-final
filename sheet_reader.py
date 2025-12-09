import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import CLIENT_SECRET_JSON, PROD_SHEET_ID, PROD_TAB

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def load_service_account():
    """
    Handles both:
    - dict (Railway auto-parsed)
    - string (raw JSON)
    """
    if isinstance(CLIENT_SECRET_JSON, dict):
        return CLIENT_SECRET_JSON

    if isinstance(CLIENT_SECRET_JSON, str):
        try:
            return json.loads(CLIENT_SECRET_JSON)
        except Exception:
            # If Railway escaped it incorrectly, try aggressive fix
            cleaned = CLIENT_SECRET_JSON.replace('\\"', '"')
            return json.loads(cleaned)

    raise ValueError("Invalid CLIENT_SECRET_JSON format")


def read_sheet():
    service_info = load_service_account()

    credentials = service_account.Credentials.from_service_account_info(
        service_info,
        scopes=SCOPES
    )

    service = build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()
    range_name = f"{PROD_TAB}!A:Z"

    result = sheet.values().get(
        spreadsheetId=PROD_SHEET_ID,
        range=range_name
    ).execute()

    values = result.get("values", [])

    # Convert rows into dicts
    if not values:
        return []

    headers = values[0]
    rows = []

    for row in values[1:]:
        row_dict = {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
        rows.append(row_dict)

    return rows
