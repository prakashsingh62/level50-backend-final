import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import CLIENT_SECRET_JSON, PROD_SHEET_ID, PROD_TAB

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def load_service_account():
    """
    Handles both:
    - dict (Railway auto-parsed from JSON)
    - string (raw JSON stored in variable)
    """
    # If Railway already parsed JSON → dict
    if isinstance(CLIENT_SECRET_JSON, dict):
        return CLIENT_SECRET_JSON

    # If string, try normal loads
    if isinstance(CLIENT_SECRET_JSON, str):
        try:
            return json.loads(CLIENT_SECRET_JSON)
        except Exception:
            # Fallback if escaped
            cleaned = CLIENT_SECRET_JSON.replace('\\"', '"')
            return json.loads(cleaned)

    raise ValueError("Invalid CLIENT_SECRET_JSON format")


def read_sheet():
    """
    Reads complete A:Z range and returns row dicts.
    """
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
    if not values:
        return []

    headers = values[0]
    rows = []

    for row in values[1:]:
        row_dict = {
            headers[i]: (row[i] if i < len(row) else "")
            for i in range(len(headers))
        }
        rows.append(row_dict)

    return rows


# ---------------------------------------------------------
# BACKWARD COMPATIBILITY (old code still imports read_rows)
# ---------------------------------------------------------
def read_rows():
    return read_sheet()
