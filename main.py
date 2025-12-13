# =========================================
# main.py — FastAPI Entry (Level-80 Strict)
# =========================================

# 🔒 Level-80 Strict Mode Kernel (MUST BE FIRST)
from strict_mode_kernel import enforce_zero_assumption

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔴 LEVEL-80 HARD GATE — executes at app startup
enforce_zero_assumption()   # DO NOT MOVE / DO NOT WRAP

# ---------------------------
# CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Routers
# ---------------------------
from backend_api import router as backend_api_router
app.include_router(backend_api_router)

# ---------------------------
# RFQ Search Router
# ---------------------------
from search_rfq import router as search_rfq_router
app.include_router(search_rfq_router)

# ---------------------------
# Root
# ---------------------------
@app.get("/")
def root():
    return {"status": "RFQ Automation Backend Running"}
