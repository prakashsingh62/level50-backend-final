import threading
import time
import os
import json
import smtplib
import ssl
from email.mime.text import MIMEText
import gspread
from google.oauth2.service_account import Credentials

# AI Library safely handled
try:
    import google.generativeai as genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        if not creds_json or not sheet_id:
            return None, None
        creds = Credentials.from_service_account_info(
            json.loads(creds_json), 
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        return gspread.authorize(creds), sheet_id
    except Exception as e:
        print(f"--- SHEET ERROR: {e} ---")
        return None, None

def send_approval_notification(rfq, draft_content, trace_id):
    sender = os.environ.get("OWNER_EMAIL")
    password = os.environ.get("TEMP_APP_PASSWORD")
    # Base URL for approval link
    base_url = "level50-backend-final-production.up.railway.app"
    approve_url = f"https://{base_url}/phase11/approve?trace_id={trace_id}"
    
    body = f"Bhai, {rfq} ka AI Draft ready hai.\n\nDraft Content:\n{draft_content}\n\n✅ APPROVE KARNE KE LIYE CLICK KAREIN:\n{approve_url}"
    
    msg = MIMEText(body)
    msg['Subject'] = f"🚀 ACTION REQ: {rfq} Draft Approval"
    msg['From'] = sender
    msg['To'] = sender 

    try:
        # Standard SSL Port 465 for Gmail
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(sender, password)
            server.send_message(msg)
        print(f"--- SUCCESS: MAIL SENT FOR {rfq} ---")
        return True
    except Exception as e:
        print(f"--- MAIL FAILED: {str(e)} ---")
        return False

def _execute_full_governance(trace_id, payload):
    try:
        # Step 1: Data extraction
        email_content = payload.get("payload_details", {}).get("message", "New RFQ")
        rfq = "RFQ-555" # Example placeholder
        draft = "AI Error"

        # Step 2: Gemini AI (Updated to gemini-pro to avoid 404)
        if AI_AVAILABLE:
            try:
                genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
                # Using gemini-pro as it's more stable on older API keys
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(f"Write a 2-sentence professional reply to: {email_content}")
                draft = response.text.strip()
            except Exception as e:
                print(f"--- GEMINI ERROR: {str(e)} ---")
                draft = f"Manual Review Required (AI Error: {str(e)[:50]})"
        
        # Step 3: Sheet Update (Confirmed working)
        client_sheet, sheet_id = get_audit_client()
        if client_sheet:
            row = [
                time.strftime("%Y-%m-%d %H:%M:%S"), 
                trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", 
                "STATUS", "NEW", draft, "PENDING_APPROVAL", "WAITING"
            ]
            client_sheet.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
            print(f"--- SHEET UPDATED FOR {rfq} ---")

        # Step 4: Notification (Final Step)
        send_approval_notification(rfq, draft, trace_id)

    except Exception as e:
        print(f"--- RUNNER CRASHED: {e} ---")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
