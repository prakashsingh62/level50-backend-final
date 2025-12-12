from utils.matcher import find_matching_row
from utils.status_engine import classify_status
from utils.followup_engine import calculate_followup_date
from utils.vendor_router import vendor_query_router
from utils.sheet_updater import update_rfq_row
from email_builder import prepare_email


# ---------------------------------------------------------------------
# LEVEL-70 RULE:
#
# If an NP row somehow passes Step-3 matching (extremely rare),
# automation MUST STOP at Step-7. NP rows are excluded from
# automation but remain fully editable manually in Google Sheets.
#
# - Automation NEVER sends emails for NP rows
# - Automation NEVER updates NP rows
# - Manual sheet edits are ALWAYS allowed for NP rows
# ---------------------------------------------------------------------


def run_full_pipeline(ai_output: dict, sheet_rows: list, thread_emails: list):

    # -----------------------------------------------------
    # STEP 3 — MATCH ROW
    # -----------------------------------------------------

    step3 = find_matching_row(
        rows=sheet_rows,
        input_rfq=ai_output.get("rfq", ""),
        input_uid=ai_output.get("uid", "")
    )

    if step3["status"] != "success":
        return {
            "pipeline_stopped": True,
            "error": "Row not found or multiple matches",
            "step3": step3
        }

    matched_row_index = step3["row"]
    matched_sheet_row = sheet_rows[matched_row_index - 1]

    # -----------------------------------------------------
    # STEP-7 HARD SKIP FOR NP ROWS
    # -----------------------------------------------------
    try:
        cp_value = matched_sheet_row[11].strip().upper()
    except:
        cp_value = ""

    if cp_value == "NP":
        return {
            "pipeline_stopped": True,
            "error": "NP row skipped (manual editing allowed)",
            "reason": "Automation cannot process NP rows",
            "step3": step3
        }

    # Extract needed fields
    vendor_name = matched_sheet_row[21].strip() if len(matched_sheet_row) > 21 else ""

    matched_row = {
        "row": matched_row_index,
        "rfq": ai_output.get("rfq"),
        "uid": ai_output.get("uid"),
        "vendor_name": vendor_name
    }

    # -----------------------------------------------------
    # STEP 5 — STATUS ENGINE
    # -----------------------------------------------------

    status = classify_status(ai_output.get("vendor_status_text", ""))

    # -----------------------------------------------------
    # STEP 5B — VENDOR ROUTER → CONFIRMATION GATE
    # -----------------------------------------------------

    vendor_router_result = vendor_query_router(
        ai_text=ai_output.get("customer_query", ""),
        matched_row=matched_row,
        thread_emails=thread_emails
    )

    if vendor_router_result.get("requires_vendor"):
        return {
            "pipeline_stopped": True,
            "awaiting_confirmation": True,
            "message": "Vendor query detected — needs SEND NOW approval.",
            "step3": step3,
            "step5": status,
            "vendor_router": vendor_router_result
        }

    # -----------------------------------------------------
    # STEP 6 — FOLLOW-UP DATE
    # -----------------------------------------------------

    try:
        val = float(ai_output.get("value", 0))
    except:
        val = 0.0

    followup_date = calculate_followup_date(status=status, rfq_value=val)

    # -----------------------------------------------------
    # STEP 4 PREPARATION — UPDATE PAYLOAD
    # -----------------------------------------------------

    update_payload = {
        "vendor_status": status,
        "quotation_date": ai_output.get("quotation_date", ""),
        "remarks": ai_output.get("remarks", ""),
        "followup_date": followup_date
    }

    return {
        "pipeline_stopped": False,
        "awaiting_confirmation": False,
        "step3": step3,
        "step5": status,
        "vendor_router": vendor_router_result,
        "update_payload": update_payload,
        "final_output": {
            "row_to_update": matched_row_index,
            "status": status,
            "followup_date": followup_date,
            "safe_to_update": True
        }
    }


# ---------------------------------------------------------------------
# FINALIZER — EXECUTED ONLY after human approves
# ---------------------------------------------------------------------

def finalize_update_after_confirmation(row_index: int, update_payload: dict):
    return update_rfq_row(
        matched_row=row_index,
        ai_output=update_payload
    )
