from fastapi import APIRouter, Query
from logic_engine import run_level50
from email_builder import build_email
from email_sender import send_email
from config import EMAIL_RECIPIENTS

router = APIRouter()

@router.post("/run")
def run_api(debug: bool = Query(False)):
    result = run_level50()
    html = build_email(result["summary"], result["sections"])

    if debug:
        return {
            "status": "debug",
            "email_preview": html
        }

    send_email(
        to_emails=EMAIL_RECIPIENTS,
        subject="Level-50 RFQ Reminder",
        html_content=html
    )

    return {"status": "email_sent"}
