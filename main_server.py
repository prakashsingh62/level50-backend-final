from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sheet_reader import fetch_rows
from sheet_writer import write_updates   # ✅ CORRECT
from logic_engine import run_engine
from email_sender import send_email
from logger import logger

app = FastAPI(title="Level-50 Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

# ----------------------------------------------------
# Test Write API
# ----------------------------------------------------
@app.post("/test/write")
async def test_write_api():
    try:
        write_updates([{"row": 2, "column": "TEST_COL", "value": "API_OK"}])   # ✅ FIXED
        return {"status": "write_ok"}
    except Exception as e:
        logger.error(f"Error in /test/write: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------
# Test Email API
# ----------------------------------------------------
@app.post("/email")
async def email_api():
    try:
        send_email("Level-50 Test Email", "<p>Your Level-50 SMTP/SendGrid email sender is working.</p>")
        return {"status": "email_sent"}
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------------------------------
# RUN API (DEBUG MODE SUPPORTED)
# ----------------------------------------------------
@app.post("/run")
async def run_api(debug: bool = False):

    try:
        rows = fetch_rows()
        updates, email_content = run_engine(rows)

        # DEBUG MODE
        if debug and not email_content.strip():
            email_content = (
                "<h3>[DEBUG MODE]</h3>"
                "<p>No reminder sections were generated.</p>"
                "<p>This email is only for debugging.</p>"
            )

        # No content & not debug → do not send email
        if not email_content.strip():
            return {"status": "run_completed_no_email"}

        # Send email
        send_email("Level-50 RFQ Reminder", email_content)

        # Apply updates (REAL WRITER)
        if updates:
            write_updates(updates)   # ✅ FIXED

        return {"status": "run_completed"}

    except Exception as e:
        logger.error(f"Error in /run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
