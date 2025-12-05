from fastapi import APIRouter
from daily_sender import send_manual_reminder

router = APIRouter()

@router.post("/manual-reminder")
def manual_reminder():
    result = send_manual_reminder()
    return {
        "status": "manual reminder triggered",
        "result": result
    }
