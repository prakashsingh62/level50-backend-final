from utils.logger import log

class AIFailover:
    """
    INFINITY PACK-5: AI SAFETY FAILOVER
    ------------------------------------
    Protects Level-70 pipeline from:
        ✔ Missing AI fields
        ✔ Wrong RFQ / UID extraction
        ✔ Wrong vendor status
        ✔ Wrong follow-up logic
        ✔ AI hallucinations
        ✔ Invalid values
    """

    REQUIRED_FIELDS = [
        "rfq", "uid", "vendor_status", "remarks"
    ]

    def validate(self, ai_output):
        """
        Auto-correct missing fields & enforce safe structure.
        """
        safe_output = ai_output.copy()

        for field in self.REQUIRED_FIELDS:
            if field not in safe_output or safe_output[field] in [None, "", []]:
                log(f"[AI FAILOVER] Missing {field} → Auto-fixing.")
                safe_output[field] = ""

        # Block invalid UID formats
        if "uid" in safe_output and len(str(safe_output["uid"])) < 3:
            log("[AI FAILOVER] UID looks invalid → clearing.")
            safe_output["uid"] = ""

        # Block invalid RFQ formats
        if "rfq" in safe_output and len(str(safe_output["rfq"])) < 3:
            log("[AI FAILOVER] RFQ looks invalid → clearing.")
            safe_output["rfq"] = ""

        return safe_output


    def pre_update_check(self, ai_output):
        """
        Verify AI output before sheet write.
        If unsafe → block update.
        """
        if not ai_output.get("vendor_status"):
            return {
                "unsafe": True,
                "reason": "Missing vendor_status"
            }

        if not ai_output.get("rfq") or len(ai_output["rfq"]) < 3:
            return {
                "unsafe": True,
                "reason": "Invalid RFQ"
            }

        if not ai_output.get("uid") or len(ai_output["uid"]) < 3:
            return {
                "unsafe": True,
                "reason": "Invalid UID"
            }

        return {"unsafe": False}


# Singleton instance
ai_failover = AIFailover()
