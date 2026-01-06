import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    audit_id = os.environ.get("AUDIT_SHEET_ID")
    trace_id = f"L80-{datetime.now().strftime('%d%H%M%S')}"
    
    print(f"🚀 BYPASS MODE ACTIVE | Trace: {trace_id}")
    sys.stdout.flush()
    
    try:
        # Auth & Setup
        info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
        creds = Credentials.from_service_account_info(info, scopes=[
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"
        ])
        gc = gspread.authorize(creds)
        
        # Open Sheets
        sh_prod = gc.open_by_key(spreadsheet_id)
        ws_prod = sh_prod.worksheet(sheet_name)
        
        # 🛡️ DIRECT DATA (Bypassing AI Model)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_uid = f"VEPL{datetime.now().strftime('%y%m%d%H%M%S')}"
        
        # Ye row direct sheet mein jayegi
        new_row = [
            "BYPASS_SALES", "TEST_BYPASS", "VADODARA", "RFQ-FINAL-BYPASS", 
            timestamp, "VALVE_TEST", new_uid, timestamp, "", "PENDING", "SYSTEM"
        ]

        # Writing to Sheet
        ws_prod.append_row(new_row, value_input_option='USER_ENTERED')
        print(f"✅ SUCCESS: Sheet Updated | Trace: {trace_id}")

    except Exception as e:
        print(f"❌ FINAL ERROR: {str(e)}")
        sys.stdout.flush()
