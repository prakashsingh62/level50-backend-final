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
    msg = MIMEText(f"Bhai, {rfq} Draft Ready:\n\n{draft_content}")
    msg['Subject'] = f"🚀 ACTION REQUIRED: {rfq} | {int(time.time())}"
    msg['From'] = sender
    msg['To'] = sender
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(sender, password)
            s.send_message(msg)
            print("--- MAIL SENT ---")
    except: print("--- MAIL FAILED ---")

def _execute_full_governance(trace_id: str, payload: dict):
    draft = "Review required for inquiry." # Default fallback
    try:
        email_content = payload.get("payload_details", {}).get("message", "New Inquiry")
        rfq = "RFQ-555"
        
        # 🛡️ DYNAMIC AI CONNECTION (Try New SDK First, then Fallback)
        try:
            from google import genai
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            # Note: No 'models/' prefix here for the new SDK
            response = client.models.generate_content(model='gemini-1.5-flash', contents=email_content)
            draft = response.text.strip()
        except Exception as e1:
            print(f"New SDK Failed: {e1}. Trying Legacy...")
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            model = legacy_genai.GenerativeModel('gemini-pro') # gemini-pro is most stable legacy name
            response = model.generate_content(email_content)
            draft = response.text.strip()

        # Update Sheet
        client_sheet, sheet_id = get_audit_client()
        if client_sheet:
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "PENDING", "WAITING"]
            client_sheet.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
            print("--- SHEET UPDATED ---")
        
        send_approval_notification(rfq, draft)
    except Exception as e:
        print(f"SYSTEM CRASHED: {e}")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
