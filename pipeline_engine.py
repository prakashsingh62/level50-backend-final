# ------------------------------------------------------------
# LEVEL-70 PIPELINE ENGINE — ENTERPRISE EDITION
# ------------------------------------------------------------
# Includes:
#   ✔ Turbo Engine
#   ✔ Plugin Framework
#   ✔ Auto-Recovery Engine
#   ✔ Smart Throttle
#   ✔ Anti-Corruption Guard
#   ✔ AI Safety Failover
#   ✔ Auto-Optimizer
#   ✔ Autonomous Behavior Engine
#   ✔ Approval Gate
#   ✔ Level-80 Strict Mode (Post-Update Snapshot)
# ------------------------------------------------------------

from rules_config import rules
from plugins.plugin_loader import load_plugin

from utils.turbo_pipeline import turbo_pipeline, turbo_event
from utils.auto_recovery import auto_recovery
from utils.smart_throttle import smart_throttle
from utils.anti_corruption import AntiCorruptionGuard
from utils.ai_failover import ai_failover
from utils.auto_optimizer import auto_optimizer
from utils.autonomous_behavior import autonomous
from utils.sheet_updater import update_rfq_row
from utils.heartbeat import log

from utils.matcher import find_matching_row
from utils.status_engine import compute_status, compute_followup
from utils.vendor_router import check_vendor_query

from strict_audit_logger import log_post_update_snapshot


# ------------------------------------------------------------
# LOAD OPTIONAL PLUGINS (SAFE)
# ------------------------------------------------------------
plugin_status = load_plugin("status_plugin")
plugin_vendor = load_plugin("vendor_plugin")
plugin_followup = load_plugin("followup_plugin")


# ------------------------------------------------------------
# STEP-3 MODULE — MULTI-STAGE DECISION LAYER
# ------------------------------------------------------------
class MultiStageDecisionLayer:

    def __init__(self):
        self.allowed_actions = {
            "SEND_VENDOR_REMINDER",
            "SEND_CLIENT_REMINDER",
            "SEND_CLARIFICATION_MAIL",
            "SEND_UID_QUERY_MAIL",
            "SKIP"
        }

    def classify_situation(self, rfq):
        if rfq.get("uid_pending"):
            return "UID_VENDOR_QUERY"
        if rfq.get("clarification_pending"):
            return "CLARIFICATION_REQUIRED"
        if rfq.get("vendor_pending"):
            return "VENDOR_PENDING"
        if rfq.get("client_followup_due"):
            return "CLIENT_FOLLOWUP_DUE"
        if rfq.get("pack7_signal") == "DELAY_RISK_HIGH":
            return "DELAY_RISK_HIGH"
        return "NO_ACTION"

    def select_action(self, situation):
        return {
            "UID_VENDOR_QUERY": "SEND_UID_QUERY_MAIL",
            "CLARIFICATION_REQUIRED": "SEND_CLARIFICATION_MAIL",
            "VENDOR_PENDING": "SEND_VENDOR_REMINDER",
            "CLIENT_FOLLOWUP_DUE": "SEND_CLIENT_REMINDER",
            "DELAY_RISK_HIGH": "SEND_VENDOR_REMINDER",
        }.get(situation, "SKIP")

    def arbitrate(self, rfq, action):
        if rfq.get("uid_pending"):
            return "SEND_UID_QUERY_MAIL"
        if rfq.get("clarification_pending"):
            return "SEND_CLARIFICATION_MAIL"
        if rfq.get("vendor_pending"):
            return "SEND_VENDOR_REMINDER"
        if rfq.get("client_followup_due"):
            return "SEND_CLIENT_REMINDER"
        return action

    def enforce_guardrails(self, rfq, action):
        if action not in self.allowed_actions:
            return "SKIP"
        if rfq.get("already_notified"):
            return "SKIP"
        if not rfq.get("rfq_id"):
            return "SKIP"
        return action

    def decide(self, rfq):
        situation = self.classify_situation(rfq)
        action = self.enforce_guardrails(
            rfq,
            self.arbitrate(rfq, self.select_action(situation))
        )
        return {
            "rfq_id": rfq.get("rfq_id"),
            "situation": situation,
            "action": action,
            "reason": f"Decision based on {situation}"
        }


