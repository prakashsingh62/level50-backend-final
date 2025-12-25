# ------------------------------------------------------------
# MAIN SERVER — FINAL, STABLE, PROD-SAFE
# ------------------------------------------------------------

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid

from core.job_store import job_store


app = FastAPI(title="Level-50 Backend Final")


# ------------------------------------------------------------
# REQUEST MODELS
# ------------------------------------------------------------

class Phase11Request(BaseModel):
    mode: str = "production"   # test | production
    rfq_no: str | None = None
    customer: str | None = None


# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

@app.post("/phase11/run")
def start_phase11(req: Phase11Request, background_tasks: BackgroundTasks):
    """
    Starts Phase-11 asynchronously.
    Returns trace_id immediately.
    """

    trace_id = str(uuid.uuid4())

    # ❗ IMPORTANT:
    # Import ONLY here (runtime), NEVER at top-level
    from core.phase11_runner import run_phase11_background

    background_tasks.add_task(
        run_phase11_background,
        trace_id,
        req.dict()
    )

    return {
        "status": "ACCEPTED",
        "trace_id": trace_id
    }


@app.get("/phase11/progress/{trace_id}")
def phase11_progress(trace_id: str):
    """
    Returns job progress/status for given trace_id.
    """

    job = job_store.get_job(trace_id)

    if not job:
        raise HTTPException(status_code=404, detail="TRACE_ID_NOT_FOUND")

    return job


@app.get("/")
def health_check():
    return {"status": "OK"}
