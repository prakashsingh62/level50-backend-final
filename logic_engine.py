import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    # Render se Audit ki ID aur Tab Name uthana
    audit_id = os.environ.get("AUDIT_SHEET_ID") 
    audit_tab = os.environ.get("AUDIT_TAB", "LEVEL_80_AUDIT_LOG")
    
    print(f"🚀 LEVEL-80 AI STARTING...")
    print(f"📂 Data Source: {spreadsheet_id}")
    print(f"📊 Audit Destination: {audit_id}")
    sys.stdout.flush()
    
    try:
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(info_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        
        # 1. READ FROM RFQ SHEET
        sh_data = gc.open_by_key(spreadsheet_id)
        worksheet = sh_data.worksheet(sheet_name)
        data = worksheet.get_all_records()
        print(f"✅ Data Read Success: {len(data)} rows.")

        # 2. WRITE TO AUDIT SHEET (Alag File)
        if audit_id:
            try:
                sh_audit = gc.open_by_key(audit_id)
                audit_ws = sh_audit.worksheet(audit_tab)
                
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Tere exact column format ke hisaab se:
                # Timestamp, TraceID/Action, Rows, Status
                audit_row = [now, "LEVEL_80_SCAN", len(data), "SUCCESS"]
                
                audit_ws.append_row(audit_row, value_input_option='USER_ENTERED')
                print(f"✅ Audit Log Updated in ASLI Sheet: {sh_audit.title} -> {audit_tab}")
            except Exception as e:
                print(f"⚠️ Audit Update Failed: {str(e)}")
        else:
            print("❌ AUDIT_SHEET_ID not found in Environment Variables!")

        sys.stdout.flush()

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
