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

# AI Brain Setup
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_email_with_ai(email_text):
    # REGEX Fallback (Agar AI fail ho jaye toh bhi RFQ nikaal lega)
    rfq_match = re.search(r'RFQ-?\d+', email_text, re.IGNORECASE)
    extracted_rfq = rfq_match.group(0) if rfq_match else "UNKNOWN-RFQ"
    
    prompt = f"Return ONLY JSON: {{\"rfq_no\": \"{extracted_rfq}\", \"intent\": \"INQUIRY\", \"status\": \"Review Needed\"}}. Analyze: {email_text}"
    
    try:
        response = model.generate_content(prompt)
        # Safely cleaning response text
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_text)
    except Exception as e:
        # Emergency Return (System crash nahi hoga)
        return {"rfq_no": extracted_rfq, "intent": "AUTO_READ", "status": "AI Offline/Busy"}

def log_to_sheet(tab_name, row_data):
    try:
        client, sheet_id = get_audit_client()
        if client: client.open_by_key(sheet_id).worksheet(tab_name).append_row(row_data)
    except: pass

def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "")
        ai_decision = analyze_email_with_ai(email_content)
        
        # Phase 15 & 16 Logging
        log_to_sheet("LEVEL_80_RUN_AUDIT", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", ai_decision['intent'], "DONE", "1"])
        log_to_sheet("LEVEL_80_CELL_AUDIT", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, ai_decision['rfq_no'], "UID-80-AUTO", "DOMESTIC_REGISTRY", "MAIN_TRACKER", "STATUS", "NEW", ai_decision['status']])
        log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", f"Success: {ai_decision['rfq_no']}", "SUCCESS"])
    except Exception as e:
        log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", str(e), "ERROR"])

def run_phase11_background(trace_id: str, payload: dict):
    log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", "AI Brain Active", "STARTING"])
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
