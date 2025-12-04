from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers in root folder
from run_router import router as run_router
from router_test import router as test_router
from router_email import router as email_router

app = FastAPI(
    title="Level-50 Automation Engine",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clean URL mounts
app.include_router(run_router, prefix="", tags=["RUN"])          # → /run
app.include_router(test_router, prefix="/test", tags=["TEST"])    # → /test/write
app.include_router(email_router, prefix="/email", tags=["EMAIL"]) # → /email/send

@app.get("/")
async def root():
    return {"status": "Level-50 backend active"}
