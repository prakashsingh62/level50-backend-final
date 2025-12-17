# ------------------------------------------------------------
# MAIN FASTAPI SERVER — PHASE-11 LOCKED & STABLE
# ------------------------------------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pipeline_engine import Level70Pipeline, apply_approved_update
from core.phase11_runner import run_phase11
from utils.heartbeat import HeartbeatMonitor

app = FastAPI(title="Level-80 / Phase-11 Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = Level70Pipeline()

heartbeat = HeartbeatMonitor()
heartbeat.start()

# ------------------------------------------------------------
# HEALTH
# ------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ------------------------------------------------------------
# LEGACY (DO NOT TOUCH)
# ------------------------------------------------------------
@app.post("/run-pipeline")
def run_pipeline(payload: dict):
    return pipeline.run(payload)

@app.post("/apply-update")
def apply_update(data: dict):
    return apply_approved_update(
        data.get("row"),
        data.get("ai_output", {})
    )

# ------------------------------------------------------------
# ✅ PHASE-11 (ONLY ENTRY POINT)
# ------------------------------------------------------------
@app.post("/phase11/run")
def phase11(payload: dict):
    return run_phase11(payload)

# ------------------------------------------------------------
# ROOT
# ------------------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "Phase-11 Backend Running",
        "endpoint": "/phase11/run"
    }

# ------------------------------------------------------------
# START
# ------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
