from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from core.phase11_runner import run_phase11_background, JOB_STORE
import uuid
from datetime import datetime

app = FastAPI(title="Level-80 Phase-11 Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "OK", "mode": "LEVEL-80", "phase": "11"}

# ─────────────────────────────────────────────
# STEP 1 — CREATE JOB (TRACE ID)
# ─────────────────────────────────────────────
@app.post("/phase11")
def create_phase11_job(payload: Dict):
    trace_id = str(uuid.uuid4())

    JOB_STORE[trace_id] = {
        "status": "PENDING",
        "created_at": datetime.utcnow().isoformat(),
        "payload": payload,
        "processed": 0,
        "error": None,
    }

    return {
        "status": "ACCEPTED",
        "trace_id": trace_id,
        "mode": "TEST" if payload.get("test") else "PRODUCTION",
    }

# ─────────────────────────────────────────────
# STEP 2 — RUN BACKGROUND JOB
# ─────────────────────────────────────────────
@app.post("/phase11/run")
def run_phase11(payload: Dict, background_tasks: BackgroundTasks):
    trace_id = payload.get("trace_id")

    if not trace_id:
        raise HTTPException(status_code=400, detail="trace_id missing")

    if trace_id not in JOB_STORE:
        raise HTTPException(status_code=404, detail="invalid trace_id")

    if JOB_STORE[trace_id]["status"] not in ["PENDING", "FAILED"]:
        return {"status": "IGNORED", "reason": "already running or completed"}

    JOB_STORE[trace_id]["status"] = "RUNNING"

    background_tasks.add_task(run_phase11_background, trace_id)

    return {"status": "STARTED", "trace_id": trace_id}

# ─────────────────────────────────────────────
# STEP 3 — STATUS / PROGRESS
# ─────────────────────────────────────────────
@app.get("/phase11/status/{trace_id}")
def phase11_status(trace_id: str):
    if trace_id not in JOB_STORE:
        raise HTTPException(status_code=404, detail="invalid trace_id")

    return JOB_STORE[trace_id]
