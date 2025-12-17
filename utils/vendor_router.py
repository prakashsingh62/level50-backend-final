# ------------------------------------------------------------
# utils/vendor_router.py
# Vendor Query Detection & Routing (SAFE + FUTURE-PROOF)
# ------------------------------------------------------------

from typing import Dict, Any, Optional
from logger import get_logger

log = get_logger(__name__)

# ------------------------------------------------------------
# MAIN ENTRY
# ------------------------------------------------------------

def check_vendor_query(ai_output: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Detects whether vendor clarification / follow-up is required.

    SAFE GUARANTEES:
    - Never crashes if ai_output is missing
    - Auto-Recovery compatible
    - Read-only (no sheet write, no approval)

    Returns structured decision dict.
    """

    # ----------------------------
    # HARD SAFETY GUARD
    # ----------------------------
    if not ai_output or not isinstance(ai_output, dict):
        log.warning("Vendor check skipped: ai_output missing or invalid")
        return {
            "status": "skipped",
            "engine": "vendor_router",
            "reason": "ai_output missing or invalid"
        }

    # ----------------------------
    # REQUIRED FIELDS
    # ----------------------------
    rfq = ai_output.get("rfq")
    uid = ai_output.get("uid")

    if not rfq or not uid:
        log.warning("Vendor check skipped: rfq / uid missing")
        return {
            "status": "skipped",
            "engine": "vendor_router",
            "reason": "rfq or uid missing"
        }

    # ----------------------------
    # DECISION FLAGS
    # ----------------------------
    vendor_pending = bool(ai_output.get("vendor_pending"))
    clarification_needed = bool(ai_output.get("vendor_query"))
    followup_due = bool(ai_output.get("client_followup_due"))

    # ----------------------------
    # NO ACTION CASE
    # ----------------------------
    if not vendor_pending and not clarification_needed:
        log.info(f"No vendor action required for RFQ={rfq}")
        return {
            "status": "ok",
            "engine": "vendor_router",
            "action": "none",
            "rfq": rfq,
            "uid": uid
        }

    # ----------------------------
    # ACTION REQUIRED
    # ----------------------------
    action = "vendor_followup" if vendor_pending else "vendor_clarification"

    log.info(
        f"Vendor action detected | RFQ={rfq} | UID={uid} | action={action}"
    )

    return {
        "status": "action_required",
        "engine": "vendor_router",
        "action": action,
        "rfq": rfq,
        "uid": uid,
        "details": {
            "vendor_pending": vendor_pending,
            "clarification_needed": clarification_needed,
            "client_followup_due": followup_due
        }
    }
