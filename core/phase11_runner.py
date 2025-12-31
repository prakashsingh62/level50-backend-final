import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
from google import genai
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
    # Railway URL variable use kar rahe hain approval link ke liye
    base_url = os.environ.get("RAILWAY_STATIC_URL", "level50-backend-final-production.up.railway.app")
    approve_url = f"https://{base_url}/phase11/approve?trace_id={trace_id}"
    
    body = f"Bhai, {rfq} ka Draft ready hai.\n\nAI Draft:\n{draft_content}\n\n✅ APPROVE: {approve_url}"
    msg = MIMEText(body)
    msg['Subject'] = f"🚀 ACTION REQ: {rfq} Approval"
    msg['From'] = sender
    msg['To'] = sender 

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
            print(f"--- MAIL SENT: {rfq} ---")
    except Exception as e:
        print(f"--- MAIL ERROR: {e} ---")

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "Inquiry")
        rfq = "RFQ-555"
        
        # 1. AI DRAFT (Latest SDK)
        client_ai = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = client_ai.models.generate_content(model='gemini-1.5-flash', contents=email_content)
        draft = response.text.strip()

        # 2. AUDIT LOG
        client_sheet, sheet_id = get_audit_client()
        if client_sheet:
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "WAITING_APPROVAL", "WAITING"]
            client_sheet.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
        
        # 3. SEND CONFIRMATION MAIL (Approval link ke saath)
        send_approval_notification(rfq, draft, trace_id)
        
    except Exception as e:
        print(f"--- RUNNER ERROR: {e} ---")

# Iska naam ekdum sahi hona chahiye taaki ImportError na aaye
def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
