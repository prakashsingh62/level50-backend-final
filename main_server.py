from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from run_router import router as run_router
from router_email import router as email_router
from router_test import router as test_router

app = FastAPI(title="Level-50 Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(test_router)
app.include_router(email_router)
app.include_router(run_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Level-50 backend running"}
