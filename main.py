from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_api import router as backend_router
from audit_report_api import router as audit_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(backend_router)
app.include_router(audit_router)

@app.get("/")
def root():
    return {
        "status": "OK",
        "mode": "LEVEL-80",
        "audit": "ENABLED"
    }
