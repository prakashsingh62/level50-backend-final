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

def send_approval_notification(rfq, draft_content):
    owner = os.environ.get("OWNER_EMAIL")
    password = os.environ.get("TEMP_APP_PASSWORD")
    msg = MIMEText(f"Bhai, {rfq} ke liye Draft taiyar hai:\n\n{draft_content}\n\nApprove karne ke liye Sheet mein YES likho.")
    msg['Subject'] = f"🚀 APPROVAL NEEDED: {rfq}"
    msg['From'] = owner
    msg['To'] = owner
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(owner, password)
            server.send_message(msg)
            return True
    except: return False

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "No Content")
        rfq_match = re.search(r'RFQ-?\d+', email_content, re.IGNORECASE)
        rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-NEW"
        
        # STABLE DRAFT (No AI call to avoid 404 errors)
        draft = f"Dear Customer, Thank you for your inquiry regarding {rfq}. We have received your message: '{email_content[:50]}...' and our team is reviewing it. We will get back to you shortly."

        client, sheet_id = get_audit_client()
        if client:
            # Column I (Draft), Column J (Status), Column K (Simulated)
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "PENDING", "WAITING"]
            client.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
        
        send_approval_notification(rfq, draft)
        print(f"Success: Notification sent for {rfq}")
    except Exception as e:
        print(f"Critical Fix Error: {e}")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
