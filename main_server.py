from fastapi import FastAPI
from sheet_writer import write_test_row
from sheet_reader import read_rows
from backend_api import run_engine
from email_sender import send_email

app = FastAPI(title="Level-50 Automation Backend")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Level-50 backend running"}

@app.get("/read")
def read_api():
    return read_sheet()

@app.post("/run")
def run_api():
    return run_engine()

@app.post("/email")
def email_api():
    return send_email()

@app.post("/test/write")
def test_write_api():
    write_test_row()
    return {"status": "test_write_ok"}
