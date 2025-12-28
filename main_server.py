from fastapi import FastAPI
from pydantic import BaseModel
import uuid

from core.job_store import job_store
from core.phase11_runner import run_phase11_background

app = FastAPI()

class Phase11Request(BaseModel):
    mode: str = "production"


@app.post("/phase11/run")
def run_phase11(payload: Phase11Request):
    trace_id = str(uuid.uuid4())

    run_phase11_background(
        trace_id=trace_id,
        payload=payload.dict()
    )

    return {
        "status": "ACCEPTED",
        "trace_id": trace_id
    }


@app.get("/")
def root():
    return {
        "status": "OK",
        "service": "level50-backend-final"
    }
