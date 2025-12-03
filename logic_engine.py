# logic_engine.py
# Level-50 Logic Engine (Final, Stable)

def classify_row(r):
    """
    Your existing classification logic.
    This function MUST always return one of:
    "HIGH", "MEDIUM", "LOW", "VENDOR_PENDING",
    "CLARIFICATION", "QUOTATION_RECEIVED",
    "OVERDUE", "SKIP", "INVALID"
    """

    # --- BASIC VALIDATION ---
    if not r or not isinstance(r, dict):
        return "INVALID"

    # Skip rows where concern person = NP
    if str(r.get("CONCERN PERSON", "")).strip().upper() == "NP":
        return "SKIP"

    # Empty RFQ means skip
    if not str(r.get("RFQ NO", "")).strip():
        return "SKIP"

    # Already closed RFQs
    status = str(r.get("STATUS", "")).upper()
    if status in ("CLOSED", "DONE", "COMPLETED"):
        return "SKIP"

    # Vendor pending → no quotation received
    if not str(r.get("QUOTATION RECEIVED", "")).strip():
        return "VENDOR_PENDING"

    # Clarification pending
    if str(r.get("CLARIFICATION", "")).strip():
        return "CLARIFICATION"

    # Quotation received
    if str(r.get("QUOTATION RECEIVED", "")).strip():
        return "QUOTATION_RECEIVED"

    # Overdue
    if r.get("DUE DAYS", 0) < 0:
        return "OVERDUE"

    # High / Medium / Low (normal RFQ priority)
    dd = int(r.get("DUE DAYS", 99))
    if dd <= 2:
        return "HIGH"
    if dd <= 3:
        return "MEDIUM"
    return "LOW"



# ----------------------------------------------------------------------
# ------------------------ MAIN ENGINE ---------------------------------
# ----------------------------------------------------------------------

def run_engine(rows):
    """
    rows → list of dictionaries from sheet_reader.py
    RETURNS → (updates, email_content)
    updates → rows that MUST be written back to Google Sheet
    email_content → summary entries for email body
    """

    updates = []
    email_content = []

    if not rows:
        return [], []

    for r in rows:

        # Safety: ensure dict format
        if not isinstance(r, dict):
            continue

        # CLASSIFY
        try:
            status = classify_row(r)
        except Exception:
            r["STATUS"] = "ERROR"
            updates.append(r)
            email_content.append({
                "rfq": r.get("RFQ NO"),
                "client": r.get("CUSTOMER NAME"),
                "status": "ERROR",
            })
            continue

        # SKIP rows
        if status == "SKIP":
            continue

        # INVALID rows
        if status == "INVALID":
            r["STATUS"] = "INVALID"
            updates.append(r)
            email_content.append({
                "rfq": r.get("RFQ NO"),
                "client": r.get("CUSTOMER NAME"),
                "status": "INVALID",
            })
            continue

        # NORMAL STATES (HIGH, MEDIUM, LOW, OVERDUE, PENDING, etc.)
        r["STATUS"] = status
        updates.append(r)

        # Build lightweight email summary
        email_content.append({
            "rfq": r.get("RFQ NO"),
            "client": r.get("CUSTOMER NAME"),
            "status": status,
            "due": r.get("DUE DAYS"),
        })

    return updates, email_content
