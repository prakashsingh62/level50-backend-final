import json
import os
import gspread
from google.oauth2.service_account import Credentials
from config import MODE, TEST_SHEET_ID, TEST_TAB, PROD_SHEET_ID, PROD_TAB

IMMUTABLE = {
    "SALES PERSON","CUSTOMER NAME","LOCATION","RFQ NO","RFQ DATE",
    "PRODUCT","UID NO","UID DATE","DUE DATE","VENDOR","CONCERN PERSON"
}

def get_ws():
    client_secret = os.getenv("CLIENT_SECRET_JSON")
    if not client_secret:
        raise RuntimeError("Missing CLIENT_SECRET_JSON")
    creds_dict = json.loads(client_secret)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    if MODE == "TEST":
        return client.open_by_key(TEST_SHEET_ID).worksheet(TEST_TAB)
    return client.open_by_key(PROD_SHEET_ID).worksheet(PROD_TAB)


def write_updates(rows):
    ws = get_ws()
    headers = ws.row_values(1)
    header_map = {h: (i + 1) for i, h in enumerate(headers)}

    batch = []

    for r in rows:
        row_no = r.get("_ROW")
        if not row_no:
            continue  # protect from malformed rows

        for k, v in r.items():
            if k in ("_ROW",):
                continue

            if k not in header_map:
                continue

            if k in IMMUTABLE:
                continue

            col_no = header_map[k]
            batch.append({
                "range": f"{ws.title}!{gspread.utils.rowcol_to_a1(row_no, col_no)}",
                "values": [[str(v) if v is not None else ""]]
            })

    if batch:
        ws.batch_update(batch)
