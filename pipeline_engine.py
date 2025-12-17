# ------------------------------------------------------------
# PIPELINE ENGINE — LEVEL-70 + PHASE-11 READY
# ------------------------------------------------------------

from logger import get_logger
from utils.status_engine import compute_status, compute_followup
from utils.vendor_router import check_vendor_query
from utils.auto_recovery import auto_recovery

logger = get_logger("PIPELINE_ENGINE")


class Level70Pipeline:
    def __init__(self):
        logger.info("Level70Pipeline initialized")

    # --------------------------------------------------------
    # INTERNAL CORE LOGIC
    # --------------------------------------------------------
    def run_pipeline_internal(self, payload: dict):
        """
        Actual pipeline logic.
        This MUST raise exceptions if something is wrong.
        AutoRecovery will catch it.
        """

        ai_output = payload.get("ai_output")
        if not ai_output:
            raise ValueError("ai_output missing in payload")

        rfq = ai_output.get("rfq")
        uid = ai_output.get("uid")

        if not rfq or not uid:
            raise ValueError("rfq / uid missing in ai_output")

        logger.info(f"Processing RFQ={rfq}, UID={uid}")

        # 1️⃣ Vendor query detection
        vendor_query = check_vendor_query(ai_output)

        # 2️⃣ Status computation
        status = compute_status(ai_output)

        # 3️⃣ Follow-up logic
        followup = compute_followup(ai_output)

        decision = ai_output.get("decision") or status

        return {
            "status": "ok",
            "rfq": rfq,
            "uid": uid,
            "decision": decision,
            "vendor_query": vendor_query,
            "followup": followup
        }

    # --------------------------------------------------------
    # PUBLIC SAFE ENTRY (LEVEL-70)
    # --------------------------------------------------------
    def run(self, payload: dict):
        """
        SAFE execution with auto-recovery.
        """
        return auto_recovery.safe_run(
            self.run_pipeline_internal,
            payload
        )

    # --------------------------------------------------------
    # PHASE-11 ENTRY (OPTIONAL FUTURE USE)
    # --------------------------------------------------------
    def run_phase11(self, payload: dict):
        """
        Phase-11 wrapper.
        Right now delegates to same pipeline.
        """
        return self.run(payload)


# ------------------------------------------------------------
# APPROVAL APPLY (LEGACY — DO NOT TOUCH)
# ------------------------------------------------------------
def apply_approved_update(row, ai_output):
    logger.info("Applying approved update")

    if not row or not ai_output:
        return {
            "status": "error",
            "reason": "row / ai_output missing"
        }

    # Stub — real sheet update already exists elsewhere
    return {
        "status": "approved",
        "row": row,
        "ai_output": ai_output
    }
