
import json, os, gspread
from google.oauth2.service_account import Credentials
from config import MODE, TEST_SHEET_ID, TEST_TAB, PROD_SHEET_ID, PROD_TAB

def get_ws():
    client_secret = os.getenv("CLIENT_SECRET_JSON")
    creds_dict = json.loads(client_secret)
    scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)

    if MODE=="TEST":
        return client.open_by_key(TEST_SHEET_ID).worksheet(TEST_TAB)
    return client.open_by_key(PROD_SHEET_ID).worksheet(PROD_TAB)

def read_rows():
    ws = get_ws()
    data = ws.get_all_records()
    for i,r in enumerate(data, start=2):
        r["_ROW"] = i
    return data
