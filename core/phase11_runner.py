import threading
import time
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# --- INTERNAL SHEET ENGINE (No Imports Needed) ---
def _direct_sheet_update(trace_id, status, details_str):
    try:
        # Railway variables se data uthayega
        creds_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        sheet_id = os.environ.get("AUDIT_SHEET_ID")
        
        if not creds_json or not sheet_id:
            print("Environment Variables Missing!")
            return

        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=scopes)
        client = gspread.authorize(creds)
        
        # Direct Sheet Access
        sheet = client.open_by_key(sheet_id).worksheet("LEVEL_80_AUDIT_LOG")
        
        # Row data prepare karo
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, trace_id, "phase11", details_str, status]
        
        sheet.append_row(row)
        print(f"✅ SHEET UPDATED: {trace_id} -> {status}")
    except Exception as e:
        print(f"❌ SHEET ENGINE FAILED: {str(e)}")

# --- MAIN RUNNER ---
def run_phase11_background(trace_id: str, payload: dict):
    # Immediate update (STARTING)
    threading.Thread(
        target=_direct_sheet_update, 
        args=(trace_id, "STARTING", f"Mode: {payload.get('mode')}"), 
        daemon=True
    ).start()
    
    # Start the actual process
    thread = threading.Thread(target=_run_pipeline, args=(trace_id,), daemon=True)
    thread.start()

def _run_pipeline(trace_id: str):
    time.sleep(5) # Simulation
    # Final update (SUCCESS)
    _direct_sheet_update(trace_id, "SUCCESS", "Pipeline Completed")
