# ------------------------------------------------------------
# MAIN SERVER (FINAL, PROD-SAFE, IMPORT-CLEAN)
# ------------------------------------------------------------
# - No phase11_runner import at module load
# - phase11_runner imported ONLY inside route
# - Railway / Uvicorn safe
# ------------------------------------------------------------

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid

from core.job_store import JobStore

app = FastAPI()
job_store = JobStore()


# -----------------------------
# REQUEST MODEL
# -----------------------------
class Phase11Request(BaseModel):
    mode: str = "production"   # test | production
    rfq_no: str | None = None
    customer: str | None = None


# -----------------------------
# START PHASE 11 (ASYNC)
# -----------------------------
@app.post("/phase11/run")
def start_phase11(
    req: Phase11Request,
    background_tasks: BackgroundTasks
):
    trace_id = str(uuid.uuid4())

    # 🚨 CRITICAL FIX:
    # Import ONLY here (never at top of file)
    from core.phase11_runner import run_phase11_background

    try:
        background_tasks.add_task(
            run_phase11_background,
            trace_id,
            req.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ACCEPTED",
        "trace_id": trace_id
    }


# -----------------------------
# PHASE 11 PROGRESS
# -----------------------------
@app.get("/phase11/progress/{trace_id}")
def phase11_progress(trace_id: str):
    job = job_store.get_job(trace_id)

    if not job:
        raise HTTPException(status_code=404, detail="Trace ID not found")

    return job
