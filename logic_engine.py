import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    audit_id = os.environ.get("AUDIT_SHEET_ID")
    # 🚨 FORCE MOCK: AI ko call hi mat karo agar "Short substrate" ka lafda hai
    is_mock = os.environ.get("MODE", "PRODUCTION").upper() == "MOCK"
    trace_id = f"L80-{datetime.now().strftime('%d%H%M%S')}"
    
    print(f"🚀 LEVEL-80 START | Trace: {trace_id} | MOCK: {is_mock}")
    sys.stdout.flush()
    
    try:
        # Auth Setup
        info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
        creds = Credentials.from_service_account_info(info, scopes=[
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"
        ])
        gc = gspread.authorize(creds)
        
        sh_prod = gc.open_by_key(spreadsheet_id)
        ws_prod = sh_prod.worksheet(sheet_name)
        sh_audit = gc.open_by_key(audit_id)
        
        # 🛡️ HARD-CODED DATA FOR BYPASS
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_uid = f"VEPL{datetime.now().strftime('%y%m%d%H%M%S')}"
        
        # Ye data seedha sheet mein jayega bina AI ko puche
        new_row = [
            "BYPASS_SALES", "MOCK CUSTOMER", "VADODARA", "RFQ-BYPASS", 
            timestamp, "BALL VALVES", new_uid, timestamp, "", "PENDING", "SYSTEM"
        ]

        # Writing to Sheet
        ws_prod.append_row(new_row, value_input_option='USER_ENTERED')
        print(f"✅ SUCCESS: Sheet Updated via Bypass Mode")

        # Audit Entry
        ws_cell = sh_audit.worksheet("LEVEL_80_CELL_AUDIT")
        ws_cell.append_row([timestamp, trace_id, "BYPASS", new_uid, "ALL", "NONE", "SUCCESS"], value_input_option='USER_ENTERED')

    except Exception as e:
        print(f"❌ FINAL ERROR: {str(e)}")
        sys.stdout.flush()
