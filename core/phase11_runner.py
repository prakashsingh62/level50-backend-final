import threading
import time
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# --- 1. GOVERNANCE ENGINE (Phase 15 & 16) ---
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

def log_to_sheet(tab_name, row_data):
    """Universal writer for all Audit Tabs"""
    try:
        client, sheet_id = get_audit_client()
        if client:
            sheet = client.open_by_key(sheet_id).worksheet(tab_name)
            sheet.append_row(row_data)
    except Exception as e:
        print(f"Logging failed for {tab_name}: {e}")

# --- 2. CORE PHASE-14 LOGIC (Strict Write Guard) ---
def _execute_full_governance(trace_id: str, payload: dict):
    try:
        # Phase-14: Entry & Normalization
        # Yahan asli RFQs read honge (Abhi simulation hai)
        rfqs = [{"rfq_no": "RFQ-LIVE-001", "customer": "HZL LTD", "due_date": "2025-01-15"}]
        
        for rfq in rfqs:
            # Phase-14: Classification & Priority
            decision = "Technical Query Received" # AI/Rule based logic
            priority = "Urgent"
            
            # Phase-15: Run Audit Enforcement
            log_to_sheet("LEVEL_80_RUN_AUDIT", [
                time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq["rfq_no"], decision, priority, "DONE"
            ])

            # Phase-16: Cell Audit (Before vs After)
            # Strict Rule: Hum sirf status columns badlenge, Customer/RFQ No nahi!
            log_to_sheet("LEVEL_80_CELL_AUDIT", [
                time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, rfq["rfq_no"], "STATUS", "NEW", decision
            ])

        # Final Success Mark
        log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase14_16", "Execution Complete", "SUCCESS"])

    except Exception as e:
        log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase14_16", str(e), "ERROR"])

# --- 3. RUNNER START ---
def run_phase11_background(trace_id: str, payload: dict):
    # Initial Log Entry
    log_to_sheet("LEVEL_80_AUDIT_LOG", [time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase14_16", "Production Run", "STARTING"])
    
    thread = threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True)
    thread.start()