# ------------------------------------------------------------
# STEP-4 MODULE — ADAPTIVE MAIL COMPOSER
# ------------------------------------------------------------
class AdaptiveMailComposer:

    def compose(self, ai_output: dict):
        action = ai_output.get("decision", {}).get("action", "SKIP")

        if action == "SEND_VENDOR_REMINDER":
            return self.build_vendor_reminder(ai_output)
        if action == "SEND_CLIENT_REMINDER":
            return self.build_client_reminder(ai_output)
        if action == "SEND_CLARIFICATION_MAIL":
            return self.build_clarification_mail(ai_output)
        if action == "SEND_UID_QUERY_MAIL":
            return self.build_uid_query_mail(ai_output)

        return {"type": "skip", "subject": None, "body": None}

    def build_vendor_reminder(self, ai):
        return {
            "type": "vendor_reminder",
            "subject": f"Reminder: Pending RFQ {ai.get('rfq')}",
            "body": f"UID: {ai.get('uid')}"
        }

    def build_client_reminder(self, ai):
        return {
            "type": "client_followup",
            "subject": f"Follow-up RFQ {ai.get('rfq')}",
            "body": "Client follow-up required"
        }

    def build_clarification_mail(self, ai):
        return {
            "type": "clarification",
            "subject": f"Clarification Required — RFQ {ai.get('rfq')}",
            "body": "Clarification pending"
        }

    def build_uid_query_mail(self, ai):
        return {
            "type": "uid_query",
            "subject": f"UID Query — {ai.get('uid')}",
            "body": "UID clarification required"
        }


# ------------------------------------------------------------
# MAIN PIPELINE ENGINE
# ------------------------------------------------------------
class Level70Pipeline:

    def run_pipeline_internal(self, email_data: dict):

        smart_throttle.limit_rate()

        with turbo_pipeline():
            turbo_event("Pipeline STARTED")

            ai_output = ai_failover.validate(email_data.get("ai_output", {}))
            confidence = autonomous.compute_confidence(ai_output)

            rfq = ai_output.get("rfq")
            uid = ai_output.get("uid")

            matched_row = auto_optimizer.optimize_match(rfq, uid) \
                or find_matching_row(rfq, uid)

            if matched_row is None:
                return {"status": "no_match", "rfq": rfq, "uid": uid}

            status = plugin_status(ai_output, rules) if plugin_status else compute_status(ai_output)
            ai_output["vendor_status"] = status

            vendor_info = plugin_vendor(ai_output, rules) if plugin_vendor else check_vendor_query(email_data, ai_output)
            if vendor_info.get("is_vendor_query"):
                return {
                    "status": "vendor_query_detected",
                    "requires_approval": True,
                    "matched_row": matched_row,
                    "ai_output": ai_output,
                }

            followup = plugin_followup(ai_output, rules) if plugin_followup else compute_followup(ai_output)
            ai_output["followup_date"] = followup

            decision = MultiStageDecisionLayer().decide({
                "rfq_id": rfq,
                "uid_pending": ai_output.get("uid_pending"),
                "clarification_pending": ai_output.get("clarification_pending"),
                "vendor_pending": ai_output.get("vendor_pending"),
                "client_followup_due": ai_output.get("client_followup_due"),
                "pack7_signal": ai_output.get("pack7_signal"),
                "already_notified": ai_output.get("already_notified"),
            })

            ai_output["decision"] = decision
            ai_output["mail"] = AdaptiveMailComposer().compose(ai_output)

            auto_optimizer.apply()

            return {
                "status": "approval_required",
                "matched_row": matched_row,
                "ai_output": ai_output
            }

    def run(self, email_data: dict):
        return auto_recovery.safe_run(self.run_pipeline_internal, email_data)


# ------------------------------------------------------------
# FINAL APPROVED UPDATE (GOOGLE SHEET WRITE)
# LEVEL-80 STEP-4 HOOK APPLIED
# ------------------------------------------------------------
def apply_approved_update(row_index: int, ai_output: dict):

    from utils.sheet_updater import sheet_obj

    guard = AntiCorruptionGuard()

    safe_values = ai_output.get("safe_update_values")
    if not safe_values:
        return {
            "status": "blocked",
            "reason": "Missing safe_update_values — Step-5 payload unavailable."
        }

    result = guard.safe_update(
        updater_fn=update_rfq_row,
        sheet_obj=sheet_obj,
        row_index=row_index,
        update_values=safe_values,
    )

    # 🔒 LEVEL-80 STEP-4: POST-UPDATE SNAPSHOT
    if result.get("status") == "success":
        log_post_update_snapshot(
            rows_written=1,
            affected_rows=[row_index],
            updater="LEVEL-80-STRICT-MODE"
        )

    return result
