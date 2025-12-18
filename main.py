from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_api import router as backend_router
from audit_report_api import router as audit_router

# 👉 ADD THESE IMPORTS
from rfq_filter_engine import filter_rfqs
from sheet_reader import read_rfqs

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing Routers (UNCHANGED)
app.include_router(backend_router)
app.include_router(audit_router)

# -----------------------------
# ✅ RFQ FILTER ENDPOINT (NEW)
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

# Root
@app.get("/")
def root():
    return {
        "status": "OK",
        "mode": "LEVEL-80",
        "audit": "ENABLED"
    }
