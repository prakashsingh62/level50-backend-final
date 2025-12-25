# ------------------------------------------------------------
# MAIN SERVER — PHASE 11 + STATUS API (FINAL)
# ------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

from core.job_store import job_store
from core.phase11_runner import run_phase11_background

app = FastAPI()


# ------------------------------------------------------------
# REQUEST MODELS
# ------------------------------------------------------------

class Phase11Request(BaseModel):
    mode: str = "production"


# ------------------------------------------------------------
# PHASE 11 RUN ENDPOINT
# ------------------------------------------------------------

@app.post("/phase11/run")
def run_phase11(payload: Phase11Request):
    """
    Starts Phase-11 pipeline.
    Returns trace_id immediately.
    """

    trace_id = str(uuid.uuid4())

    # Start background runner (handles ping internally)
    run_phase11_background(
        trace_id=trace_id,
        payload=payload.dict(),
    )

    return {
        "status": "ACCEPTED",
        "trace_id": trace_id,
    }


# ------------------------------------------------------------
# STATUS ENDPOINT (NEW — REQUIRED)
# ------------------------------------------------------------

@app.get("/status/{trace_id}")
def get_status(trace_id: str):
    """
    Returns job status from JobStore.
    """

    job = job_store.get_job(trace_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Trace ID not found"
        )

    return job


# ------------------------------------------------------------
# ROOT / HEALTH (OPTIONAL)
# ------------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "OK",
        "service": "level50-backend-final",
    }
