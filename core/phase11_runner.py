from core.job_store import job_store
import threading
import time

def run_phase11_background(trace_id: str, payload: dict):
    # Seedha STARTING entry trigger karo
    job_store.update_job(trace_id=trace_id, status="STARTING", result={"mode": "production"})
    
    thread = threading.Thread(target=_run_phase11_pipeline, args=(trace_id,), daemon=True)
    thread.start()

def _run_phase11_pipeline(trace_id: str):
    time.sleep(2)
    # Final SUCCESS entry
    job_store.update_job(trace_id=trace_id, status="SUCCESS", result={"msg": "Done"})
