from fastapi import FastAPI, Request
import uuid

from core.job_store import job_store
from core.phase11_runner import run_phase11_background

app = FastAPI()

@app.get("/")
def health():
    return {"status": "OK"}

@app.post("/phase11/run")
async def run_phase11(request: Request):
    payload = await request.json()
    trace_id = str(uuid.uuid4())

    run_phase11_background(trace_id, payload)

    return {
        "status": "ACCEPTED",
        "trace_id": trace_id
    }

@app.get("/status/{trace_id}")
def get_status(trace_id: str):
    job = job_store.get_job(trace_id)
    if not job:
        return {"status": "NOT_FOUND"}
    return job
