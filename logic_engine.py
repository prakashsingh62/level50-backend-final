import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    audit_id = os.environ.get("AUDIT_SHEET_ID")
    trace_id = f"L80-{datetime.now().strftime('%d%H%M%S')}"
    
    print(f"🚀 SYSTEM RELOADED | Trace: {trace_id} | SHIFTING FROM GEMINI")
    sys.stdout.flush()
    
    try:
        # Auth Setup
        info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        
        sh_prod = gc.open_by_key(spreadsheet_id)
        ws_prod = sh_prod.worksheet(sheet_name)
        
        # 🛡️ FAIL-SAFE DATA (AI bypass jab tak naya AI link na ho)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_uid = f"VEPL{datetime.now().strftime('%y%m%d%H%M%S')}"
        
        # Ye data direct sheet mein jayega - NO AI CRASH POSSIBLE
        new_row = [
            "GPT_TRANSITION", "NEW CUSTOMER", "VADODARA", "RFQ-FORCE-UPDATE", 
            timestamp, "VALVE SYSTEM", new_uid, timestamp, "", "PENDING", "SYSTEM_GPT"
        ]

        ws_prod.append_row(new_row, value_input_option='USER_ENTERED')
        print(f"✅ SUCCESS: Sheet entry created without Gemini | Trace: {trace_id}")

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
