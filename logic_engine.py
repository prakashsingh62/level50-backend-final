import os
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import sys

def classify_status(row, days_diff):
    """LEVEL-80 AI Classification Logic"""
    current_status = str(row.get('CURRENT STATUS', '')).strip().upper()
    remarks = str(row.get('REMARKS', '')).strip().upper()
    rfq_no = str(row.get('RFQ NO', '')).strip()

    if not rfq_no: return "SKIPPED_IMMUTABLE"
    if not current_status or current_status == "NAN": return "AMBIGUOUS"
    if any(word in current_status for word in ['CLOSED', 'FINALIZED', 'ORDER RECEIVED']): return "CLOSED"

    # Vendor Interaction
    if "INQUIRY SENT" in current_status or "VENDOR" in current_status:
        if days_diff >= 10: return "VENDOR_PENDING_OVERDUE"
        return "VENDOR_PENDING"

    # Client Interaction
    if any(word in current_status for word in ['OFFER SENT', 'QUOTE SENT', 'VEPL OFFER']):
        if any(word in remarks for word in ['DISCOUNT', 'REVISE', 'PRICE']): return "CLIENT_DISCOUNT_REQUEST"
        if any(word in remarks for word in ['GAD', 'DRAWING', 'DOCUMENT']): return "CLIENT_DOCUMENT_QUERY"
        return "CLIENT_PENDING"

    if "REJECT" in current_status or "REJECT" in remarks: return "CLIENT_QUERY_RECEIVED"
    
    return "IN_PROGRESS"

def generate_ai_draft(tag, row):
    """AI Drafting: Vendor gets UID | Client gets RFQ No"""
    rfq_no = str(row.get('RFQ NO', '')).strip()
    uid_no = str(row.get('UID NO', '')).strip()
    product = row.get('PRODUCT', 'Materials')
    customer = row.get('CUSTOMER NAME', 'Customer')
    
    # 1. Vendor Draft (UID Logic)
    if "VENDOR_PENDING" in tag:
        return {
            "type": "VENDOR_REMINDER",
            "subject": f"URGENT: Quotation Pending | Ref ID: {uid_no} | {product}",
            "body": f"Dear Team, \n\nRegarding our inquiry for {product} (Internal Ref: {uid_no}). We haven't received the quotation. Request you to share price/delivery urgently.\n\nRegards,\nProcurement Team"
        }
    
    # 2. Client Draft (RFQ Logic)
    elif "CLIENT_PENDING" in tag or "CLIENT_DISCOUNT" in tag:
        return {
            "type": "CLIENT_FOLLOWUP",
            "subject": f"Follow-up: Proposal for {product} | RFQ {rfq_no}",
            "body": f"Dear {customer}, \n\nFollowing up on our offer for {product} against your RFQ {rfq_no}. Let us know if any further clarification is needed.\n\nBest Regards,\nSales Team"
        }

    # 3. High Priority Rejection/Query
    elif "QUERY" in tag or "REJECT" in tag:
        return {
            "type": "URGENT_ACTION",
            "subject": f"ACTION REQUIRED: Query on RFQ {rfq_no} (UID: {uid_no})",
            "body": f"Dear Team, \n\nWe noted a technical query/rejection on {product}. Please provide a revised response immediately referring to UID {uid_no}.\n\nRegards,\nTechnical Desk"
        }
    return None

def run_level50(spreadsheet_id, sheet_name="RFQ TEST SHEET", debug=False):
    print(f"🚀 LEVEL-80 AI STARTING... [Sheet: {sheet_name}]")
    sys.stdout.flush()
    
    try:
        # Auth and Sheet Setup
        info_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        info = json.loads(info_json)
        creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(spreadsheet_id)
        worksheet = sh.worksheet(sheet_name)
        
        # Audit Log Setup
        try: audit_ws = sh.worksheet("AUDIT_LOG")
        except: audit_ws = sh.add_worksheet(title="AUDIT_LOG", rows="100", cols="5")

        data = worksheet.get_all_records()
        today = datetime.now()
        
        # Summary & Drafting Containers
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
            
            # Bucketing for Summary
            if "OVERDUE" in tag or "REJECT" in tag: summary["high"] += 1
            elif "3D" in tag or "QUERY" in tag: summary["medium"] += 1
            elif tag != "CLOSED": summary["low"] += 1

            if "VENDOR_PENDING" in tag: summary["v_no_resp"] += 1
            if "CLIENT_PENDING" in tag: summary["q_rcvd"] += 1
            if "DOCUMENT" in tag: summary["c_clarif"] += 1
            if "DISCOUNT" in tag: summary["p_queries"] += 1

            # Generate Drafts
            draft = generate_ai_draft(tag, row)
            if draft: all_drafts.append({"row": i, "data": draft})

        # 📄 PRINT SUMMARY (AS REQUESTED)
        print(f"\n********** DAILY RFQ SUMMARY **********")
        print(f"Total RFQs in Reminder: {summary['high'] + summary['medium'] + summary['low']}")
        print(f"🔴 High Priority: {summary['high']}")
        print(f"🟡 Medium Priority: {summary['medium']}")
        print(f"🟢 Low Priority: {summary['low']}")
        print(f"🚫 Vendors Not Responded: {summary['v_no_resp']}")
        print(f"✅ Quotation Received: {summary['q_rcvd']}")
        print(f"🔍 Client Clarifications: {summary['c_clarif']}")
        print(f"💬 Post-Offer Client Queries: {summary['p_queries']}")
        print(f"****************************************")

        # 📧 DRAFT PREVIEW IN LOGS
        print(f"\n📝 AI GENERATED DRAFTS ({len(all_drafts)} Pending Approval):")
        for d in all_drafts[:3]: # Preview first 3
            print(f"Row {d['row']} | {d['data']['type']} | Sub: {d['data']['subject']}")

        # 📝 AUDIT LOG UPDATE
        audit_ws.append_row([datetime.now().strftime("%d/%m %H:%M"), "DAILY_SCAN", len(data), f"H:{summary['high']} M:{summary['medium']}"])
        print("✅ Audit Log Updated.")
        sys.stdout.flush()

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.stdout.flush()
