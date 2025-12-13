# =========================================
# backend_api.py
# CORE API ROUTER (NO app HERE)
# =========================================

from fastapi import APIRouter

router = APIRouter()

# -------------------------------
# BASIC HEALTH / TEST ENDPOINT
# -------------------------------
@router.get("/api/ping")
def ping():
    return {"status": "backend_api_ok"}
