import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def classify_status(row, days_diff):
    current_status = str(row.get('CURRENT STATUS', '')).strip().upper()
    remarks = str(row.get('REMARKS', '')).strip().upper()
    if any(word in current_status for word in ['CLOSED', 'FINALIZED']): return "CLOSED"
    if "INQUIRY SENT" in current_status: return "VENDOR_PENDING"
    if "OFFER SENT" in current_status: return "CLIENT_PENDING"
    return "IN_PROGRESS"

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    print(f"🚀 LEVEL-80 AI STARTING...")
    sys.stdout.flush()
    try:
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(info_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(spreadsheet_id)
        
        # Main Sheet Read
        worksheet = sh.worksheet(sheet_name)
        data = worksheet.get_all_records()
        
        # 🚨 AUDIT UPDATE ATTEMPT
        audit_tab = "LEVEL_80_AUDIT_LOG"
        try:
            audit_ws = sh.worksheet(audit_tab)
            audit_ws.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                "DAILY_SCAN", 
                len(data), 
                "SUCCESS"
            ])
            print(f"✅ Audit Log Updated in: {audit_tab}")
        except Exception as e:
            print(f"❌ AUDIT FAILED: Share your sheet with {info['client_email']}")
            print(f"Error Detail: {str(e)}")

        # Print Summary to Logs
        print(f"********** DAILY RFQ SUMMARY **********")
        print(f"Total RFQs Scanned: {len(data)}")
        print(f"****************************************")
        sys.stdout.flush()

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
