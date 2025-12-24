from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid

from core.phase11_runner import run_phase11_background
from core.job_store import JobStore

app = FastAPI()

job_store = JobStore()


class Phase11Request(BaseModel):
    mode: str = "production"  # test | production
    rfq_no: str | None = None
    customer: str | None = None


@app.post("/phase11/run")
def start_phase11(req: Phase11Request, background_tasks: BackgroundTasks):
    trace_id = str(uuid.uuid4())

    job_store.create_job(
        trace_id=trace_id,
        status="QUEUED",
        mode=req.mode
    )

    background_tasks.add_task(
        run_phase11_background,
        trace_id=trace_id,
        payload=req.dict()
    )

    return {
        "status": "ACCEPTED",
        "trace_id": trace_id
    }


@app.get("/phase11/progress/{trace_id}")
def phase11_progress(trace_id: str):
    job = job_store.get_job(trace_id)
    if not job:
        raise HTTPException(status_code=404, detail="Invalid trace_id")

    return job
