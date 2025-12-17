from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from backend_api import router as backend_router
from audit_report_api import router as audit_router
from run_router import router as run_router   # ✅ ADD THIS

app = FastAPI()

# ==============================
# CORS CONFIG (LEVEL-80 FIX)
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://level50-frontend.vercel.app",
        "*",  # temporary wide open for strict-mode testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Register ALL routers
# ==============================
app.include_router(backend_router)
app.include_router(audit_router)
app.include_router(run_router, prefix="/api")  # ✅ THIS FIXES /api/run

# ==============================
# Root Health Check
# ==============================
@app.get("/")
def root():
    return {
        "status": "OK",
        "mode": "LEVEL-80",
        "audit": "ENABLED"
    }
