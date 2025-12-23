from typing import Optional
from fastapi import FastAPI
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

@app.post("/phase11/run")
def phase11(payload: Optional[dict] = None):
    return run_phase11(payload)
