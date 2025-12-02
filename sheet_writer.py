from __future__ import annotations
import gspread
from google.oauth2.service_account import Credentials
from config import (
    CLIENT_SECRET_JSON,
    PROD_SHEET_ID,
    PROD_TAB,
)
import json

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client():
    """Authenticate using service account JSON stored in env variable."""
    info = json.loads(CLIENT_SECRET_JSON)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


def get_worksheet():
    """Return worksheet reference for SAFE writing."""
    client = get_client()
    sheet = client.open_by_key(PROD_SHEET_ID)
    ws = sheet.worksheet(PROD_TAB)
    return ws


def write_test_row():
    """
    Writes a test row to confirm sheet writing works.
    Does NOT overwrite any business columns.
    """
    ws = get_worksheet()
    ws.append_row(["TEST_WRITE_OK"], value_input_option="USER_ENTERED")
    return True


def write_updates(row_number: int, updates: dict):
    """
    Update specific columns in a row based on dictionary keys.
    Protects critical business columns.
    """

    BLOCKED_COLUMNS = [
        "SALES PERSON", "CUSTOMER NAME", "LOCATION", "RFQ NO", "RFQ DATE",
        "PRODUCT", "UID NO", "UID DATE", "DUE DATE", "VENDOR", "CONCERN PERSON"
    ]

    ws = get_worksheet()
    headers = ws.row_values(1)

    for col_name, value in updates.items():
        if col_name in BLOCKED_COLUMNS:
            continue  # skip protected fields

        if col_name in headers:
            col_index = headers.index(col_name) + 1
            ws.update_cell(row_number, col_index, value)

    return True
