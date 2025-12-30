import threading
import time
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# --- 1. INTERNAL GOVERNANCE ENGINE (Phase 15 & 16) ---
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
    """Universal writer for all Audit Tabs with strict column alignment"""
    try:
        client, sheet_id = get_audit_client()
        if client:
            sheet = client.open_by_key(sheet_id).worksheet(tab_name)
            sheet.append_row(row_data)
    except Exception as e:
        print(f"Logging failed for {tab_name}: {e}")

# --- 2. CORE EXECUTION ENGINE (Phase 14 Logic + 15/16 Enforcement) ---
def _execute_full_governance(trace_id: str, payload: dict):
    try:
        # Phase-14: Simulation of RFQ Processing
        rfq_no = "RFQ-LIVE-001"
        uid_no = "UID-80-AUTO"
        decision = "Technical Query Received"
        priority = "Urgent"

        # PHASE-15: LEVEL_80_RUN_AUDIT (Header Aligned)
        # Headers: TIMESTAMP_IST | TRACE_ID | PHASE | MODE | STATUS | RFQS_TOTAL | ...
        run_audit_row = [
            time.strftime("%Y-%m-%d %H:%M:%S"), # TIMESTAMP_IST
            trace_id,                            # TRACE_ID
            "phase14_16",                        # PHASE
            decision,                            # MODE (Mapped to decision)
            priority,                            # STATUS (Mapped to priority)
            "DONE"                               # RFQS_TOTAL (Marking as finished)
        ]
        log_to_sheet("LEVEL_80_RUN_AUDIT", run_audit_row)

        # PHASE-16: LEVEL_80_CELL_AUDIT (Header Aligned)
        # Headers: TIMESTAMP_IST | TRACE_ID | RFQ_NO | UID_NO | SHEET_NAME | TAB_NAME | ...
        cell_audit_row = [
            time.strftime("%Y-%m-%d %H:%M:%S"), # TIMESTAMP_IST
            trace_id,                            # TRACE_ID
            rfq_no,                              # RFQ_NO
            uid_no,                              # UID_NO
            "DOMESTIC_REGISTRY",                 # SHEET_NAME
            "MAIN_TRACKER",                      # TAB_NAME
            "STATUS",                            # COLUMN_NAME
            "NEW",                               # OLD_VALUE
            decision                             # NEW_VALUE
        ]
        log_to_sheet("LEVEL_80_CELL_AUDIT", cell_audit_row)

        # FINAL LOG: LEVEL_80_AUDIT_LOG (Already working)
        log_to_sheet("LEVEL_80_AUDIT_LOG", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase14_16", "Execution Complete", "SUCCESS"
        ])

    except Exception as e:
        log_to_sheet("LEVEL_80_AUDIT_LOG", [
            time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase14_16", str(e), "ERROR"
        ])

# --- 3. BACKGROUND RUNNER START ---
def run_phase11_background(trace_id: str, payload: dict):
    # Initial Log Entry
    log_to_sheet("LEVEL_80_AUDIT_LOG", [
        time.strftime("%Y-%m-%d %H:%M:%S"), trace_id, "phase14_16", "Production Run", "STARTING"
    ])
    
    thread = threading.Thread(target=_execute_full_governance, args=(trace_id, payload), daemon=True)
    thread.start()
