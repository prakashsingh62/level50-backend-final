# main_server.py
from fastapi import FastAPI, HTTPException
from sheet_reader import fetch_rows
from sheet_writer import write_updates
from logic_engine import run_engine
from email_builder import build_email_html
from email_sender import send_email
from logger import get_logger

logger = get_logger()

app = FastAPI()

@app.post("/test/write")
async def test_write_api():
    try:
        test_updates = [
            {"row": 2, "column": "SYSTEM NOTES", "value": "API_OK"}
        ]
        write_updates(test_updates)
        return {"status": "write_ok"}
    except Exception as e:
        logger.error(f"Error in /test/write: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/email")
async def email_api():
    try:
        html_body = "<p>Your Level-50 email system is working.</p>"
        send_email("Level-50 Test Email", html_body)
        return {"status": "email_sent"}
    except Exception as e:
        logger.error(f"Error in /email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run")
async def run_api(debug: bool = False):
    try:
        rows = fetch_rows()
        updates, email_blocks = run_engine(rows)
        final_html = build_email_html(email_blocks)

        if not email_blocks:
            if debug:
                return {
                    "status": "run_completed_debug",
                    "email_preview": "NO EMAIL GENERATED"
                }
            return {"status": "run_completed_no_email"}

        if not debug:
            send_email("Level-50 Daily RFQ Reminder", final_html)
        else:
            return {
                "status": "run_completed_debug",
                "email_preview": final_html
            }

        if updates:
            write_updates(updates)

        return {"status": "run_completed"}

    except Exception as e:
        logger.error(f"Error in /run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
