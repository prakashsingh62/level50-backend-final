from fastapi import APIRouter
from email_sender import send_email
from email_builder import build_email_html

router = APIRouter()

@router.post("/send")
async def send_email_route():
    """
    Manual email trigger (debugging)
    """
    html = build_email_html([])
    send_email(html)
    return {"status": "email_sent_test"}
