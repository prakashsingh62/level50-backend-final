import threading
import time
import os
import sys

# 🔴 PATH FORCING: Ye Railway ko batayega ki file kahaan hai
# Hum saare possible paths add kar rahe hain
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 'app' folder
CORE_DIR = os.path.dirname(os.path.abspath(__file__)) # 'core' folder

if BASE_DIR not in sys.path: sys.path.append(BASE_DIR)
if CORE_DIR not in sys.path: sys.path.append(CORE_DIR)

def run_phase11_background(trace_id: str, payload: dict):
    def force_audit():
        try:
            # Multi-level import try kar rahe hain
            try:
                from core.google_sheets import sheet_manager
            except ImportError:
                import google_sheets
                from google_sheets import sheet_manager
            
            sheet_manager.append_audit_log(
                trace_id=trace_id,
                status="RUNNING",
                details=f"Triggered from Postman: {payload.get('mode', 'N/A')}"
            )
            print(f"✅ Audit Success for {trace_id}")
        except Exception as e:
            print(f"❌ CRITICAL AUDIT ERROR: {str(e)}")

    # Run in background
    threading.Thread(target=force_audit, daemon=True).start()
    threading.Thread(target=_run_pipeline, args=(trace_id,), daemon=True).start()

def _run_pipeline(trace_id: str):
    time.sleep(5) # Simulation time
    try:
        try:
            from core.google_sheets import sheet_manager
        except:
            import google_sheets
            from google_sheets import sheet_manager
            
        sheet_manager.append_audit_log(
            trace_id=trace_id, 
            status="SUCCESS", 
            details="Pipeline Process Finished"
        )
    except:
        pass
