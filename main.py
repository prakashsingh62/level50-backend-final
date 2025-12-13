from fastapi import FastAPI

# Routers
from backend_api import router as backend_router
from audit_report_api import router as audit_router

app = FastAPI()

# Register ALL routers here
app.include_router(backend_router)
app.include_router(audit_router)

@app.get("/")
def root():
    return {
        "status": "OK",
        "mode": "LEVEL-80",
        "audit": "ENABLED"
    }
