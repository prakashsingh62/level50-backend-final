import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def classify_status(row, days_diff):
    """
    LEVEL-80 AI Status Classification Logic (Mail Meaning + Sheet Context)
    """
    # Exact headers from your sheet
    current_status = str(row.get('CURRENT STATUS', '')).strip().upper()
    remarks = str(row.get('REMARKS', '')).strip().upper()
    rfq_no = str(row.get('RFQ NO', '')).strip()

    # 1. SAFETY / AMBIGUOUS CHECK
    if not rfq_no:
        return "SKIPPED_IMMUTABLE"
    if not current_status or current_status == "NAN":
        return "AMBIGUOUS"

    # 2. RFQ LIFECYCLE (Primary)
    if any(word in current_status for word in ['CLOSED', 'FINALIZED', 'ORDER RECEIVED']):
        return "CLOSED"

    # 3. VENDOR INTERACTION (Critical Aging)
    if "INQUIRY SENT" in current_status or "VENDOR" in current_status:
        if days_diff >= 10: return "VENDOR_PENDING_OVERDUE"
        if days_diff >= 3: return "VENDOR_PENDING_3D"
        return "VENDOR_PENDING"

    # 4. CLIENT INTERACTION (Post-Quote Intelligence)
    if any(word in current_status for word in ['OFFER SENT', 'QUOTE SENT', 'VEPL OFFER']):
        # AI detects query types from Remarks or Status
        if any(word in remarks or word in current_status for word in ['DISCOUNT', 'REVISE', 'PRICE']):
            return "CLIENT_DISCOUNT_REQUEST"
        if any(word in remarks or word in current_status for word in ['GAD', 'DRAWING', 'DATASHEET', 'DOCUMENT']):
            return "CLIENT_DOCUMENT_QUERY"
        if any(word in remarks or word in current_status for word in ['DELIVERY', 'LEAD TIME', 'URGENT']):
            return "CLIENT_DELIVERY_QUERY"
        return "CLIENT_PENDING"

    # 5. REJECTION / ERROR HANDLING
    if "REJECT" in current_status or "REJECT" in remarks:
        return "CLIENT_QUERY_RECEIVED" # High priority alert

    return "IN_PROGRESS"

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    print(f"🚀 LEVEL-80 AI STARTING... [Sheet: {sheet_name}]")
    sys.stdout.flush()
    
    try:
        # Load Credentials from Render Environment
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not info_json:
            print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON missing in Render Env!")
            return

        info = json.loads(info_json)
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
        
        data = worksheet.get_all_records()
        print(f"SUCCESS: Scanning {len(data)} rows with Due Date logic.")
        sys.stdout.flush()

        today = datetime.now()
        
        # Phase-14 Buckets
        buckets = {
            "VENDOR_PENDING": [],   # Inquiry sent, no reply
            "FOLLOW_UPS": [],       # Client pending
            "CLARIFICATIONS": [],   # Queries, GAD, Rejections
            "MANUAL_REVIEW": []     # Ambiguous/Missing Status
        }

        for i, row in enumerate(data, start=2):
            # Calculate Aging based on DUE DATE
            due_date_str = row.get('DUE DATE')
            days_diff = 0
            if due_date_str:
                try:
                    # Handling string or possible numeric date formats from Sheets
                    due_date = datetime.strptime(str(due_date_str), "%d/%m/%Y")
                    days_diff = (today - due_date).days
                except: pass

            # Classify using Level-80 Rules
            status_tag = classify_status(row, days_diff)

            # Map Status to Reminder Buckets
            if "VENDOR_PENDING" in status_tag:
                buckets["VENDOR_PENDING"].append(f"Row {i} | RFQ: {row.get('RFQ NO')} | {days_diff} days")
            elif status_tag in ["CLIENT_PENDING", "CLIENT_DELIVERY_QUERY"]:
                buckets["FOLLOW_UPS"].append(f"Row {i} | Client: {row.get('CUSTOMER NAME')} | Due: {due_date_str}")
            elif "QUERY" in status_tag or "REQUEST" in status_tag:
                buckets["CLARIFICATIONS"].append(f"Row {i} | Action: {status_tag} | RFQ: {row.get('RFQ NO')}")
            elif status_tag == "AMBIGUOUS":
                buckets["MANUAL_REVIEW"].append(f"Row {i} | Missing status info")

        # Log Summary
        print(f"\n--- AUTOMATION SUMMARY ---")
        print(f"Vendor Pending: {len(buckets['VENDOR_PENDING'])}")
        print(f"Client Follow-ups: {len(buckets['FOLLOW_UPS'])}")
        print(f"Clarifications: {len(buckets['CLARIFICATIONS'])}")
        print(f"Manual Review Needed: {len(buckets['MANUAL_REVIEW'])}")
        
        # Print top items for logs
        if buckets["CLARIFICATIONS"]:
            print("\n🚨 URGENT CLARIFICATIONS:")
            for item in buckets["CLARIFICATIONS"][:5]: print(f"  {item}")

        sys.stdout.flush()

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
