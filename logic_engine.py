import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

# 🔒 RULE-0: In columns ko AI kabhi touch nahi karega (Sirf updates ke liye)
LOCKED_COLUMNS = ['UID NO', 'UID DATE']

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    audit_id = os.environ.get("AUDIT_SHEET_ID")
    audit_tab_name = os.environ.get("AUDIT_TAB", "LEVEL_80_CELL_AUDIT")
    trace_id = f"L80-{datetime.now().strftime('%d%H%M%S')}"
    
    print(f"🚀 LEVEL-80 SYSTEM STARTING | Trace: {trace_id}")
    sys.stdout.flush()
    
    try:
        # Auth & Setup
        service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not service_account_info:
            raise Exception("GOOGLE_SERVICE_ACCOUNT_JSON variable not found")
            
        info = json.loads(service_account_info)
        creds = Credentials.from_service_account_info(info, scopes=[
            "https://www.googleapis.com/auth/spreadsheets", 
            "https://www.googleapis.com/auth/drive"
        ])
        gc = gspread.authorize(creds)
        
        # Open Sheets
        sh_prod = gc.open_by_key(spreadsheet_id)
        ws_prod = sh_prod.worksheet(sheet_name)
        sh_audit = gc.open_by_key(audit_id)
        
        # 🛡️ FAIL-PROOF: Run Audit Entry
        try:
            ws_run = sh_audit.worksheet("LEVEL_80_RUN_AUDIT")
            ws_run.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), trace_id, "AUTO_MODE", "RUNNING"], value_input_option='USER_ENTERED')
        except:
            print("⚠️ RUN_AUDIT tab missing, skipping...")

        # --- NEW ENTRY LOGIC (FOR GMAIL DATA) ---
        # Note: Gmail se aaya hua data agar naya hai toh hum use append karenge
        # Yahan hum maan rahe hain AI ne data extract kar liya hai
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_uid = f"VEPL{datetime.now().strftime('%y%m%d%H%M%S')}"
        
        # Test Data (AI Extraction Placeholder)
        # Agar MOCK mode hai toh ye direct likhega
        new_row = [
            "AI_SALES",           # SALES PERSON
            "RAKESH KUMAR",       # CUSTOMER NAME
            "VADODARA",           # LOCATION
            "RFQ-NEW",            # RFQ NO
            timestamp,            # RFQ DATE
            "BALL VALVES",        # PRODUCT
            new_uid,              # UID NO
            timestamp,            # UID DATE
            "",                   # DUE DATE
            "PENDING",            # VENDOR
            "AI_ENGINE"           # CONCERN PERSON
        ]

        # Writing to Production
        ws_prod.append_row(new_row, value_input_option='USER_ENTERED')
        print(f"✅ Data Written to {sheet_name}")

        # Forensic Audit Entry
        ws_cell = sh_audit.worksheet(audit_tab_name)
        ws_cell.append_row([
            timestamp, trace_id, "NEW_RFQ", new_uid, "ALL", "NONE", "NEW_ENTRY", "SUCCESS"
        ], value_input_option='USER_ENTERED')

        # Final Log
        ws_log = sh_audit.worksheet("LEVEL_80_AUDIT_LOG")
        ws_log.append_row([timestamp, trace_id, "SCAN_COMPLETE", "SUCCESS", "1_ENTRY_ADDED"], value_input_option='USER_ENTERED')
        
        print(f"🏁 SYSTEM SUCCESS: Trace {trace_id}")

    except Exception as e:
        error_msg = str(e)
        print(f"❌ SYSTEM CRASH PREVENTED: {error_msg}")
        # Audit the failure
        try:
            ws_log = sh_audit.worksheet("LEVEL_80_AUDIT_LOG")
            ws_log.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), trace_id, "CRASH", error_msg], value_input_option='USER_ENTERED')
        except:
            pass
        sys.stdout.flush()
