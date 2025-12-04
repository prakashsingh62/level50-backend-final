from fastapi import APIRouter, Query
from logic_engine import run_level50
from email_sender import send_email
from config import MODE

router = APIRouter()


@router.post("/run")
def run_api(debug: bool = Query(False, description="Enable debug mode")):
    """
    Main endpoint to run Level-50 logic.
    """
    result = run_level50()

    # Debug = return preview (NO email sent)
    if debug:
        return {
            "status": "run_completed_debug",
            "summary": result["summary"],
            "sections": result["sections"],
        }

    # PRODUCTION MODE = send email
    if MODE == "production":
        send_email(result["summary"], result["sections"])
        return {"status": "email_sent"}

    return {"status": "run_completed_no_email"}
