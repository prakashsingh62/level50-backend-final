import threading
import time
import os
import json
import re
import gspread
import google.generativeai as genai
from google.oauth2.service_account import Credentials

# --- 1. GOOGLE SHEETS AUTH ---
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

# --- 2. AI CONFIGURATION (Ziddi AI Mode) ---
# API Key from your Railway Variables
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_email_with_ai(email_text):
    # Forced Safety Bypass: Har inquiry process hogi
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    
    # AI Instruction for Strict JSON
    prompt = f"""
    You are an Industrial Inquiry Manager. Analyze this email and return ONLY a JSON object.
    Email: {email_text}
    
    JSON Format:
    {{
        "rfq_no": "Extract RFQ number (e.g. RFQ-555)",
        "intent": "GAD_REQUEST or PRICE_NEGOTIATION",
        "status_update": "Short summary (e.g. Drawings Asked)"
    }}
    """
    
    try:
        response = model.generate_content(
            prompt, 
            safety_settings=safety_settings,
            generation_config={"response_mime_type": "application/json"}
        )
        if response.text:
            return json.loads(response.text)
        raise ValueError("Empty response from AI")
    except Exception as e:
        # Fallback Logic: Agar AI busy hai toh manual regex se RFQ nikal lo
        rfq_match = re.search(r'RFQ-?\d+', email_text, re.IGNORECASE)
        fallback_rfq = rfq_match.group(0).upper() if rfq_match else "RFQ-MANUAL"
        return {
            "rfq_no": fallback_rfq,
            "intent": "AI_BUSY_RETRY",
            "status_update": "AI Processing... Check Soon"
        }

# --- 3. AUDIT WRITER ---
def log_to_sheet(tab_name, row_data):
    try:
        client, sheet_id = get_audit_client()
        if client:
            sheet = client.open_by_key(sheet_id).worksheet(tab_name)
            sheet.append_row(row_data)
    except Exception as e:
        print(f"Logging failed: {e}")

# --- 4. CORE EXECUTION ---
def _execute_full_governance(trace_id: str, payload: dict):
    try:
        email_content = payload.get("payload_details", {}).get("message", "No content")
        
        # 🧠 AI DECISION
        ai_decision = analyze_email_with_ai(email_content)
        
        # Phase 15: RUN AUDIT
        log_to_sheet("LEVEL_80_RUN_AUDIT", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", 
            ai_decision.get("intent"), "DONE", "1"
        ])

        # Phase 16: CELL AUDIT (AI Final Result)
        log_to_sheet("LEVEL_80_CELL_AUDIT", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, ai_decision.get("rfq_no"), "UID-80-AUTO",
            "DOMESTIC_REGISTRY", "MAIN_TRACKER", "STATUS", "NEW", ai_decision.get("status_update")
        ])

        # Final Log Entry
        log_to_sheet("LEVEL_80_AUDIT_LOG", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", 
            f"Result: {ai_decision.get('rfq_no')}", "SUCCESS"
        ])

    except Exception as e:
        log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", str(e), "ERROR"])

def run_phase11_background(trace_id: str, payload: dict):
    # Initial Start Log
    log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase17_AI", "AI Brain Wakeup", "STARTING"])
    threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True).start()
