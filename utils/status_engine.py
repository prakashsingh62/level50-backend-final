# ------------------------------------------------------------
# STATUS ENGINE — STABLE BASE VERSION
# ------------------------------------------------------------

def compute_status(ai_output: dict) -> str:
    """
    Determines vendor status based on AI output.
    MUST exist — pipeline_engine depends on this.
    """
    if ai_output.get("vendor_pending"):
        return "VENDOR_PENDING"

    if ai_output.get("clarification_pending"):
        return "CLARIFICATION_PENDING"

    if ai_output.get("uid_pending"):
        return "UID_PENDING"

    return "OK"


def compute_followup(ai_output: dict):
    """
    Determines follow-up date / need.
    """
    if ai_output.get("client_followup_due"):
        return "FOLLOWUP_REQUIRED"

    return None
