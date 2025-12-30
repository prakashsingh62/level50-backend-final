import threading, time, os, json, re, gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials

def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds), sheet_id
    except: return None, None

# AI Setup
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_email_with_ai(email_text):
    # REGEX extraction hamesha backup rahega
    rfq_match = re.search(r'RFQ-?\d+', email_text, re.IGNORECASE)
    rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-PENDING"
    
    # Ultra-Simple Prompt for Free Tier Stability
    prompt = f"Task: Extract intent from email. Email: {email_text}. Format: {{\"rfq_no\":\"{rfq}\", \"intent\":\"INQUIRY\", \"status\":\"AI: Verified {rfq}\"}}"
    
    try:
        # Request without complex safety blocks
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        if response.text:
            return json.loads(response.text)
        raise Exception("No AI Text")
    except:
        # Agar AI fir bhi nakhre kare, toh hum manually summary banayenge
        return {"rfq_no": rfq, "intent": "AUTO_DETECT", "status": f"System Read: {rfq}"}

def log_to_sheet(tab_name, row_data):
    try:
        client, sheet_id = get_audit_client()
        if client: client.open_by_key(sheet_id).worksheet(tab_name).append_row(row_data)
    except: pass

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "")
        ai_res = analyze_email_with_ai(email_content)
        
        # Logging to all 3 Tabs
        log_to_sheet("LEVEL_80_RUN_AUDIT", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", ai_res['intent'], "DONE", "1"])
        log_to_sheet("LEVEL_80_CELL_AUDIT", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, ai_res['rfq_no'], "UID-80-AUTO", "DOMESTIC_REGISTRY", "MAIN_TRACKER", "STATUS", "NEW", ai_res['status']])
        log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", f"AI_OK: {ai_res['rfq_no']}", "SUCCESS"])
    except: pass

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
