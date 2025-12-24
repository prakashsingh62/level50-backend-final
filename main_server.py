from fastapi import FastAPI, BackgroundTasks, Request
from core.phase11_runner import run_phase11_async
from core.job_store import get_job

app = FastAPI()


@app.post("/phase11/run")
async def phase11_run(payload: dict, background_tasks: BackgroundTasks):
    trace_id = payload.get("trace_id")

    if not trace_id:
        return {
            "status": "ERROR",
            "reason": "trace_id missing"
        }

    background_tasks.add_task(run_phase11_async, payload)

    return {
        "status": "ACCEPTED",
        "phase": "11",
        "mode": "PRODUCTION",
        "trace_id": trace_id
    }


@app.get("/phase11/status/{trace_id}")
def phase11_status(trace_id: str):
    job = get_job(trace_id)

    if not job:
        return {
            "status": "NOT_FOUND",
            "trace_id": trace_id
        }

    return {
        "status": "OK",
        "trace_id": trace_id,
        "job": job
    }
