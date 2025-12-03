# main_server.py — Updated for Write Optimization V2
from fastapi import FastAPI, HTTPException
from sheet_reader import fetch_rows
from sheet_writer import write_batch_updates
from logic_engine import run_engine
from email_builder import build_email_html
from email_sender import send_email
from logger import get_logger

logger = get_logger()
app = FastAPI()


@app.post("/test/write")
async def test_write_api():
    try:
        # simple test
        return {"status": "write_ok"}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/email")
async def email_api():
    try:
        html = "<p>Your Level-50 email system is working.</p>"
        send_email("Level-50 Test Email", html)
        return {"status": "email_sent"}
    except Exception as e:
        logger.error(f"/email error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
async def run_api(debug: bool = False):
    try:
        rows = fetch_rows()
        aging_updates, vendor_updates, email_blocks = run_engine(rows)
        final_html = build_email_html(email_blocks)

        # Debug mode: return preview only
        if debug:
            return {"status": "run_completed_debug", "email_preview": final_html}

        # Send email
        send_email("Daily RFQ Reminder", final_html)
        logger.info("Email sent successfully.")

        # Perform batch write (V2)
        write_batch_updates(aging_updates, vendor_updates)
        logger.info("Batch updates written successfully.")

        return {"status": "run_completed"}

    except Exception as e:
        logger.error(f"/run error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
