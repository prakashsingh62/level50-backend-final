"""
classify.py
Level-80 RFQ Classifier
Safe adapter for pipeline_engine
"""

from typing import Dict


def classify_rfq(rfq: Dict) -> Dict:
    """
    Classifies RFQ and decides actions.

    RULES:
    - Must NEVER raise import error
    - Must NEVER return None
    - Must ALWAYS return rfq dict
    """

    if not isinstance(rfq, dict):
        # Hard safety: pipeline must not crash
        return {
            "rfq_no": None,
            "uid": None,
            "customer": None,
            "vendor": None,
            "send_mail": False,
        }

    # -------------------------------------------------
    # DEFAULTS (STRICT MODE)
    # -------------------------------------------------
    rfq.setdefault("send_mail", False)
    rfq.setdefault("priority", "NORMAL")
    rfq.setdefault("status", "OK")

    # -------------------------------------------------
    # BASIC REAL LOGIC (NOT DUMMY)
    # -------------------------------------------------
    vendor = (rfq.get("vendor") or "").strip()
    customer = (rfq.get("customer") or "").strip()

    # If essential data missing → do NOT send mail
    if not vendor or not customer:
        rfq["send_mail"] = False
        rfq["status"] = "INVALID_RFQ"
        return rfq

    # Example real condition:
    # Future me yahin AI / rules / scoring aayega
    if rfq.get("priority") == "HIGH":
        rfq["send_mail"] = True

    return rfq
