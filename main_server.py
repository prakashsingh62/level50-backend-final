from fastapi import FastAPI
from sheet_reader import read_rows
from logic_engine import run_engine
from sheet_writer import write_updates, write_test_row
from email_sender import send_email

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "message": "Level-50 backend running"}

# -------------------------------------------------
# TEST WRITE ENDPOINT
# -------------------------------------------------
@app.post("/test/write")
def test_write_api():
    write_test_row()
    return {"status": "test_write_ok"}

# -------------------------------------------------
# EMAIL TEST ENDPOINT  (FIXED)
# -------------------------------------------------
@app.post("/email")
def email_api():
    subject = "Level-50 Test Email"
    body = "Your Level-50 SMTP email sender is working correctly."
    send_email(subject, body)
    return {"status": "email_sent"}

# -------------------------------------------------
# MAIN RUN ENDPOINT  (Level-50 Logic Engine)
# -------------------------------------------------
@app.post("/run")
def run_api():
    rows = read_rows()
    updates, email_content = run_engine(rows)

    if updates:
        write_updates(updates)

    if email_content:
        send_email(email_content["subject"], email_content["body"])

    return {"status": "run_completed"}
