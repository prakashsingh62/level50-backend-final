# router_email.py
# Manual reminder route (one-click) — sends only to sales@ventilengineering.com
# Drop this file into your repo (replace existing router_email.py) and deploy.

from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
import os
import traceback
from typing import Any, Dict

# These modules should already exist in your project
# - process_sheet should run the same engine as /run (non-debug) and return a dict
# - send_email(to, subject, body) should send email via SendGrid and return a status/result
try:
    from logic_engine import process_sheet            # function that runs sheet logic
except Exception:
    # fallback import path (in case you have different layout)
    from logic_engine import process_sheet  # keep as-is; adjust only if module name differs

try:
    from email_sender import send_email              # function to send email (SendGrid wrapper)
except Exception:
    # If your send_email lives elsewhere, update this import accordingly
    from email_sender import send_email

router = APIRouter()

SALES_RECIPIENT = "sales@ventilengineering.com"

def build_email_from_engine_result(result: Dict[str, Any]) -> str:
    """
    Convert engine result into a plain-text email body.
    Keep it concise but include key counts and top items.
    """
    lines = []
    lines.append("Level-50 Manual Reminder — RFQ Follow-up")
    lines.append("")
    # Basic summary
    summary = result.get("summary") or {}
    if summary:
        lines.append("Summary:")
        for k in ["HIGH", "MEDIUM", "LOW", "OVERDUE", "NOACTION", "SKIP"]:
            if k in summary:
                lines.append(f"  {k}: {summary.get(k)}")
        lines.append("")

    # Level51 diagnostics if present
    level51 = result.get("level51")
    if level51:
        lines.append("Data Health (level51):")
        for k in ["total_raw_rows", "kept_rows", "autofixed_rows", "rows_with_invalid_fields", "skipped_np"]:
            if k in level51:
                lines.append(f"  {k}: {level51.get(k)}")
        lines.append("")

    # Add a short list of top actionable RFQs if present (limit to 6)
    sections = result.get("sections") or {}
    actionable = []
    # prefer HIGH, OVERDUE, VENDOR PENDING (if exists)
    for bucket in ("HIGH", "OVERDUE", "VENDOR PENDING", "VENDOR_PENDING", "Vendor Pending"):
        items = sections.get(bucket) or []
        for r in items:
            actionable.append({
                "priority": bucket,
                "rfq": r.get("RFQ NO") or r.get("RFQ_NO") or r.get("RFQ No") or r.get("RFQ No", ""),
                "customer": r.get("CUSTOMER NAME") or r.get("CUSTOMER") or "",
                "due": r.get("DUE DATE") or r.get("DUE_DATE") or "",
                "note": r.get("NOTE") or r.get("INQUIRY SENT ON") or ""
            })
    # fallback: if no named buckets, take first few from any section
    if not actionable:
        for k, items in sections.items():
            for r in items[:6]:
                actionable.append({
                    "priority": k,
                    "rfq": r.get("RFQ NO") or r.get("RFQ_NO") or "",
                    "customer": r.get("CUSTOMER NAME") or "",
                    "due": r.get("DUE DATE") or "",
                    "note": ""
                })
    if actionable:
        lines.append("Top actionable RFQs (sample):")
        for a in actionable[:6]:
            lines.append(f" - [{a['priority']}] RFQ: {a['rfq']} | Cust: {a['customer']} | Due: {a['due']} | Note: {a['note']}")
        lines.append("")
    else:
        lines.append("No actionable RFQs found for manual reminder.")
        lines.append("")

    lines.append("If an item is already handled, ignore this email.")
    lines.append("")
    lines.append("-- Automation System")
    return "\n".join(lines)


@router.post("/manual-reminder")
async def manual_reminder():
    """
    Manual one-click reminder (sends only to sales@ventilengineering.com).
    Runs the same engine as the scheduled job (non-debug).
    """
    try:
        # 1) Run the sheet processing engine (non-debug)
        # process_sheet should return a dict like your /run response
        result = process_sheet(debug=False)

        # 2) Build the email body
        body = build_email_from_engine_result(result)

        # 3) Subject line
        subject = "Manual Reminder — RFQ Follow-up"

        # 4) Send ONLY to sales@ventilengineering.com
        to_email = SALES_RECIPIENT

        # 5) Call your send_email wrapper
        send_result = send_email(to_email, subject, body)

        # 6) Return structured response
        return {
            "status": "sent",
            "recipient": to_email,
            "send_result": send_result,
            "engine_summary": result.get("summary"),
            "level51": result.get("level51")
        }

    except Exception as ex:
        # return traceback (safe short form) to help debugging in logs/response
        tb = traceback.format_exc()
        # Log can be expanded if you have a logger
        return HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                             detail=f"manual_reminder_failed: {str(ex)}\n{tb}")
