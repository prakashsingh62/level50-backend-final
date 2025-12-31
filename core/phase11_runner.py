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
    sender = os.environ.get("OWNER_EMAIL")
    password = os.environ.get("TEMP_APP_PASSWORD")
    
    # Validation
    if not sender or not password:
        print("--- MAIL ERROR: Credentials missing in Railway Variables ---")
        return False

    msg = MIMEText(f"Bhai, {rfq} Draft Ready:\n\n{draft_content}\n\nSheet check karo.")
    msg['Subject'] = f"🚀 SYSTEM ALERT: {rfq} | {int(time.time())}"
    msg['From'] = f"Level-80 System <{sender}>"
    msg['To'] = sender # Sending to yourself
    
    try:
        # Standard Gmail SMTP (Port 587 with STARTTLS is more stable than 465)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"--- SUCCESS: MAIL SENT TO {sender} ---")
        return True
    except Exception as e:
        print(f"--- SMTP ERROR: {str(e)} ---")
        return False

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "New Inquiry")
        rfq_match = re.search(r'RFQ-?\d+', email_content, re.IGNORECASE)
        rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-AUTO"
        
        # Row data preparation
        draft = f"SYSTEM DRAFT: Inquiry received for {rfq}. Manual review pending."

        # 1. Update Sheet (Jo ab chal raha hai)
        client_sheet, sheet_id = get_audit_client()
        if client_sheet:
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "PENDING", "WAITING"]
            client_sheet.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
            print(f"--- SHEET UPDATED: {rfq} ---")
        
        # 2. Trigger Mail (Iska error check karna hai)
        send_approval_notification(rfq, draft)
        
    except Exception as e:
        print(f"--- RUNNER CRASH: {e} ---")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
