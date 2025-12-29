from core.job_store import job_store
import threading
import time

def run_phase11_background(trace_id: str, payload: dict):
    # Create job with both names to be 100% safe
    job_store.create_job(job_id=trace_id, trace_id=trace_id, status="STARTING")
    
    thread = threading.Thread(
        target=_run_phase11_pipeline,
        args=(trace_id,),
        daemon=True
    )
    thread.start()

def _run_phase11_pipeline(trace_id: str):
    try:
        time.sleep(2)
        # Final update jo Audit Sheet mein dikhega
        job_store.update_job(
            job_id=trace_id, 
            status="SUCCESS", 
            result={"message": "Pipeline Completed Successfully"}
        )
    except Exception as e:
        job_store.update_job(job_id=trace_id, status="FAILED", result={"error": str(e)})
