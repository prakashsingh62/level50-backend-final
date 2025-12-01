
import json, os, gspread
from google.oauth2.service_account import Credentials
from config import MODE, TEST_SHEET_ID, TEST_TAB, PROD_SHEET_ID, PROD_TAB

IMMUTABLE = {"SALES PERSON","CUSTOMER NAME","LOCATION","RFQ NO","RFQ DATE","PRODUCT","UID NO","UID DATE","DUE DATE","VENDOR","CONCERN PERSON"}

def get_ws():
    client_secret = os.getenv("CLIENT_SECRET_JSON")
    creds_dict = json.loads(client_secret)
    scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    if MODE=="TEST":
        return client.open_by_key(TEST_SHEET_ID).worksheet(TEST_TAB)
    return client.open_by_key(PROD_SHEET_ID).worksheet(PROD_TAB)

def write_updates(rows):
    ws = get_ws()
    headers = ws.row_values(1)
    header_map = {h:i+1 for i,h in enumerate(headers)}

    for r in rows:
        row_no = r["_ROW"]
        for k,v in r.items():
            if k in ("_ROW","STATUS"): continue
            if k in header_map and k not in IMMUTABLE:
                ws.update_cell(row_no, header_map[k], v)
