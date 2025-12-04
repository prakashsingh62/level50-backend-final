from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
import traceback

# Corrected import
from sheet_reader import read_sheet
from logic_engine import process_sheet
from sheet_writer import write_updates

# Email sender (SendGrid wrapper)
from email_sender import send_email

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
                lines.append(f"  {k}: {summary[k]}")
        lines.append("")

    level51 = result.get("level51", {})
    if level51:
        lines.append("Data Health:")
        for k in ("total_raw_rows", "kept_rows", "autofixed_rows", "rows_with_invalid_fields", "skipped_np"):
            if k in level51:
                lines.append(f"  {k}: {level51[k]}")
        lines.append("")

    sections = result.get("sections", {})
    actionable = []

    # Prefer HIGH and OVERDUE rows
    for key in ("HIGH", "OVERDUE"):
        for r in sections.get(key, [])[:6]:
            actionable.append((key, r.get("RFQ NO"), r.get("CUSTOMER NAME"), r.get("DUE DATE")))

    if actionable:
        lines.append("Top actionable RFQs:")
        for sec, rfq, cust, due in actionable:
            lines.append(f" - [{sec}] RFQ: {rfq} | Cust: {cust} | Due: {due}")
        lines.append("")
    else:
        lines.append("No actionable RFQs found.")
        lines.append("")

    lines.append("This is a manual reminder.")
    lines.append("-- Automation System")
    return "\n".join(lines)


@router.post("/manual-reminder")
def manual_reminder():
    """
    Manual one-click reminder:
    - Runs Level-50 engine directly (no backend_api import)
    - Sends email to sales@ventilengineering.com only
    """
    try:
        rows = read_sheet()          # FIXED HERE
        processed, engine_meta = process_sheet(rows)

        # Write results back to Google Sheet
        if processed:
            write_updates(processed)

        # Build email
        body = build_email_from_engine_result(engine_meta)
        subject = "Manual Reminder — RFQ Follow-up"

        # Send email
        send_result = send_email(SALES_RECIPIENT, subject, body)

        return {
            "status": "sent",
            "recipient": SALES_RECIPIENT,
            "engine_summary": engine_meta.get("summary"),
            "level51": engine_meta.get("level51"),
            "send_result": send_result
        }

    except Exception as ex:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"manual_reminder_failed: {str(ex)}\n{tb}"
        )
