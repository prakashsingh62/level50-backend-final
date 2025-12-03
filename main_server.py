from fastapi import FastAPI, HTTPException
from sheet_reader import fetch_rows
from sheet_writer import write_updates
from logic_engine import run_engine
from email_sender import send_email
from logger import logger

app = FastAPI()


@app.post("/test/write")
async def test_write_api():
    try:
        write_updates([{
            "row": 2,
            "column": "TEST_COL",
            "value": "API_OK"
        }])
        return {"status": "write_ok"}
    except Exception as e:
        logger.error(f"Error in /test/write: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/email")
async def email_api():
    try:
        send_email("Level-50 Test Email",
                   "<p>Your Level-50 SMTP/SendGrid email sender is working.</p>")
        return {"status": "email_sent"}
    except Exception as e:
        logger.error(f"Error in /email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
async def run_api(debug: bool = False):
    """
    Main Level-50 pipeline:
    1. Read rows
    2. Run logic engine → updates + email_content (list)
    3. Send email only if content exists AND not debug
    4. Apply updates (Google Sheet)
    """

    try:
        rows = fetch_rows()
        updates, email_content = run_engine(rows)

        # email_content is a LIST → join safely
        final_email = "\n".join(email_content).strip()

        # If empty → skip email
        if not final_email:
            if debug:
                return {
                    "status": "run_completed_debug",
                    "email_preview": "NO EMAIL GENERATED"
                }
            return {"status": "run_completed_no_email"}

        # Send mail only if NOT debug
        if not debug:
            send_email("Level-50 RFQ Reminder", final_email)
        else:
            # Only preview result
            return {
                "status": "run_completed_debug",
                "email_preview": final_email
            }

        # Apply sheet updates
        if updates:
            write_updates(updates)

        return {"status": "run_completed"}

    except Exception as e:
        logger.error(f"Error in /run: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
