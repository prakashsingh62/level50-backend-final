import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    audit_id = os.environ.get("AUDIT_SHEET_ID")
    
    print(f"🚀 LEVEL-80 FORCED TRIPLE SYNC...")
    sys.stdout.flush()
    
    try:
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(info_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        
        # 1. READ SOURCE
        sh_data = gc.open_by_key(spreadsheet_id)
        worksheet = sh_data.worksheet(sheet_name)
        data = worksheet.get_all_records()
        
        # 2. CONNECT AUDIT
        sh_audit = gc.open_by_key(audit_id)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trace_id = f"L80-{datetime.now().strftime('%d%H%M')}"

        # --- SYNC 1: LOG ---
        ws_log = sh_audit.worksheet("LEVEL_80_AUDIT_LOG")
        ws_log.append_row([now, trace_id, "DAILY_SCAN", "SUCCESS", len(data)], value_input_option='USER_ENTERED')
        print("✅ Sync 1: Log Updated")

        # --- SYNC 2: RUN ---
        ws_run = sh_audit.worksheet("LEVEL_80_RUN_AUDIT")
        ws_run.append_row([now, trace_id, "phase80_AI", "DONE", len(data)], value_input_option='USER_ENTERED')
        print("✅ Sync 2: Run Updated")

        # --- SYNC 3: CELL ---
        # 🚨 FIX: Forced loop for cell audit
        ws_cell = sh_audit.worksheet("LEVEL_80_CELL_AUDIT")
        cell_updates = []
        for i, row in enumerate(data[:5], start=2): # Sirf top 5 rows testing ke liye
            cell_updates.append([
                now, trace_id, str(row.get('RFQ NO', 'N/A')), str(row.get('UID NO', 'N/A')),
                "RFQ TEST SHEET", "MAIN_TRACKER", i, "STATUS_CHECK", "SAMPLED"
            ])
        
        if cell_updates:
            ws_cell.append_rows(cell_updates, value_input_option='USER_ENTERED')
            print(f"✅ Sync 3: Cell Audit Updated with {len(cell_updates)} rows.")

        sys.stdout.flush()

    except Exception as e:
        print(f"❌ SYNC ERROR: {str(e)}")
        sys.stdout.flush()
