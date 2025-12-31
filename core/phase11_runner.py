import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
import google.generativeai as genai # Legacy support focus

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
        print(f"--- SUCCESS: NOTIFICATION SENT ---")
    except Exception as e:
        print(f"--- SMTP ERROR: {str(e)} ---")

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "Inquiry")
        rfq = "RFQ-555"
        
        # FIX: Explicit Model Config
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        try:
            response = model.generate_content(f"Write a 1 line reply: {email_content}")
            draft = response.text.strip()
        except Exception as ai_err:
            print(f"AI Failed: {ai_err}")
            draft = "AI Draft Error - Please review manually."

        # Update Sheet (Audit)
        # ... (Sheet logic same rahegi)

        # Trigger Mail
        send_approval_notification(rfq, draft, trace_id)
        
    except Exception as e:
        print(f"--- CRITICAL RUNNER ERROR: {e} ---")

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
