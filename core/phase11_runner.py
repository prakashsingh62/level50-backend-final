import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
from google import genai
from google.oauth2.service_account import Credentials

def send_approval_notification(rfq, draft_content, trace_id):
    sender = os.environ.get("OWNER_EMAIL")
    password = os.environ.get("TEMP_APP_PASSWORD")
    # Base URL for the approval link
    base_url = os.environ.get("RAILWAY_STATIC_URL", "level50-backend-final-production.up.railway.app")
    approve_url = f"https://{base_url}/phase11/approve?trace_id={trace_id}"
    
    body = f"Bhai, {rfq} ka Draft ready hai.\n\nAI Draft:\n{draft_content}\n\n✅ APPROVE: {approve_url}"
    msg = MIMEText(body)
    msg['Subject'] = f"🚀 ACTION REQUIRED: {rfq} Draft Approval"
    msg['From'] = sender
    msg['To'] = sender 

    try:
        # Switching to Port 587 (STARTTLS) - Better for Railway to Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"--- SUCCESS: APPROVAL MAIL SENT TO {sender} ---")
    except Exception as e:
        print(f"--- CRITICAL MAIL ERROR: {str(e)} ---")

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "New Inquiry")
        rfq = "RFQ-555" # Example ID
        
        # 1. AI DRAFT (Confirmed Working in Sheets)
        client_ai = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = client_ai.models.generate_content(model='gemini-1.5-flash', contents=email_content)
        draft = response.text.strip()

        # 2. TRIGGER NOTIFICATION
        send_approval_notification(rfq, draft, trace_id)
        
    except Exception as e:
        print(f"--- BACKGROUND RUNNER FAILED: {e} ---")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
