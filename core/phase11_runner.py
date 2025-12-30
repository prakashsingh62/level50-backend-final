import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
import google.generativeai as genai
from google.oauth2.service_account import Credentials

# --- AUTH & SETUP ---
def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds), sheet_id
    except: return None, None

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# --- MAIL SENDER LOGIC ---
def send_approval_notification(rfq, draft_content):
    owner = os.environ.get("OWNER_EMAIL")
    password = os.environ.get("TEMP_APP_PASSWORD")
    
    msg = MIMEText(f"Bhai, {rfq} ke liye AI Draft taiyar hai:\n\n{draft_content}\n\nApprove karne ke liye Sheet mein YES likho.")
    msg['Subject'] = f"🚀 APPROVAL NEEDED: {rfq}"
    msg['From'] = owner
    msg['To'] = owner
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(owner, password)
            server.send_message(msg)
            return True
    except: return False

# --- CORE EXECUTION ---
def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "")
        
        # 1. AI Extract & Draft
        rfq_match = re.search(r'RFQ-?\d+', email_content, re.IGNORECASE)
        rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-NEW"
        
        prompt = f"Create professional reply for {rfq} from: {email_content}. Return ONLY JSON: {{\"draft\": \"...\"}}"
        res = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        draft = json.loads(res.text).get("draft", "Draft Error")

        # 2. Update Sheet
        client, sheet_id = get_audit_client()
        if client:
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "PENDING", "WAITING"]
            client.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)

        # 3. Send Mobile Notification
        send_approval_notification(rfq, draft)
        
    except Exception as e:
        print(f"Trigger Error: {e}")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
