import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
import google.generativeai as genai
from google.oauth2.service_account import Credentials

# 1. API Configuration - Fixed Model ID
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

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
    
    # TIMESTAMP added to subject to force Gmail to show it as a NEW notification
    timestamp = time.strftime("%H:%M:%S")
    subject = f"🚨 APPROVAL REQ: {rfq} | Time: {timestamp}"
    
    body = f"Bhai, {rfq} ka draft ready hai.\n\nAI DRAFT:\n{draft_content}\n\nSheet mein YES likho approval ke liye."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = f"Level-80 AI <{sender}>"
    msg['To'] = sender
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
            print(f"--- MAIL SENT SUCCESSFULLY TO {sender} ---")
            return True
    except Exception as e:
        print(f"--- MAIL FAILED: {e} ---")
        return False

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        # THE FIX: Using the exact stable name without 'models/' prefix
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        email_content = payload.get("payload_details", {}).get("message", "No content")
        rfq_match = re.search(r'RFQ-?\d+', email_content, re.IGNORECASE)
        rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-AUTO"
        
        # AI Logic
        res = model.generate_content(f"Generate a professional 2-sentence reply for: {email_content}")
        draft = res.text.strip()

        client, sheet_id = get_audit_client()
        if client:
            # Writing to Column I (Draft), Column J (Approval), Column K (Status)
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "PENDING", "WAITING"]
            client.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
            print(f"--- SHEET UPDATED FOR {rfq} ---")
        
        send_approval_notification(rfq, draft)
    except Exception as e:
        print(f"--- SYSTEM ERROR: {e} ---")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
