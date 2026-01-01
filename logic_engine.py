import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def classify_status(row, days_diff):
    """Level-80 AI Classification Logic"""
    current_status = str(row.get('CURRENT STATUS', '')).strip().upper()
    remarks = str(row.get('REMARKS', '')).strip().upper()
    
    if any(word in current_status for word in ['CLOSED', 'FINALIZED']): return "CLOSED"
    if "INQUIRY SENT" in current_status or "VENDOR" in current_status: return "VENDOR_PENDING"
    if "OFFER SENT" in current_status or "QUOTE" in current_status: return "CLIENT_PENDING"
    if "REJECT" in current_status or "REJECT" in remarks: return "CLIENT_QUERY_RECEIVED"
    
    return "IN_PROGRESS"

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    print(f"🚀 LEVEL-80 AI STARTING... [Sheet ID: {spreadsheet_id}]")
    sys.stdout.flush()
    
    try:
        # Auth Setup
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(info_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        
        # Open the specific Spreadsheet
        sh = gc.open_by_key(spreadsheet_id)
        
        # 1. READ DATA
        worksheet = sh.worksheet(sheet_name)
        data = worksheet.get_all_records()
        print(f"✅ Data Read Success: {len(data)} rows.")

        # 2. AUDIT LOG UPDATE (Using your exact tab name)
        audit_tab_name = "LEVEL_80_AUDIT_LOG"
        try:
            # Pura path check karo ki tab mil raha hai ya nahi
            audit_ws = sh.worksheet(audit_tab_name)
            
            # Timestamp formatted correctly for your sheet
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Mapping data according to your Audit Sheet columns
            # Column A: Timestamp, B: Action, C: Rows, D: Status
            audit_row = [now, "LEVEL_80_SCAN", len(data), "SUCCESS"]
            audit_ws.append_row(audit_row)
            
            print(f"✅ Audit Sheet Updated Successfully in {audit_tab_name}")
        except Exception as audit_err:
            print(f"⚠️ Audit Tab Update Failed: {str(audit_err)}")

        # 3. GENERATE SUMMARY FOR LOGS
        v_pending = 0
        for row in data:
            tag = classify_status(row, 0)
            if tag == "VENDOR_PENDING": v_pending += 1

        print(f"--- DAILY RFQ SUMMARY ---")
        print(f"Total RFQs: {len(data)}")
        print(f"Vendors Pending: {v_pending}")
        print(f"--------------------------")
        sys.stdout.flush()

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
