from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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

from email_reader import router as email_reader_router
app.include_router(email_reader_router)

from manual_reminder import router as manual_reminder_router
app.include_router(manual_reminder_router)

# ---------------------------
# NEW: RFQ Search Router
# ---------------------------
from search_rfq import router as search_rfq_router
app.include_router(search_rfq_router)


# ---------------------------
# Root
# ---------------------------
@app.get("/")
def root():
    return {"status": "RFQ Automation Backend Running"}
