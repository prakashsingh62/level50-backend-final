# ------------------------------------------------------------
# PIPELINE ENGINE — LEVEL 70 / PHASE 11
# FINAL, AUDIT-ISOLATED, PROD-SAFE
# ------------------------------------------------------------

from sheet_reader import read_rfqs
from classify import classify_rfq
from sheet_writer import write_sheet

class Level70Pipeline:
    def run(self, payload=None):
        payload = payload or {}

        # -------------------------------
        # PING MODE (NO SIDE EFFECTS)
        # -------------------------------
        if payload.get("mode") == "ping":
            return {
                "status": "OK",
                "mode": "PING",
                "message": "Pipeline reachable"
            }

        # -------------------------------
        # READ RFQs
        # -------------------------------
        try:
            rfqs = read_rfqs(payload)
        except Exception as e:
            return {
                "status": "FAILED",
                "processed": 0,
                "error": f"read_rfqs_failed: {str(e)}"
            }

        if not rfqs:
            return {
                "status": "NO_OP",
                "processed": 0,
                "reason": "No RFQs resolved"
            }

        if isinstance(rfqs, dict):
            rfqs = [rfqs]

        # -------------------------------
        # PROCESS RFQs (NO AUDIT HERE)
        # -------------------------------
        processed = 0

        for rfq in rfqs:
            try:
                classify_rfq(rfq)
                write_sheet(rfq)
                processed += 1
            except Exception:
                # skip single RFQ failure
                continue

        # -------------------------------
        # FINAL RETURN
        # -------------------------------
        return {
            "status": "OK",
            "processed": processed
        }

# REQUIRED SINGLETON
pipeline = Level70Pipeline()
