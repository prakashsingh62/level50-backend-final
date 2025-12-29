import threading
import time
import os
import sys

# Path fix to find google_sheets.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_phase11_background(trace_id: str, payload: dict):
    # DIRECT WRITE TO SHEET
    def force_audit():
        try:
            from google_sheets import sheet_manager
            sheet_manager.append_audit_log(
                trace_id=trace_id,
                status="RUNNING",
                details=f"Postman Triggered - Mode: {payload.get('mode')}"
            )
        except Exception as e:
            print(f"Audit failed: {e}")

    # Start background work
    thread = threading.Thread(target=force_audit, daemon=True)
    thread.start()

    # Simulation pipeline
    thread2 = threading.Thread(target=_run_pipeline, args=(trace_id,), daemon=True)
    thread2.start()

def _run_pipeline(trace_id: str):
    time.sleep(5)
    try:
        from google_sheets import sheet_manager
        sheet_manager.append_audit_log(trace_id=trace_id, status="SUCCESS", details="Task Completed")
    except:
        pass
