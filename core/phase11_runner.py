import threading
import time
import os
import json
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION & AUTH ---
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

# AI Brain Setup with Phase 17 fixes
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. THE AI BRAIN (Fixed for "Failed" error) ---
def analyze_email_with_ai(email_text):
    # Fix for Safety Filters
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
    
    prompt = f"""
    Analyze this industrial business email and return ONLY a JSON object. 
    Do not include any conversational text or markdown.
    
    Format: 
    {{
        "rfq_no": "Extract RFQ number (e.g., RFQ-555). If none, use UNKNOWN",
        "intent": "GAD_REQUEST or PRICE_QUERY or DELIVERY_QUERY",
        "status_update": "Short 3-word summary of the request"
    }}
    
    Email Content: {email_text}
    """
    
    try:
        # Strict JSON Mode enabled
        response = model.generate_content(
            prompt,
            safety_settings=safety_settings,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Analysis Crash: {e}")
        return {
            "rfq_no": "ERROR-FIX",
            "intent": "RETRY_REQUIRED",
            "status_update": "AI Safety/Format Error"
        }

# --- 3. AUDIT WRITER ---
def log_to_sheet(tab_name, row_data):
    try:
        client, sheet_id = get_audit_client()
        if client:
            sheet = client.open_by_key(sheet_id).worksheet(tab_name)
            sheet.append_row(row_data)
    except Exception as e:
        print(f"Logging failed for {tab_name}: {e}")

# --- 4. CORE EXECUTION (Governance & Audit) ---
def _execute_full_governance(trace_id: str, payload: dict):
    try:
        # Extract message from Postman
        email_content = payload.get("payload_details", {}).get("message", "No content")
        
        # 🧠 AI DECISION MAKING
        ai_decision = analyze_email_with_ai(email_content)
        
        rfq_no = ai_decision.get("rfq_no", "UNKNOWN-RFQ")
        new_status = ai_decision.get("status_update", "Status Pending")
        intent = ai_decision.get("intent", "GENERAL")

        # Update RUN_AUDIT (Phase 15 logic)
        run_audit_row = [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", 
            intent, "DONE", "1"
        ]
        log_to_sheet("LEVEL_80_RUN_AUDIT", run_audit_row)

        # Update CELL_AUDIT (Phase 16 logic)
        cell_audit_row = [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq_no, "UID-80-AUTO",
            "DOMESTIC_REGISTRY", "MAIN_TRACKER", "STATUS", "NEW", new_status
        ]
        log_to_sheet("LEVEL_80_CELL_AUDIT", cell_audit_row)

        # Final Log
        log_to_sheet("LEVEL_80_AUDIT_LOG", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", f"Success: {rfq_no}", "SUCCESS"
        ])

    except Exception as e:
        log_to_sheet("LEVEL_80_AUDIT_LOG", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", str(e), "ERROR"
        ])

def run_phase11_background(trace_id: str, payload: dict):
    # Initial Log to Audit
    log_to_sheet("LEVEL_80_AUDIT_LOG", [
        time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", "AI Brain Wakeup", "STARTING"
    ])
    thread = threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True)
    thread.start()
