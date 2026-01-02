import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    # Render Environment Variables
    audit_id = os.environ.get("AUDIT_SHEET_ID")
    
    print(f"🚀 LEVEL-80 TRIPLE SYNC STARTING...")
    sys.stdout.flush()
    
    try:
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(info_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        
        # 1. READ SOURCE DATA
        sh_data = gc.open_by_key(spreadsheet_id)
        worksheet = sh_data.worksheet(sheet_name)
        data = worksheet.get_all_records()
        
        # 2. CONNECT TO AUDIT FILE
        sh_audit = gc.open_by_key(audit_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trace_id = f"L80-{datetime.now().strftime('%H%M%S')}"

        # --- TAB 1: LEVEL_80_AUDIT_LOG (Daily Summary) ---
        ws_log = sh_audit.worksheet("LEVEL_80_AUDIT_LOG")
        ws_log.append_row([now, trace_id, "PHASE-80", "DAILY_SCAN_COMPLETE", "SUCCESS", len(data)], value_input_option='USER_ENTERED')
        print("✅ Sync 1/3: AUDIT_LOG Updated.")

        # --- TAB 2: LEVEL_80_RUN_AUDIT (Execution Trace) ---
        ws_run = sh_audit.worksheet("LEVEL_80_RUN_AUDIT")
        ws_run.append_row([now, trace_id, "phase80_AI", "AUTO_DETECT", "DONE", len(data), len(data), "No Errors", "{} "], value_input_option='USER_ENTERED')
        print("✅ Sync 2/3: RUN_AUDIT Updated.")

        # --- TAB 3: LEVEL_80_CELL_AUDIT (Specific Actions) ---
        # Yahan hum sirf un RFQs ko daalte hain jinpar action hona hai
        ws_cell = sh_audit.worksheet("LEVEL_80_CELL_AUDIT")
        action_count = 0
        for i, row in enumerate(data, start=2):
            # Example condition: Agar status missing hai ya koi draft ban raha hai
            if not row.get('CURRENT STATUS') or action_count < 5: # Limit for testing
                ws_cell.append_row([
                    now, trace_id, row.get('RFQ NO', 'N/A'), row.get('UID NO', 'N/A'), 
                    "RFQ TEST SHEET", "MAIN_TRACKER", i, "STATUS", "NEW"
                ], value_input_option='USER_ENTERED')
                action_count += 1
        print(f"✅ Sync 3/3: CELL_AUDIT Updated with {action_count} rows.")

        sys.stdout.flush()

    except Exception as e:
        print(f"❌ TRIPLE SYNC ERROR: {str(e)}")
        sys.stdout.flush()
