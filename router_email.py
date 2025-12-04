# router_email.py
# Manual reminder route — calls the existing /run engine (backend_api.run_engine_api)
# and sends a single email to sales@ventilengineering.com

from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
import traceback

# Use the actual working engine endpoint function from backend_api (your /run endpoint)
try:
    from backend_api import run_engine_api
except Exception as e:
    raise ImportError("Failed to import run_engine_api from backend_api. "
                      "Ensure backend_api.py exists and defines run_engine_api().") from e

# Use your existing send_email wrapper
try:
    from email_sender import send_email
except Exception:
    raise ImportError("Failed to import send_email from email_sender. Ensure email_sender.send_email exists.")

router = APIRouter()
SALES_RECIPIENT = "sales@ventilengineering.com"


def build_email_from_engine_result(result: dict) -> str:
    """Create a readable plain-text summary email from engine result dict."""
    lines = []
    lines.append("Level-50 Manual Reminder — RFQ Follow-up")
    lines.append("")
    summary = result.get("summary", {})
    if summary:
        lines.append("Summary:")
        for k in ("HIGH", "MEDIUM", "LOW", "OVERDUE", "NOACTION", "SKIP"):
            if k in summary:
                lines.append(f"  {k}: {summary.get(k)}")
        lines.append("")

    level51 = result.get("level51") or {}
    if level51:
        lines.append("Data health (level51):")
        for k in ("total_raw_rows", "kept_rows", "autofixed_rows", "rows_with_invalid_fields", "skipped_np"):
            if k in level51:
                lines.append(f"  {k}: {level51.get(k)}")
        lines.append("")

    sections = result.get("sections") or {}
    actionable = []
    # prefer HIGH and OVERDUE
    for key in ("HIGH", "OVERDUE"):
        for r in sections.get(key, [])[:6]:
            rfq = r.get("RFQ NO") or r.get("RFQ_NO") or r.get("RFQ No") or ""
            cust = r.get("CUSTOMER NAME") or r.get("CUSTOMER") or ""
            due = r.get("DUE DATE") or r.get("DUE_DATE") or ""
            actionable.append((key, rfq, cust, due))

    # fallback: take first few across sections
    if not actionable:
        for sec, items in sections.items():
            for r in items[:6]:
                rfq = r.get("RFQ NO") or r.get("RFQ_NO") or ""
                cust = r.get("CUSTOMER NAME") or ""
                due = r.get("DUE DATE") or ""
                actionable.append((sec, rfq, cust, due))

    if actionable:
        lines.append("Top actionable RFQs (sample):")
        for sec, rfq, cust, due in actionable[:6]:
            lines.append(f" - [{sec}] RFQ: {rfq} | Cust: {cust} | Due: {due}")
        lines.append("")
    else:
        lines.append("No actionable RFQs found for manual reminder.")
        lines.append("")

    lines.append("If an item is already handled, ignore this email.")
    lines.append("")
    lines.append("-- Automation System")
    return "\n".join(lines)


@router.post("/manual-reminder")
def manual_reminder():
    """
    Manual one-click reminder:
    - Calls backend_api.run_engine_api() to run the engine
    - Sends the compiled summary ONLY to sales@ventilengineering.com
    """
    try:
        # Call the existing /run function. It returns a dict (the same shape your /run returns).
        engine_result = run_engine_api()

        # If backend_api.run_engine_api returned an HTTPException or similar, normalize it
        if isinstance(engine_result, HTTPException):
            raise engine_result

        # Build email body
        body = build_email_from_engine_result(engine_result)

        # Subject
        subject = "Manual Reminder — RFQ Follow-up"

        # Send email (only to SALES_RECIPIENT)
        send_result = send_email(SALES_RECIPIENT, subject, body)

        return {
            "status": "sent",
            "recipient": SALES_RECIPIENT,
            "send_result": send_result,
            "engine_summary": engine_result.get("summary"),
            "level51": engine_result.get("level51")
        }

    except HTTPException as httpe:
        # re-raise HTTPExceptions to preserve status
        raise httpe
    except Exception as ex:
        tb = traceback.format_exc()
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"manual_reminder_failed: {str(ex)}\n{tb}")
