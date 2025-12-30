import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
import google.generativeai as genai
from google.oauth2.service_account import Credentials

# 1. API Configuration (Gemini Stable Setup)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds), sheet_id
    except: return None, None

def send_approval_notification(rfq, draft_content):
    # Sender (Wo email jiska App Password hai)
    sender_email = os.environ.get("OWNER_EMAIL") 
    
    # RECIPIENT: Hum 'OWNER_EMAIL' par hi bhejenge par different logic se 
    # taaki Gmail use block na kare (Subject badal kar)
    receiver_email = sender_email 
    
    password = os.environ.get("TEMP_APP_PASSWORD")
    
    msg = MIMEText(f"Bhai, {rfq} ke liye AI Draft taiyar hai:\n\n{draft_content}\n\nApprove karne ke liye Sheet mein YES likho.")
    msg['Subject'] = f"ACTION REQUIRED: Approval for {rfq} - {int(time.time())}" # Added timestamp for uniqueness
    msg['From'] = f"Level-80 System <{sender_email}>"
    msg['To'] = receiver_email
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)
            print(f"Mail successfully sent to {receiver_email}")
            return True
    except Exception as e:
        print(f"Mail Error: {e}")
        return False

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        # Stable Model Call
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        email_content = payload.get("payload_details", {}).get("message", "No content found")
        rfq_match = re.search(r'RFQ-?\d+', email_content, re.IGNORECASE)
        rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-NEW"
        
        # AI Draft Generation
        prompt = f"Create a professional business reply for {rfq} based on this content: {email_content}. Be concise."
        res = model.generate_content(prompt)
        draft = res.text.strip()

        client, sheet_id = get_audit_client()
        if client:
            # Writing to LEVEL_80_CELL_AUDIT (Column J is Approval, Column K is Mail Status)
            row = [
                time.strftime("%Y-%m-%d %H:%M:%S"), 
                trace_id, 
                rfq, 
                "UID-80", 
                "DOMESTIC", 
                "MAIN", 
                "STATUS", 
                "NEW", 
                draft, 
                "PENDING", 
                "WAITING"
            ]
            client.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
            print(f"Row added to Sheet for {rfq}")
        
        # Trigger Email
        send_approval_notification(rfq, draft)
        
    except Exception as e:
        print(f"Full Governance Error: {e}")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
