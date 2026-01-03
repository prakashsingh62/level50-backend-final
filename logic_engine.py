import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

# 🔒 RULE-0: In columns ko AI kabhi touch nahi karega
LOCKED_COLUMNS = ['SALES PERSON', 'CUSTOMER NAME', 'LOCATION', 'RFQ NO', 'RFQ DATE', 'PRODUCT', 'UID NO', 'UID DATE', 'DUE DATE', 'VENDOR', 'CONCERN PERSON']

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    audit_id = os.environ.get("AUDIT_SHEET_ID")
    trace_id = f"L80-{datetime.now().strftime('%d%H%M%S')}"
    
    print(f"🚀 LEVEL-80 SYSTEM STARTING | Trace: {trace_id}")
    sys.stdout.flush()
    
    try:
        # Auth & Setup
        info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        
        # Open Sheets
        sh_prod = gc.open_by_key(spreadsheet_id)
        ws_prod = sh_prod.worksheet(sheet_name)
        sh_audit = gc.open_by_key(audit_id)
        
        headers = ws_prod.row_values(1)
        data = ws_prod.get_all_records()

        # 🛡️ FAIL-PROOF: Run Audit Entry
        ws_run = sh_audit.worksheet("LEVEL_80_RUN_AUDIT")
        ws_run.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), trace_id, "AUTO_MODE", "RUNNING", len(data)], value_input_option='USER_ENTERED')

        cell_audits = []

        # Logic: AI identifies row via UID NO
        for i, row in enumerate(data, start=2):
            uid = str(row.get('UID NO', '')).strip()
            if not uid: continue

            # AI Logic Placeholder (Example: If Mail received, update status)
            # Yahan hum maan rahe hain ki AI ne status badla hai
            target_col = 'RFQ STATUS'
            new_val = "AI_UPDATED" 
            old_val = row.get(target_col)

            if old_val != new_val and target_col not in LOCKED_COLUMNS:
                col_idx = headers.index(target_col) + 1
                
                # Snapshot & Update
                ws_prod.update_cell(i, col_idx, new_val)
                
                # Prepare Forensic Audit
                cell_audits.append([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), trace_id, 
                    row.get('RFQ NO'), uid, target_col, str(old_val), new_val, "RULE-0_PASSED", "SUCCESS"
                ])

        # Batch Write Cell Audits (Future-Proof)
        if cell_audits:
            ws_cell = sh_audit.worksheet("LEVEL_80_CELL_AUDIT")
            ws_cell.append_rows(cell_audits, value_input_option='USER_ENTERED')

        # Final Log
        ws_log = sh_audit.worksheet("LEVEL_80_AUDIT_LOG")
        ws_log.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), trace_id, "SCAN_COMPLETE", "SUCCESS", len(cell_audits)], value_input_option='USER_ENTERED')

    except Exception as e:
        print(f"❌ SYSTEM CRASH PREVENTED: {str(e)}")
        sys.stdout.flush()
