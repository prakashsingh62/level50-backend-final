import datetime

DATE_FORMAT = "%d-%m-%Y"

FINAL_SKIP_STATUSES = {"closed", "completed", "regret", "submitted", "done"}

def parse_date(val):
    if not val:
        return None
    try:
        return datetime.datetime.strptime(val.strip(), DATE_FORMAT).date()
    except:
        return None

def days_between(d1, d2):
    if not d1 or not d2:
        return None
    return (d1 - d2).days

def compute_next_step(days_overdue, vendor_pending, client_clarification):
    if days_overdue is not None and days_overdue > 0:
        return "Overdue – prepare immediately"
    if vendor_pending:
        return "Vendor follow-up now"
    if client_clarification:
        return "Prepare clarification reply"
    return ""

def classify_rows(rows):
    today = datetime.date.today()

    summary = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "vendor_pending": 0,
        "clarification": 0,
        "post_offer": 0,
        "overdue": 0
    }

    sections = {
        "high": [],
        "medium": [],
        "low": [],
        "vendor_pending": [],
        "clarification": [],
        "post_offer": [],
        "overdue": []
    }

    for r in rows:
        rfq_no = r.get("RFQ NO", "").strip()
        uid = r.get("UID NO", "").strip()
        customer = r.get("CUSTOMER NAME", "").strip()
        due_raw = r.get("DUE DATE", "").strip()
        final_status = r.get("FINAL STATUS", "").strip().lower()
        vendor_pending_flag = "vendor" in r.get("VENDOR QUOTATION STATUS", "").lower()
        clarification_flag = bool(r.get("POST OFFER QUERY", "").strip())

        if final_status in FINAL_SKIP_STATUSES:
            continue

        due_date = parse_date(due_raw)
        if not due_date:
            continue

        days_overdue = days_between(today, due_date)
        if days_overdue is not None and days_overdue > 10:
            continue

        next_step = compute_next_step(days_overdue, vendor_pending_flag, clarification_flag)

        base_row = {
            "rfq": rfq_no,
            "uid": uid,
            "customer": customer,
            "due": due_raw,
            "next_step": next_step,
            "days_overdue": days_overdue if days_overdue else 0
        }

        # Classification
        if days_overdue and days_overdue > 0:
            summary["overdue"] += 1
            sections["overdue"].append(base_row)

        if vendor_pending_flag:
            summary["vendor_pending"] += 1
            sections["vendor_pending"].append(base_row)

        if clarification_flag:
            summary["clarification"] += 1
            sections["clarification"].append(base_row)

        # Priority logic
        if days_overdue and days_overdue > 0:
            summary["high"] += 1
            sections["high"].append(base_row)
        else:
            # Within due range
            if 0 <= days_overdue <= 2:
                summary["high"] += 1
                sections["high"].append(base_row)
            elif 3 <= days_overdue <= 4:
                summary["medium"] += 1
                sections["medium"].append(base_row)
            else:
                summary["low"] += 1
                sections["low"].append(base_row)

    return summary, sections
