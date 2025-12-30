import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
import google.generativeai as genai
from google.oauth2.service_account import Credentials

# 1. API Configuration
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds), sheet_id
    except: return None, None

def send_approval_notification(rfq, draft_content):
    sender_email = os.environ.get("OWNER_EMAIL")
    password = os.environ.get("TEMP_APP_PASSWORD")
    
    # Subject ko unique rakha hai taaki Gmail use hide na kare
    msg = MIMEText(f"Bhai, {rfq} ke liye Draft taiyar hai:\n\n{draft_content}\n\nApprove karne ke liye Sheet mein YES likho.")
    msg['Subject'] = f"🚀 ACTION REQUIRED: {rfq} Approval Request - {int(time.time())}"
    msg['From'] = sender_email
    msg['To'] = sender_email 
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
            print(f"Notification Sent Successfully")
            return True
    except Exception as e:
        print(f"Mail Error: {e}")
        return False

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        # THE ULTIMATE FIX: Using the most generic model name to avoid 404
        model = genai.GenerativeModel('gemini-pro')
        
        email_content = payload.get("payload_details", {}).get("message", "New Inquiry Received")
        rfq_match = re.search(r'RFQ-?\d+', email_content, re.IGNORECASE)
        rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-AUTO"
        
        # Simple prompt to ensure speed and stability
        res = model.generate_content(f"Write a short 2-line business reply for: {email_content}")
        draft = res.text.strip()

        client, sheet_id = get_audit_client()
        if client:
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "PENDING", "WAITING"]
            client.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
        
        send_approval_notification(rfq, draft)
    except Exception as e:
        print(f"Final Fix Attempt Error: {e}")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
