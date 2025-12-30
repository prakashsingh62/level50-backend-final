import threading, time, os, json, re, gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials

# --- 1. SETUP & AUTH ---
def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds), sheet_id
    except: return None, None

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. AI DRAFTING ENGINE (Phase 19) ---
def generate_draft_with_ai(email_text, rfq_no):
    prompt = f"""
    Create a professional short reply for RFQ: {rfq_no}.
    Context: {email_text}
    Return ONLY JSON: {{"draft": "Dear Customer, Thank you for {rfq_no}. We are reviewing it.", "intent": "ACKNOWLEDGE"}}
    """
    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        return json.loads(response.text)
    except:
        return {"draft": f"Dear Customer, we have received your request for {rfq_no}. Our team is working on it.", "intent": "AUTO_ACK"}

# --- 3. EXECUTION LOGIC ---
def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "")
        
        # RFQ Extraction (Bulletproof Logic)
        rfq_match = re.search(r'RFQ-?\d+', email_content, re.IGNORECASE)
        rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-PENDING"
        
        # AI Draft Creation
        ai_data = generate_draft_with_ai(email_content, rfq)
        
        # Log to CELL_AUDIT with Approval Column
        # Columns: Timestamp, TraceID, RFQ, UID, Registry, Tracker, StatusName, OldVal, NewVal, APPROVAL, MAIL_STATUS
        row_data = [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq, "UID-80-AUTO",
            "DOMESTIC_REGISTRY", "MAIN_TRACKER", "STATUS", "NEW", 
            ai_data['draft'], "PENDING", "WAITING"
        ]
        
        client, sheet_id = get_audit_client()
        if client:
            client.open_by_key(sheet_id).worksheet("LEVEL_80_CELL_AUDIT").append_row(row_data)
            
        # Final Audit Log
        log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase19_Draft", f"Draft Ready for {rfq}", "SUCCESS"])
    except Exception as e:
        print(f"Phase 19 Error: {e}")

def log_to_sheet(tab_name, row_data):
    try:
        client, sheet_id = get_audit_client()
        if client: client.open_by_key(sheet_id).worksheet(tab_name).append_row(row_data)
    except: pass

def run_phase11_background(trace_id: str, payload: dict):
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
