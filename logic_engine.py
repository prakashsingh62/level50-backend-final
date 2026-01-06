import os
import gspread
import json
import sys
from google.oauth2.service_account import Credentials
from datetime import datetime

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    # 1. Trace ID & Initial Log
    trace_id = f"L80-{datetime.now().strftime('%d%H%M%S')}"
    print(f"🚀 BYPASSING ALL AI | Trace: {trace_id}")
    sys.stdout.flush()
    
    try:
        # 2. Auth Setup
        service_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not service_json:
            raise Exception("Service Account JSON environment variable is missing!")
            
        info = json.loads(service_json)
        creds = Credentials.from_service_account_info(
            info, 
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        
        # 3. Open Worksheet
        sh_prod = gc.open_by_key(spreadsheet_id)
        ws_prod = sh_prod.worksheet(sheet_name)
        
        # 4. Prepare Direct Entry (No AI needed)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Structure: SALES, CUSTOMER, LOCATION, RFQ NO, DATE, PRODUCT, UID, UID DATE, DUE, VENDOR, CONCERN
        new_row = [
            "FORCE_ENTRY", 
            "TEST_CLIENT", 
            "VADODARA", 
            f"RFQ-{datetime.now().strftime('%M%S')}", 
            ts, 
            "VALVE_UNIT", 
            f"VEPL{datetime.now().strftime('%y%m%d%H%M%S')}", 
            ts, 
            "", 
            "PENDING", 
            "SYSTEM_BYPASS"
        ]
        
        # 5. Write to Sheet
        ws_prod.append_row(new_row, value_input_option='USER_ENTERED')
        print(f"✅ Sheet Updated Successfully! Row Added with UID: {new_row[6]}")
        sys.stdout.flush()
        
    except Exception as e:
        print(f"❌ Error in Logic Engine: {str(e)}")
        sys.stdout.flush()
