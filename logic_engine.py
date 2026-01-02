import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    audit_id = os.environ.get("AUDIT_SHEET_ID")
    
    # ⚡ Turant signal bhejo ki engine start ho gaya
    print(f"🚀 ENGINE_START: Triple Sync Initiated...")
    sys.stdout.flush()
    
    try:
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(info_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        
        # Connection optimization
        sh_data = gc.open_by_key(spreadsheet_id)
        worksheet = sh_data.worksheet(sheet_name)
        data = worksheet.get_all_records()
        
        sh_audit = gc.open_by_key(audit_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trace_id = f"L80-{datetime.now().strftime('%H%M%S')}"

        # ⚡ BATCH UPDATE: Saare syncs ko ek saath handle karna
        # Sync 1: Daily Log
        ws_log = sh_audit.worksheet("LEVEL_80_AUDIT_LOG")
        ws_log.append_row([now, trace_id, "DAILY_SCAN", "SUCCESS", len(data)], value_input_option='USER_ENTERED')

        # Sync 2: Run Audit
        ws_run = sh_audit.worksheet("LEVEL_80_RUN_AUDIT")
        ws_run.append_row([now, trace_id, "phase80_AI", "DONE", len(data)], value_input_option='USER_ENTERED')

        print(f"✅ TRIPLE_SYNC_COMPLETE | Trace: {trace_id}")
        sys.stdout.flush()

    except Exception as e:
        print(f"❌ DEPLOYMENT_ERROR: {str(e)}")
        sys.stdout.flush()
