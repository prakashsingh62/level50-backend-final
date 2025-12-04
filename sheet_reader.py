import os
import gspread
from google.oauth2.service_account import Credentials
import json

from config import CLIENT_SECRET_JSON, PROD_SHEET_ID, PROD_TAB

def read_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        json.loads(CLIENT_SECRET_JSON),
        scopes=scopes
    )
    client = gspread.authorize(creds)

    sheet = client.open_by_key(PROD_SHEET_ID)
    worksheet = sheet.worksheet(PROD_TAB)

    rows = worksheet.get_all_values()

    if not rows or len(rows) < 2:
        return []

    headers = rows[0]
    data_rows = rows[1:]

    final_data = []
    for r in data_rows:
        row_dict = {}
        for i, h in enumerate(headers):
            value = r[i] if i < len(r) else ""
            row_dict[h.strip()] = value
        final_data.append(row_dict)

    return final_data
