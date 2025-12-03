import gspread
from google.oauth2.service_account import Credentials
from config import CLIENT_SECRET_JSON, PROD_SHEET_ID, PROD_TAB
import json

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def get_client():
    creds = Credentials.from_service_account_info(CLIENT_SECRET_JSON, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def get_worksheet():
    client = get_client()
    sheet = client.open_by_key(PROD_SHEET_ID)
    ws = sheet.worksheet(PROD_TAB)
    return ws


def write_updates(update_list):
    """
    Accepts a LIST of updates:
    [
        {"row": 5, "column": "STATUS", "value": "PENDING"},
        {"row": 12, "column": "AGING", "value": "3"}
    ]
    """

    BLOCKED_COLUMNS = [
        "SALES PERSON", "CUSTOMER NAME", "LOCATION", "RFQ NO", "RFQ DATE",
        "PRODUCT", "UID NO", "UID DATE", "DUE DATE", "VENDOR", "CONCERN PERSON"
    ]

    ws = get_worksheet()
    headers = ws.row_values(1)

    for upd in update_list:
        row = upd["row"]
        col_name = upd["column"]
        value = upd["value"]

        # Skip protected fields
        if col_name in BLOCKED_COLUMNS:
            continue

        if col_name in headers:
            col_index = headers.index(col_name) + 1
            ws.update_cell(row, col_index, value)

    return True


def write_test_row():
    ws = get_worksheet()
    ws.append_row(["TEST_WRITE_OK"], value_input_option="USER_ENTERED")
    return True
