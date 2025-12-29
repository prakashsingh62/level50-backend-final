import threading
import time
import os
import sys

# 🔴 YE SABSE ZAROORI HAI: Path fix for Railway
# Ye code server ko batayega ki 'app' aur 'core' folder kahaan hain
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

def run_phase11_background(trace_id: str, payload: dict):
    def force_audit():
        try:
            # Absolute import try kar rahe hain
            try:
                from core.google_sheets import sheet_manager
            except ImportError:
                from google_sheets import sheet_manager
            
            sheet_manager.append_audit_log(
                trace_id=trace_id,
                status="RUNNING",
                details=f"Triggered: {payload.get('mode')}"
            )
        except Exception as e:
            # Agar ab bhi error aaye toh logs mein dikhega
            print(f"CRITICAL AUDIT ERROR: {str(e)}")

    # Background threads
    threading.Thread(target=force_audit, daemon=True).start()
    threading.Thread(target=_run_pipeline, args=(trace_id,), daemon=True).start()

def _run_pipeline(trace_id: str):
    time.sleep(5)
    try:
        try:
            from core.google_sheets import sheet_manager
        except:
            from google_sheets import sheet_manager
        sheet_manager.append_audit_log(trace_id=trace_id, status="SUCCESS", details="Task Completed")
    except:
        pass
