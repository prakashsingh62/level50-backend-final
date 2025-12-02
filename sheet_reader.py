import json, os, gspread
from google.oauth2.service_account import Credentials
from config import MODE, TEST_SHEET_ID, TEST_TAB, PROD_SHEET_ID, PROD_TAB


def get_ws():
    client_secret = os.getenv("CLIENT_SECRET_JSON")
    creds_dict = json.loads(client_secret)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    if MODE == "TEST":
        return client.open_by_key(TEST_SHEET_ID).worksheet(TEST_TAB)

    return client.open_by_key(PROD_SHEET_ID).worksheet(PROD_TAB)


def read_rows():
    ws = get_ws()

    # Read FULL sheet A → AT
    values = ws.get("A:AT")

    if not values:
        return []

    header = values[0]
    data_rows = values[1:]

    final = []
    for i, row in enumerate(data_rows, start=2):
        record = {}

        for col_index, col_value in enumerate(row):
            if col_index < len(header):
                key = header[col_index]
            else:
                key = f"COL_{col_index}"

            record[key] = col_value

        record["_ROW"] = i
        final.append(record)

    return final
