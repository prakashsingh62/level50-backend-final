from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from router_email import router as email_router
from router_test import router as test_router
from run_router import router as run_router

app = FastAPI(
    title="Level-50 Backend",
    description="Final Production API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health():
    return {"status": "ok", "message": "Level-50 backend running"}

# Routers
app.include_router(test_router)
app.include_router(email_router)
app.include_router(run_router)

if __name__ == "__main__":
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000)
