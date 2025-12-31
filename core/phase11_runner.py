import threading, time, os, json, re, gspread, smtplib
from email.mime.text import MIMEText
from google import genai
from google.oauth2.service_account import Credentials

# --- EMAIL TRIGGER WITH APPROVAL LINK ---
def send_approval_notification(rfq, draft_content, trace_id):
    sender = os.environ.get("OWNER_EMAIL")
    password = os.environ.get("TEMP_APP_PASSWORD")
    # Ye link hamare backend ko hit karega jo email send karega
    approve_url = f"https://{os.environ.get('RAILWAY_STATIC_URL')}/phase11/approve?trace_id={trace_id}"
    
    body = f"""
Bhai, naya RFQ aaya hai: {rfq}

AI DRAFT:
"{draft_content}"

Upar wala draft sahi hai?
✅ APPROVE KARNE KE LIYE YAHAN CLICK KARO: {approve_url}

(Click karte hi ye draft customer ko chala jayega)
"""
    msg = MIMEText(body)
    msg['Subject'] = f"🚀 ACTION REQ: Approve Draft for {rfq}"
    msg['From'] = sender
    msg['To'] = sender 

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
            print(f"--- NOTIFICATION SENT TO {sender} ---")
    except Exception as e:
        print(f"--- MAIL ERROR: {e} ---")

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "Inquiry")
        rfq = "RFQ-555" # Dynamic nikal sakte hain logic se
        
        # 1. AI DRAFT (Latest SDK)
        client_ai = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        response = client_ai.models.generate_content(model='gemini-1.5-flash', contents=email_content)
        draft = response.text.strip()

        # 2. AUDIT LOG (Backup ke liye)
        client_sheet, sheet_id = get_audit_client()
        if client_sheet:
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80", "DOMESTIC", "MAIN", "STATUS", "NEW", draft, "AWAITING_MOBILE_APPROVAL", "WAITING"]
            client_sheet.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row)
        
        # 3. SEND CONFIRMATION MAIL TO YOU
        send_approval_notification(rfq, draft, trace_id)
        
    except Exception as e:
        print(f"--- ERROR: {e} ---")
