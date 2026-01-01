import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def classify_status(row, days_diff):
    current_status = str(row.get('CURRENT STATUS', '')).strip().upper()
    remarks = str(row.get('REMARKS', '')).strip().upper()
    rfq_no = str(row.get('RFQ NO', '')).strip()

    if not rfq_no: return "SKIPPED_IMMUTABLE"
    if not current_status or current_status == "NAN": return "AMBIGUOUS"
    if any(word in current_status for word in ['CLOSED', 'FINALIZED', 'ORDER RECEIVED']): return "CLOSED"

    if "INQUIRY SENT" in current_status or "VENDOR" in current_status:
        if days_diff >= 10: return "VENDOR_PENDING_OVERDUE"
        return "VENDOR_PENDING"

    if any(word in current_status for word in ['OFFER SENT', 'QUOTE SENT', 'VEPL OFFER']):
        if any(word in remarks for word in ['DISCOUNT', 'REVISE', 'PRICE']): return "CLIENT_DISCOUNT_REQUEST"
        if any(word in remarks for word in ['GAD', 'DRAWING', 'DOCUMENT']): return "CLIENT_DOCUMENT_QUERY"
        return "CLIENT_PENDING"

    if "REJECT" in current_status or "REJECT" in remarks: return "CLIENT_QUERY_RECEIVED"
    return "IN_PROGRESS"

def generate_ai_draft(tag, row):
    rfq_no = str(row.get('RFQ NO', '')).strip()
    uid_no = str(row.get('UID NO', '')).strip()
    product = row.get('PRODUCT', 'Materials')
    customer = row.get('CUSTOMER NAME', 'Customer')
    
    if "VENDOR_PENDING" in tag:
        return {
            "type": "VENDOR_REMINDER",
            "subject": f"URGENT: Quotation Pending | Ref ID: {uid_no} | {product}",
            "body": f"Dear Team, \n\nRegarding inquiry for {product} (Internal Ref: {uid_no}). Quote pending. Share price urgently.\n\nRegards,\nProcurement"
        }
    elif "CLIENT_PENDING" in tag:
        return {
            "type": "CLIENT_FOLLOWUP",
            "subject": f"Follow-up: Proposal for {product} | RFQ {rfq_no}",
            "body": f"Dear {customer}, \n\nFollowing up on offer for {product} against RFQ {rfq_no}. Please provide update.\n\nRegards,\nSales Team"
        }
    return None

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    print(f"🚀 LEVEL-80 AI STARTING... [Sheet: {sheet_name}]")
    sys.stdout.flush()
    
    try:
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(info_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
        
        # 🚨 FIX: Using your exact Audit Tab name from screenshot
        audit_tab_name = "LEVEL_80_AUDIT_LOG"
        try:
            audit_ws = sh.worksheet(audit_tab_name)
        except:
            audit_ws = sh.add_worksheet(title=audit_tab_name, rows="1000", cols="5")

        data = worksheet.get_all_records()
        today = datetime.now()
        summary = {"high": 0, "medium": 0, "low": 0, "v_no_resp": 0, "q_rcvd": 0, "c_clarif": 0, "p_queries": 0}
        all_drafts = []

        for i, row in enumerate(data, start=2):
            due_date_str = row.get('DUE DATE')
            days_diff = 0
            if due_date_str:
                try:
                    due_date = datetime.strptime(str(due_date_str), "%d/%m/%Y")
                    days_diff = (today - due_date).days
                except: pass

            tag = classify_status(row, days_diff)
            if "OVERDUE" in tag or "REJECT" in tag: summary["high"] += 1
            elif "3D" in tag: summary["medium"] += 1
            elif tag != "CLOSED": summary["low"] += 1

            if "VENDOR_PENDING" in tag: summary["v_no_resp"] += 1
            
            draft = generate_ai_draft(tag, row)
            if draft: all_drafts.append({"row": i, "data": draft})

        # 📄 PRINT SUMMARY
        print(f"\n********** DAILY RFQ SUMMARY **********")
        print(f"Total RFQs in Reminder: {summary['high'] + summary['medium'] + summary['low']}")
        print(f"🔴 High Priority: {summary['high']} | 🟡 Medium: {summary['medium']} | 🟢 Low: {summary['low']}")
        print(f"🚫 Vendors Not Responded: {summary['v_no_resp']}")
        print(f"****************************************")

        # 📧 DRAFT PREVIEW
        if all_drafts:
            print(f"📝 AI DRAFTS READY: {len(all_drafts)}")
            print(f"SAMPLE DRAFT: {all_drafts[0]['data']['subject']}")

        # 📝 AUDIT LOG UPDATE - Exact Tab
        audit_ws.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
            "DAILY_SCAN", 
            len(data), 
            f"High:{summary['high']} Drafts:{len(all_drafts)}"
        ])
        print(f"✅ Audit Log Updated in tab: {audit_tab_name}")
        sys.stdout.flush()

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
