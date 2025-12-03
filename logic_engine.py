# logic_engine.py
from datetime import datetime
from typing import List, Tuple

DATE_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]

FINAL_STATUS_SKIP = {
    "CLOSED", "LOST", "DROPPED", "CANCELLED", "WON", "REGRET"
}

HIGH_VALUE_THRESHOLD = 500000  # You selected 5 lakh

def parse_date(s: str):
    if not s:
        return None
    s = s.strip()
    for f in DATE_FORMATS:
        try:
            return datetime.strptime(s, f)
        except:
            pass
    try:
        return datetime.fromisoformat(s)
    except:
        return None

def safe_get(row: list, header: list, col: str, default=""):
    if col not in header:
        return default
    i = header.index(col)
    return row[i] if i < len(row) else default

def run_engine(rows: List[List[str]]) -> Tuple[List[dict], List[str]]:
    updates = []
    email_sections = []

    if not rows or len(rows) < 2:
        return updates, email_sections

    header = rows[0]
    body = rows[1:]
    now = datetime.now()

    urgent = []
    high = []
    medium = []
    low = []
    vendor_pending = []
    post_offer = []
    clarifications = []
    high_value = []
    followups = []
    smart = []

    for idx, row in enumerate(body, start=2):
        current = safe_get(row, header, "CURRENT STATUS").strip().upper()
        final = safe_get(row, header, "FINAL STATUS").strip().upper()

        if final in FINAL_STATUS_SKIP:
            continue

        due_str = safe_get(row, header, "DUE DATE")
        inquiry_str = safe_get(row, header, "INQUIRY SENT ON")
        vendor_status = safe_get(row, header, "VENDOR QUOTATION STATUS").strip().upper()
        post_query = safe_get(row, header, "POST OFFER QUERY").strip()
        clarif = safe_get(row, header, "CLARIFICATION").strip()
        follow_date = safe_get(row, header, "FOLLOWUP DATE").strip()
        offer_value_raw = safe_get(row, header, "VEPL OFFER VALUE").strip()

        due_date = parse_date(due_str)
        inquiry_date = parse_date(inquiry_str)
        follow_dt = parse_date(follow_date)

        aging = ""
        vendor_aging = ""

        if due_date:
            aging = (now - due_date).days
            updates.append({"row": idx, "column": "Aging", "value": aging})

        if inquiry_date:
            vendor_aging = (now - inquiry_date).days
            updates.append({"row": idx, "column": "Vendor Follow-up Aging", "value": vendor_aging})

        offer_value = None
        try:
            offer_value = float(offer_value_raw.replace(",", ""))
        except:
            pass

        if due_date:
            if due_date.date() < now.date():
                urgent.append((idx, row, "Overdue – prepare immediately"))
            elif due_date.date() == now.date():
                urgent.append((idx, row, "Due today – action required now"))

        if due_date:
            days = (due_date.date() - now.date()).days
            if days <= 2 and days >= 0:
                high.append((idx, row, "High priority (<=2 days)"))
            elif days == 3:
                medium.append((idx, row, "Due in 3 days"))
            elif days == 4:
                low.append((idx, row, "Due in 4 days"))

        if (vendor_status == "" or vendor_status in ("PENDING", "NOT RECEIVED", "NO QUOTE")):
            if isinstance(vendor_aging, int) and vendor_aging >= 2:
                vendor_pending.append((idx, row, f"No vendor quote for {vendor_aging} days"))

        if post_query:
            post_offer.append((idx, row, "Customer has a post-offer query"))

        if clarif:
            clarifications.append((idx, row, "Clarification required"))

        if offer_value and offer_value >= HIGH_VALUE_THRESHOLD:
            high_value.append((idx, row, f"High value RFQ (>= {HIGH_VALUE_THRESHOLD})"))

        if follow_dt:
            if follow_dt.date() == now.date():
                followups.append((idx, row, "Customer follow-up due today"))

        if (not post_query and not clarif and not vendor_pending and not urgent):
            if isinstance(aging, int) and aging >= 7:
                smart.append((idx, row, f"No movement for {aging} days – review needed"))

    def block(title, rows):
        if not rows:
            return ""
        html = f"<h3 style='color:#3366cc;'>{title}</h3>"
        html += "<table class='mobile-table' style='width:100%;border-collapse:collapse;font-size:14px;'>"
        html += "<tr style='background:#f0f0f0;font-weight:bold;'>"
        html += "<td>Row</td><td>CUSTOMER</td><td>PRODUCT</td><td>DUE</td><td>STATUS</td><td>AGING</td><td>NEXT STEP</td></tr>"
        for (r, row, nxt) in rows:
            cust = safe_get(row, header, "CUSTOMER NAME")
            prod = safe_get(row, header, "PRODUCT")
            due = safe_get(row, header, "DUE DATE")
            st = safe_get(row, header, "CURRENT STATUS")
            ag = safe_get(row, header, "Aging")
            html += f"<tr><td>{r}</td><td>{cust}</td><td>{prod}</td><td>{due}</td><td>{st}</td><td>{ag}</td><td>{nxt}</td></tr>"
        html += "</table><br>"
        return html

    email_sections = [
        block("URGENT", urgent),
        block("High Priority", high),
        block("Medium Priority", medium),
        block("Low Priority", low),
        block("Vendor Pending", vendor_pending),
        block("Post-Offer Queries", post_offer),
        block("Clarifications Required", clarifications),
        block("High Value RFQs", high_value),
        block("Follow-Up Due Today", followups),
        block("System Suggestions", smart),
    ]

    final_blocks = [b for b in email_sections if b.strip()]
    return updates, final_blocks
