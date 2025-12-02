# backend_api.py
#
# Level-50 final API router
# Safe for Railway / Render
# No DB writes, no sheet overwrites except via controlled functions

from fastapi import APIRouter
from logger import get_logger
from sheet_reader import read_rows
from logic_engine import run_engine
from sheet_writer import write_updates
from templates import build_email
from email_sender import send_email

router = APIRouter()
log = get_logger()

@router.get("/health")
def health():
    return {"status": "ok", "message": "Level-50 backend running"}

@router.get("/read")
def read_sheet_api():
    try:
        rows = read_rows()
        return {"count": len(rows), "rows": rows}
    except Exception as e:
        log.error(f"/read failed: {e}")
        return {"error": str(e)}

@router.post("/run")
def run_engine_api():
    try:
        rows = read_rows()
        processed = run_engine(rows)

        if not processed:
            return {"status": "no_updates"}

        write_updates(processed)
        return {"status": "success", "updated": len(processed)}

    except Exception as e:
        log.error(f"/run failed: {e}")
        return {"error": str(e)}

@router.post("/email")
def send_email_api():
    try:
        rows = read_rows()
        processed = run_engine(rows)

        if not processed:
            return {"status": "no_email"}

        subject, body = build_email(processed)
        send_email(subject, body)

        return {"status": "sent"}

    except Exception as e:
        log.error(f"/email failed: {e}")
        return {"error": str(e)}

@router.post("/test/write")
def test_write_api():
    """
    Only writes a simple dummy row to verify write access.
    This is EXACTLY the same endpoint we agreed earlier.
    """
    try:
        write_updates(
            [{"_ROW": 2, "TEST_WRITE": "OK — backend API working"}]
        )
        return {"status": "test_write_ok"}
    except Exception as e:
        log.error(f"/test/write failed: {e}")
        return {"error": str(e)}
