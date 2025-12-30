import threading, time, os, json, re, gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds), sheet_id
    except: return None, None

# AI Brain Setup (Phase 17)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. THE STABLE AI BRAIN (With Fallback) ---
def analyze_email_with_ai(email_text):
    # Regex Fallback: Agar AI fail ho, toh ye RFQ-555 khud nikal lega
    rfq_match = re.search(r'RFQ-?\d+', email_text, re.IGNORECASE)
    extracted_rfq = rfq_match.group(0).upper() if rfq_match else "UNKNOWN-RFQ"
    
    prompt = f"Analyze this business email and return ONLY JSON in this format: {{\"rfq_no\": \"{extracted_rfq}\", \"intent\": \"GAD_REQUEST\", \"status\": \"AI Processing\"}}. Email text: {email_text}"
    
    try:
        # Strict Response Generation
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except Exception as e:
        # Emergency Return: "ERROR-FIX" ki jagah ab sahi RFQ jayega
        return {
            "rfq_no": extracted_rfq, 
            "intent": "AUTO_RECOVERY", 
            "status": "AI Offline - Manual Review"
        }

# --- 3. AUDIT WRITERS ---
def log_to_sheet(tab_name, row_data):
    try:
        client, sheet_id = get_audit_client()
        if client: client.open_by_key(sheet_id).worksheet(tab_name).append_row(row_data)
    except: pass

# --- 4. EXECUTION ---
def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "No content")
        ai_decision = analyze_email_with_ai(email_content)
        
        # Log 1: RUN AUDIT
        log_to_sheet("LEVEL_80_RUN_AUDIT", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", ai_decision['intent'], "DONE", "1"])

        # Log 2: CELL AUDIT (No more ERROR-FIX!)
        log_to_sheet("LEVEL_80_CELL_AUDIT", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, ai_decision['rfq_no'], "UID-80-AUTO",
            "DOMESTIC_REGISTRY", "MAIN_TRACKER", "STATUS", "NEW", ai_decision['status']
        ])

        log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", f"Success: {ai_decision['rfq_no']}", "SUCCESS"])
    except Exception as e:
        log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", str(e), "ERROR"])

def run_phase11_background(trace_id: str, payload: dict):
    log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", "AI Brain Active", "STARTING"])
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
