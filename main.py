from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from backend_api import router as backend_router
from audit_report_api import router as audit_router

# RFQ filtering
from rfq_filter_engine import filter_rfqs
from sheet_reader import read_rfqs

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Existing Routers (UNCHANGED)
# -----------------------------
app.include_router(backend_router)
app.include_router(audit_router)

# -----------------------------
# RFQ FILTER ENDPOINT
# -----------------------------
@app.get("/rfqs/filter")
def rfqs_filter(
    status: str | None = None,
    vendor_pending: bool | None = None,
    overdue: bool | None = None,
    last_n_days: int = 30,
    page: int = 1,
    page_size: int = 50
):
    rows = read_rfqs()
    return filter_rfqs(
        rows=rows,
        status=status,
        vendor_pending=vendor_pending,
        overdue=overdue,
        last_n_days=last_n_days,
        page=page,
        page_size=page_size
    )

# -----------------------------
# SAFETY / DRY-RUN VISIBILITY
# -----------------------------
@app.get("/system/mode")
def system_mode():
    return {
        "automation_enabled": os.getenv("AUTOMATION_ENABLED", "false"),
        "dry_run": os.getenv("DRY_RUN", "true"),
    }

# -----------------------------
# Root / Health
# -----------------------------
@app.get("/")
def root():
    return {
        "status": "OK",
        "mode": "LEVEL-80",
        "audit": "ENABLED"
    }

@app.get("/debug/headers")
def debug_headers():
    rows = read_rfqs()
    if not rows:
        return {"error": "no rows returned"}
    return {
        "headers": list(rows[0].keys())
    }
