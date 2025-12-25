# ------------------------------------------------------------
# MAIN SERVER (FINAL, PROD-SAFE)
# ------------------------------------------------------------
# ✔ NO BackgroundTasks
# ✔ Pipeline triggered via internal threading (phase11_runner)
# ✔ Browser-safe status endpoint
# ✔ Railway / Uvicorn compatible
# ------------------------------------------------------------

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

from core.job_store import JobStore

app = FastAPI()
job_store = JobStore()


# -----------------------------
# REQUEST MODEL
# -----------------------------
class Phase11Request(BaseModel):
    mode: str = "production"   # ping | production
    rfq_no: str | None = None
    customer: str | None = None


# -----------------------------
# START PHASE 11
# -----------------------------
@app.post("/phase11/run")
def start_phase11(req: Phase11Request):
    trace_id = str(uuid.uuid4())

    # 🔥 CRITICAL:
    # Import ONLY inside function (prevents boot crash)
    from core.phase11_runner import run_phase11_background

    try:
        # ✅ DIRECT CALL (NO BackgroundTasks)
        run_phase11_background(
            trace_id=trace_id,
            payload=req.dict()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ACCEPTED",
        "trace_id": trace_id
    }


# -----------------------------
# PHASE 11 STATUS (BROWSER SAFE)
# -----------------------------
@app.get("/phase11/status/{trace_id}")
def get_phase11_status(trace_id: str):
    job = job_store.get_job(trace_id)

    if not job:
        raise HTTPException(status_code=404, detail="TRACE_ID_NOT_FOUND")

    return {
        "trace_id": trace_id,
        "status": job.get("status"),
        "result": job.get("result"),
        "error": job.get("error"),
    }
