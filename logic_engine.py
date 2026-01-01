import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def classify_status(row, days_diff):
    """
    LEVEL-80 AI Status Classification Logic
    """
    current_status = str(row.get('CURRENT STATUS', '')).upper()
    
    # 1. RFQ LIFECYCLE CHECK
    if not row.get('RFQ NO'): return "NEW_RFQ"
    if "CLOSED" in current_status or "ORDER" in current_status: return "CLOSED"

    # 2. VENDOR INTERACTION LAYER
    if "INQUIRY SENT" in current_status:
        if days_diff >= 10: return "VENDOR_PENDING_OVERDUE"
        if days_diff >= 3: return "VENDOR_PENDING_3D"
        return "VENDOR_PENDING"

    # 3. CLIENT INTERACTION LAYER (Post-Quote Intelligence)
    if "OFFER SENT" in current_status or "QUOTE SENT" in current_status:
        # Detect Client Queries (Keywords based on your Level-80 rules)
        remarks = str(row.get('REMARKS', '')).lower()
        if any(word in remarks for word in ['discount', 'revise', 'better price']):
            return "CLIENT_DISCOUNT_REQUEST"
        if any(word in remarks for word in ['drawing', 'gad', 'datasheet']):
            return "CLIENT_DOCUMENT_QUERY"
        return "CLIENT_PENDING"

    # 4. SAFETY / AMBIGUOUS
    if not current_status: return "AMBIGUOUS"
    
    return "IN_PROGRESS"

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    print(f"🚀 LEVEL-80 AI STARTING...")
    sys.stdout.flush()
    
    try:
        # Auth and Sheet Connection (using your Env Var)
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(info_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
        
        data = worksheet.get_all_records()
        print(f"SUCCESS: Scanning {len(data)} rows with Level-80 Context.")
        sys.stdout.flush()

        today = datetime.now()
        buckets = {
            "VENDOR_PENDING": [],
            "CLIENT_FOLLOWUPS": [],
            "CLARIFICATIONS": [],
            "MANUAL_REVIEW": []
        }

        for i, row in enumerate(data, start=2):
            due_date_str = row.get('DUE DATE')
            days_diff = 0
            
            if due_date_str:
                try:
                    due_date = datetime.strptime(str(due_date_str), "%d/%m/%Y")
                    days_diff = (today - due_date).days
                except: pass

            # GET AI CLASSIFICATION
            ai_status = classify_status(row, days_diff)

            # MAP TO REMINDER BUCKETS (Phase-14)
            if "VENDOR_PENDING" in ai_status:
                buckets["VENDOR_PENDING"].append(f"Row {i}: {row.get('RFQ NO')} ({days_diff} days)")
            elif "CLIENT_PENDING" in ai_status:
                buckets["CLIENT_FOLLOWUPS"].append(f"Row {i}: Follow-up for {row.get('CUSTOMER NAME')}")
            elif "QUERY" in ai_status or "REJECT" in ai_status:
                buckets["CLARIFICATIONS"].append(f"Row {i}: Action on {ai_status}")
            elif ai_status == "AMBIGUOUS":
                buckets["MANUAL_REVIEW"].append(f"Row {i}: Missing status")

        # Output Results
        for bucket, items in buckets.items():
            if items:
                print(f"--- {bucket} ({len(items)}) ---")
                for item in items[:5]: print(f"  > {item}")

        sys.stdout.flush()

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
