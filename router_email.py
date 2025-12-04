from fastapi import APIRouter
from email_sender import send_email

router = APIRouter()

@router.post("/email")
def email_api():
    result = send_email()
    return {"status": "email_sent", "response": result}
