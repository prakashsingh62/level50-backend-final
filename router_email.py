from fastapi import APIRouter
from logic_engine import run_level50
from email_builder import build_email
from email_sender import send_email
from config import EMAIL_RECIPIENTS

router = APIRouter()

@router.post("/email")
def send_email_route():
    result = run_level50()
    html = build_email(result["summary"], result["sections"])

    send_email(
        to_emails=EMAIL_RECIPIENTS,
        subject="Level-50 RFQ Reminder",
        html_content=html
    )

    return {"status": "email_sent"}
