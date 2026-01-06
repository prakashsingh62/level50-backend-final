import os, gspread, json, sys
from google.oauth2.service_account import Credentials
from datetime import datetime

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    trace_id = f"L80-{datetime.now().strftime('%d%H%M%S')}"
    # Locked Columns jo tune bataye the
    LOCKED = ['SALES PERSON', 'CUSTOMER NAME', 'LOCATION', 'RFQ NO', 'RFQ DATE', 'PRODUCT', 'UID NO', 'UID DATE', 'DUE DATE', 'VENDOR', 'CONCERN PERSON']
    
    print(f"🚀 FINAL_ATTEMPT | Trace: {trace_id}")
    sys.stdout.flush()
    
    try:
        info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        
        ws = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
        headers = ws.row_values(1)
        
        # 'RFQ STATUS' Column (L) update karenge kyunki wo LOCKED nahi hai
        if "RFQ STATUS" not in LOCKED:
            col_idx = headers.index("RFQ STATUS") + 1
            # Sabse last wali row mein status update kar do
            last_row = len(ws.get_all_values())
            ws.update_cell(last_row, col_idx, "BYPASS_DONE")
            print(f"✅ Sheet Updated: Row {last_row}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    sys.stdout.flush()
