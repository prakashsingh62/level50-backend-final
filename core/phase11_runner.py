import threading
import time
import os
import json
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
def get_audit_client():
    try:
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
        return gspread.authorize(creds), sheet_id
    except Exception as e:
        print(f"Audit Connection Error: {e}")
        return None, None

# AI Brain Setup (Phase 17)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. THE AI BRAIN (Decision Engine) ---
def analyze_email_with_ai(email_text):
    prompt = f"""
    You are an Industrial Inquiry Manager. Analyze this email text and return ONLY a JSON object:
    1. "rfq_no": Extract RFQ number (like RFQ-XXX), if not found use "UNKNOWN".
    2. "intent": What does the sender want? (Options: GAD_REQUEST, PRICE_NEGOTIATION, DELIVERY_QUERY, ORDER_CONFIRMATION).
    3. "status_update": A short 3-4 word status for a spreadsheet.
    
    Email Text: {email_text}
    """
    try:
        response = model.generate_content(prompt)
        # Cleaning the response to get pure JSON
        raw_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(raw_text)
    except:
        return {"rfq_no": "ERROR", "intent": "UNKNOWN", "status_update": "AI Processing Failed"}

# --- 3. AUDIT WRITER ---
def log_to_sheet(tab_name, row_data):
    try:
        client, sheet_id = get_audit_client()
        if client:
            sheet = client.open_by_key(sheet_id).worksheet(tab_name)
            sheet.append_row(row_data)
    except Exception as e:
        print(f"Logging failed for {tab_name}: {e}")

# --- 4. CORE EXECUTION (AI Powered) ---
def _execute_full_governance(trace_id: str, payload: dict):
    try:
        # Get Email Text from Postman Payload
        email_content = payload.get("payload_details", {}).get("message", "No content")
        
        # AI ANALYSIS START
        ai_decision = analyze_email_with_ai(email_content)
        
        rfq_no = ai_decision.get("rfq_no", "RFQ-LIVE-001")
        new_status = ai_decision.get("status_update", "Technical Query Received")

        # PHASE-15: RUN AUDIT (Aligned)
        run_audit_row = [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", 
            ai_decision.get("intent"), "DONE", "1"
        ]
        log_to_sheet("LEVEL_80_RUN_AUDIT", run_audit_row)

        # PHASE-16: CELL AUDIT (Real AI Update)
        cell_audit_row = [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq_no, "UID-80-AUTO",
            "DOMESTIC_REGISTRY", "MAIN_TRACKER", "STATUS", "NEW", new_status
        ]
        log_to_sheet("LEVEL_80_CELL_AUDIT", cell_audit_row)

        log_to_sheet("LEVEL_80_AUDIT_LOG", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", "AI Decision: " + new_status, "SUCCESS"
        ])

    except Exception as e:
        log_to_sheet("LEVEL_80_AUDIT_LOG", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", str(e), "ERROR"
        ])

def run_phase11_background(trace_id: str, payload: dict):
    log_to_sheet("LEVEL_80_AUDIT_LOG", [
        time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", "AI Brain Processing", "STARTING"
    ])
    thread = threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True)
    thread.start()
