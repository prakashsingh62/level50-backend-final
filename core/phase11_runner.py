import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
from google.oauth2.service_account import Credentials

# AI Library ko safely import kar rahe hain
try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds), sheet_id
    except Exception as e:
        print(f"--- SHEET CLIENT ERROR: {e} ---")
        return None, None

def send_approval_notification(rfq, draft_content, trace_id):
    sender = os.environ.get("OWNER_EMAIL")
    password = os.environ.get("TEMP_APP_PASSWORD")
    base_url = "level50-backend-final-production.up.railway.app"
    approve_url = f"https://{base_url}/phase11/approve?trace_id={trace_id}"
    
    body = f"Bhai, {rfq} ka Draft ready hai.\n\nAI Draft:\n{draft_content}\n\n✅ APPROVE: {approve_url}"
    msg = MIMEText(body)
    msg['Subject'] = f"🚀 ACTION REQ: {rfq} Approval"
    msg['From'] = sender
    msg['To'] = sender 

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"--- SUCCESS: MAIL SENT FOR {rfq} ---")
    except Exception as e:
        print(f"--- MAIL ERROR: {e} ---")

def _execute_full_governance(trace_id, payload):
    try:
        email_content = payload.get("payload_details", {}).get("message", "New RFQ")
        rfq = "RFQ-555"
        draft = "AWAITING AI..."

        # 1. AI Logic
        if AI_AVAILABLE:
            try:
                genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"Draft a short professional reply: {email_content}")
                draft = response.text.strip()
            except Exception as e:
                print(f"--- GEMINI API ERROR: {str(e)} ---")
                draft = "Manual Review Required (AI Error)"
        else:
            draft = "Manual Review Required (Library Missing)"
        
        # 2. Update Sheet
        client_sheet, sheet_id = get_audit_client()
        if client_sheet:
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "PENDING_REVIEW", "WAITING"]
            client_sheet.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
            print(f"--- SHEET UPDATED FOR {rfq} ---")

        # 3. Trigger Notification
        send_approval_notification(rfq, draft, trace_id)

    except Exception as e:
        print(f"--- BACKGROUND RUNNER CRASH: {e} ---")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
