# ------------------------------------------------------------
# MAIN FASTAPI SERVER  (SAFE + CLEAN + HEALTH ENDPOINT)
# ------------------------------------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Level-70 core imports
from pipeline_engine import Level70Pipeline, apply_approved_update

# Heartbeat & Auto-Recovery (Infinity Pack)
from utils.heartbeat import HeartbeatMonitor

# ------------------------------------------------------------
# APP INITIALIZATION
# ------------------------------------------------------------

app = FastAPI()

# Allow frontend (React UI) & local/dev access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # keep open for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Level-70 pipeline
pipeline = Level70Pipeline()

# Start 24/7 Heartbeat Monitor (Infinity Pack-2)
heartbeat = HeartbeatMonitor()
heartbeat.start()


# ------------------------------------------------------------
# HEALTH ENDPOINT (REQUIRED BY HEARTBEAT MONITOR)
# ------------------------------------------------------------
@app.get("/health")
def health_check():
    """
    This endpoint is pinged every 30 seconds by HeartbeatMonitor.
    Must ALWAYS return {"status": "ok"} if backend is alive.
    """
    return {"status": "ok"}


# ------------------------------------------------------------
# LEVEL-70: MAIN PIPELINE EXECUTION ENDPOINT
# (Email → AI → Matching → Preview)
# ------------------------------------------------------------
@app.post("/run-pipeline")
def run_pipeline_api(payload: dict):
    """
    Receives email_data from AI preprocessor.
    Returns:
        - no_match
        - vendor_query_detected
        - approval_required
    """
    result = pipeline.run(payload)
    return result


# ------------------------------------------------------------
# LEVEL-70: APPROVAL EXECUTION ENDPOINT
# (User clicks YES on UI)
# ------------------------------------------------------------
@app.post("/apply-update")
def apply_update_api(data: dict):
    """
    React UI calls this when human approves update.
    """
    row = data.get("row")
    ai_output = data.get("ai_output", {})

    result = apply_approved_update(row, ai_output)
    return result


# ------------------------------------------------------------
# ROOT TEST ENDPOINT (Optional)
# ------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "Level-70 Backend Running"}
