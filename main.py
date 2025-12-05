from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from backend_api import router as backend_router
from manual_reminder_router import router as manual_router

app = FastAPI(
    title="Level 51 Automation",
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

# Routers include
app.include_router(backend_router, prefix="/api")
app.include_router(manual_router)

@app.get("/")
def root():
    return {"status": "Level 51 Automation Server Running"}

