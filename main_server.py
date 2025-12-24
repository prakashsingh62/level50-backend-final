from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.phase11_runner import run_phase11

app = FastAPI(title="Level-80 / Phase-11 Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "OK", "mode": "LEVEL-80", "audit": "ENABLED"}

# ✅ MATCH POSTMAN URL
@app.post("/phase11")
async def phase11(request: Request):
    payload = await request.json()
    return run_phase11(payload)
