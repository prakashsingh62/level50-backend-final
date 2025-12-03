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


# ------------------------------------------------------
# OLD FUNCTION (kept for backward compatibility)
# ------------------------------------------------------
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

        if col_name in BLOCKED_COLUMNS:
            continue

        if col_name in headers:
            col_index = headers.index(col_name) + 1
            ws.update_cell(row, col_index, value)

    return True


# ------------------------------------------------------
# WRITE OPTIMIZATION V2 — NEW HIGH-SPEED BATCH WRITER
# ------------------------------------------------------
def write_batch_updates(aging_updates: dict, vendor_updates: dict):
    """
    aging_updates = { row: value }
    vendor_updates = { row: value }

    Sends ALL updates in ONE batchUpdate (quota-safe).
    """

    ws = get_worksheet()
    sheet_id = ws.id  # Required for batchUpdate
    headers = ws.row_values(1)

    # Find column indexes
    try:
        aging_col_index = headers.index("Aging") + 1
    except ValueError:
        aging_col_index = None

    try:
        vendor_col_index = headers.index("Vendor Follow-up Aging") + 1
    except ValueError:
        vendor_col_index = None

    # Build request payload
    requests = []

    # ---- Aging updates ----
    if aging_col_index:
        for row, value in aging_updates.items():
            requests.append({
                "updateCells": {
                    "rows": [{
                        "values": [{
                            "userEnteredValue": {"stringValue": str(value)}
                        }]
                    }],
                    "fields": "userEnteredValue",
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row - 1,
                        "endRowIndex": row,
                        "startColumnIndex": aging_col_index - 1,
                        "endColumnIndex": aging_col_index
                    }
                }
            })

    # ---- Vendor Follow-up Aging updates ----
    if vendor_col_index:
        for row, value in vendor_updates.items():
            requests.append({
                "updateCells": {
                    "rows": [{
                        "values": [{
                            "userEnteredValue": {"stringValue": str(value)}
                        }]
                    }],
                    "fields": "userEnteredValue",
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": row - 1,
                        "endRowIndex": row,
                        "startColumnIndex": vendor_col_index - 1,
                        "endColumnIndex": vendor_col_index
                    }
                }
            })

    # If nothing to update
    if not requests:
        return True

    # Execute 1 SINGLE batch update
    client = get_client()
    body = {"requests": requests}

    client.request(
        method="post",
        path=f"/v4/spreadsheets/{PROD_SHEET_ID}:batchUpdate",
        json=body
    )

    return True


def write_test_row():
    ws = get_worksheet()
    ws.append_row(["TEST_WRITE_OK"], value_input_option="USER_ENTERED")
    return True
