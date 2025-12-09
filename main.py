from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers in root folder
from run_router import router as run_router
from router_test import router as test_router

# ⭐ NEW — Auto-Suggest API Router
from backend_api import router as suggest_router


app = FastAPI(
    title="Level-50 Automation Engine",
    version="1.0.0",
)

# =====================
#        CORS
# =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
#     URL MOUNTS
# =====================
app.include_router(run_router, prefix="", tags=["RUN"])
app.include_router(test_router, prefix="/test", tags=["TEST"])

# ⭐ ADD THIS — Suggestion API mount
app.include_router(suggest_router, prefix="", tags=["SUGGEST"])


@app.get("/")
async def root():
    return {"status": "Level-50 backend active"}
