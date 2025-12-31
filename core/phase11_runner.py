import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
from google.oauth2.service_account import Credentials

def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds), sheet_id
    except: return None, None

def send_approval_notification(rfq, draft_content, trace_id):
    sender = os.environ.get("OWNER_EMAIL")
    password = os.environ.get("TEMP_APP_PASSWORD")
    base_url = os.environ.get("RAILWAY_STATIC_URL", "level50-backend-final-production.up.railway.app")
    approve_url = f"https://{base_url}/phase11/approve?trace_id={trace_id}"
    
    body = f"Bhai, {rfq} Approval Req.\n\nDraft:\n{draft_content}\n\n✅ APPROVE: {approve_url}"
    msg = MIMEText(body)
    msg['Subject'] = f"🚀 ACTION REQ: {rfq}"
    msg['From'] = sender
    msg['To'] = sender 

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"--- SUCCESS: MAIL SENT ---")
    except Exception as e:
        print(f"--- SMTP ERROR: {e} ---")

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        # Step 1: Data Parsing
        email_content = payload.get("payload_details", {}).get("message", "New Inquiry")
        rfq = "RFQ-555"
        draft = f"SYSTEM: Received inquiry - {email_content[:50]}..."

        # Step 2: Sheet Update (Audit)
        client_sheet, sheet_id = get_audit_client()
        if client_sheet:
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "WAITING_APPROVAL", "WAITING"]
            client_sheet.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
            print("--- SHEET UPDATED ---")

        # Step 3: Mail Notification
        send_approval_notification(rfq, draft, trace_id)
        
    except Exception as e:
        print(f"--- RUNNER CRASH: {e} ---")

def run_phase11_background(trace_id: str, payload: dict):
    # No external AI library imports here to prevent ImportError
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
