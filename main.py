from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from run_router import router as run_router
from router_test import router as test_router
from email_router import router as email_router
from manual_reminder_router import router as manual_router  # <-- NEW IMPORTANT ROUTER

app = FastAPI(
    title="Level 50 Backend Final",
    description="Production backend for RFQ automation",
    version="1.0.0"
)

# CORS (allows all clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(run_router)
app.include_router(test_router)
app.include_router(email_router)
app.include_router(manual_router)  # <-- REQUIRED FOR MANUAL REMINDER


@app.get("/")
def root():
    return {"message": "Level 50 Backend Final Running"}
