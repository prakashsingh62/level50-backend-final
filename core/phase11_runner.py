import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
from google import genai # Latest SDK
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
    
    msg = MIMEText(f"Bhai, {rfq} ke liye AI Draft ready hai:\n\n{draft_content}\n\nSheet check karo.")
    msg['Subject'] = f"🚀 ACTION REQUIRED: {rfq}"
    msg['From'] = sender
    msg['To'] = sender 

    try:
        # Using Port 465 (SSL) as it's often more reliable for Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
            print(f"--- SUCCESS: MAIL SENT FOR {rfq} ---")
            return True
    except Exception as e:
        print(f"--- MAIL ERROR: {e} ---")
        return False

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "New Inquiry")
        rfq_match = re.search(r'RFQ-?\d+', email_content, re.IGNORECASE)
        rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-AUTO"
        
        # 1. GENERATE AI DRAFT (Now Working!)
        client_ai = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = client_ai.models.generate_content(
            model='gemini-1.5-flash', 
            contents=f"Write a professional 2-sentence reply for: {email_content}"
        )
        draft = response.text.strip()

        # 2. UPDATE SHEET (Verified Working!)
        client_sheet, sheet_id = get_audit_client()
        if client_sheet:
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "PENDING", "WAITING"]
            client_sheet.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
            print(f"--- SUCCESS: SHEET UPDATED FOR {rfq} ---")
        
        # 3. SEND EMAIL
        send_approval_notification(rfq, draft)
        
    except Exception as e:
        print(f"--- CRITICAL SYSTEM ERROR: {e} ---")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
