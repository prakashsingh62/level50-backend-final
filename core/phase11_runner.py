# core/phase11_runner.py
# ------------------------------------------------------------
# PHASE-11 RUNNER — FINAL (WITH GOOGLE SHEET AUDIT)
# ------------------------------------------------------------

import os
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

from core.contracts import TraceContext, PipelineResult, AuditEvent
from core.audit_bus import emit_audit
from pipeline_engine import Level70Pipeline

from utils.time_ist import ist_date, ist_time
from utils.audit_logger import append_audit_with_alert

# ------------------------------------------------------------
# PIPELINE
# ------------------------------------------------------------
pipeline = Level70Pipeline()

# ------------------------------------------------------------
# ENV (RAILWAY SAFE)
# ------------------------------------------------------------
AUDIT_SHEET_ID = os.environ["AUDIT_SHEET_ID"]
AUDIT_TAB = os.environ.get("AUDIT_TAB", "audit_log")
SHEET_NAME = os.environ.get("TAB_NAME", "RFQ TEST SHEET")

# ------------------------------------------------------------
# GOOGLE CREDS (FROM ENV)
# ------------------------------------------------------------
_creds = Credentials.from_service_account_info(
    json.loads(os.environ["CLIENT_SECRET_JSON"]),
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
_svc = build("sheets", "v4", credentials=_creds)

# ------------------------------------------------------------
# INTERNAL: GOOGLE SHEET AUDIT (PER-COLUMN)
# ------------------------------------------------------------
def _audit_after_update(row_number: int, ai_output: dict):
    rfq_no = ai_output.get("rfq_no", "")
    uid_no = ai_output.get("uid_no", "")

    # Map ONLY fields that are actually updated in Phase-11
    col_map = [
        ("Vendor Status", ai_output.get("vendor_status")),
        ("Quotation Date", ai_output.get("quotation_date")),
        ("Remarks", ai_output.get("remarks")),
        ("Followup Date", ai_output.get("followup_date")),
    ]

    for col_name, new_val in col_map:
        if not new_val:
            continue

        audit_row = [
            f"{ist_date()} {ist_time()}",  # TIMESTAMP_IST
            ist_date(),                    # DATE
            ist_time(),                    # TIME
            rfq_no,                        # RFQ_NO
            uid_no,                        # UID_NO
            SHEET_NAME,                    # SHEET_NAME
            SHEET_NAME,                    # TAB_NAME
            row_number,                    # ROW_NUMBER
            col_name,                      # COLUMN_NAME
            "",                             # OLD_VALUE (turbo/no-read)
            str(new_val),                  # NEW_VALUE
            "UPDATE",                      # ACTION_TYPE
            "PHASE11",                     # TRIGGER_SOURCE
            "LEVEL_80_ENGINE",             # ACTOR
            "SUCCESS",                     # STATUS
            "AUTO_UPDATE",                 # REASON
            "REQ_AUTO",                    # REQUEST_ID
            "RUN_AUTO",                    # RUN_ID
        ]

        append_audit_with_alert(
            creds=_creds,
            sheets_service=_svc,
            spreadsheet_id=AUDIT_SHEET_ID,
            tab_name=AUDIT_TAB,
            audit_row=audit_row,
            run_id="RUN_AUTO",
            request_id="REQ_AUTO",
        )

# ------------------------------------------------------------
# ENTRY POINT — ACTUAL PRODUCTION PATH
# ------------------------------------------------------------
def run_phase11(email_payload: dict) -> PipelineResult:
    ctx = TraceContext.create()

    emit_audit(AuditEvent(
        trace_id=ctx.trace_id,
        stage="PIPELINE_START",
        payload=email_payload,
        timestamp=ctx.timestamp
    ))

    # -------------------------------
    # RUN PIPELINE (PHASE-11)
    # -------------------------------
    result = pipeline.run(email_payload)

    # -------------------------------
    # GOOGLE SHEET AUDIT (ONLY IF UPDATE HAPPENED)
    # EXPECTED FROM pipeline.run():
    # result = {
    #   "status": "...",
    #   "row": <row_number>,
    #   "ai_output": {...}
    # }
    # -------------------------------
    try:
        row_number = result.get("row")
        ai_output = result.get("ai_output", {})
        if row_number and ai_output:
            _audit_after_update(row_number, ai_output)
    except Exception as _e:
        # DO NOT BREAK PIPELINE ON AUDIT FAILURE
        pass

    emit_audit(AuditEvent(
        trace_id=ctx.trace_id,
        stage="PIPELINE_END",
        payload=result,
        timestamp=ctx.timestamp
    ))

    return PipelineResult(
        status=result.get("status"),
        trace_id=ctx.trace_id,
        data=result
    )
