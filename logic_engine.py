# logic_engine.py (Write Optimization V2 Enabled)
from datetime import datetime
from typing import List, Tuple

FINAL_STATUS_SKIP = {"CLOSED", "COMPLETED", "REGRET", "SUBMITTED", "DONE"}
VENDOR_NO_QUOTE = {"", "PENDING", "NOT RECEIVED", "NO QUOTE", "NONE", "N/A"}

DATE_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d %b %Y", "%d %B %Y"]


def parse_date(s: str):
    if not s:
        return None
    s = str(s).strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except:
        pass
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except:
            continue
    return None


def make_header_map(header_row: List[str]):
    m = {}
    for i, h in enumerate(header_row):
        if h:
            m[str(h).strip().upper()] = i
    return m


def safe_col(row, header_map, names, default=""):
    if isinstance(names, str):
        names = [names]
    for n in names:
        key = n.upper()
        if key in header_map:
            idx = header_map[key]
            return row[idx] if idx < len(row) else default
    return default


def short_next_step(cat, days, vendor_age):
    if cat == "HIGH":
        return "Prepare immediately"
    if cat == "MEDIUM":
        return "Prepare soon"
    if cat == "LOW":
        return "Follow-up"
    if cat == "VENDOR_PENDING":
        return "Vendor follow-up now"
    if cat == "CLARIFICATION":
        return "Clarification required"
    if cat == "POST_OFFER":
        return "Respond to query"
    if cat == "OVERDUE":
        return "Prepare immediately"
    return "Review"


def run_engine(rows: List[List[str]]):
    """
    RETURNS:
      aging_updates = {row_number: value}
      vendor_updates = {row_number: value}
      email_blocks = list of HTML blocks
    """
    aging_updates = {}
    vendor_updates = {}
    email_blocks = []

    if not rows or len(rows) < 2:
        return aging_updates, vendor_updates, email_blocks

    header = rows[0]
    body = rows[1:]
    header_map = make_header_map(header)
    today = datetime.now().date()

    # Containers for sections
    high = []
    medium = []
    low = []
    vendor_pending = []
    clarifications = []
    post_offer = []
    overdue = []

    summary = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0,
        "VENDOR_PENDING": 0,
        "QUOTATION_RECEIVED": 0,
        "CLARIFICATIONS": 0,
        "POST_OFFER": 0,
        "OVERDUE": 0
    }

    total_in_reminder = 0

    # -------------------------
    # PROCESS EACH ROW
    # -------------------------
    for idx, row in enumerate(body, start=2):
        rfq_no = safe_col(row, header_map, "RFQ NO")
        uid_no = safe_col(row, header_map, "UID NO")
        customer = safe_col(row, header_map, "CUSTOMER NAME")
        due_raw = safe_col(row, header_map, "DUE DATE")
        final_status = str(safe_col(row, header_map, "FINAL STATUS")).upper().strip()
        vendor_status = str(safe_col(row, header_map, "VENDOR QUOTATION STATUS")).upper().strip()
        inquiry_raw = safe_col(row, header_map, "INQUIRY SENT ON")
        post_offer_query = safe_col(row, header_map, "POST OFFER QUERY")
        clarification = safe_col(row, header_map, "CLARIFICATION")

        # Skip final status completed rows
        if final_status in FINAL_STATUS_SKIP:
            continue

        # Parse due date
        due_dt = parse_date(due_raw)
        if not due_dt:
            continue
        due_date = due_dt.date()

        # Only overdue or due today, max 10 days
        days_overdue = (today - due_date).days
        if days_overdue < 0:
            continue
        if days_overdue > 10:
            continue

        total_in_reminder += 1

        # -----------------------
        # AGING updates (V2 batching)
        # -----------------------
        aging_updates[idx] = days_overdue

        # Vendor aging
        vendor_age = None
        if inquiry_raw:
            iq_dt = parse_date(inquiry_raw)
            if iq_dt:
                vendor_age = (today - iq_dt.date()).days
                vendor_updates[idx] = vendor_age
            else:
                vendor_age = None

        # -----------------------
        # Categorization
        # -----------------------
        if 0 <= days_overdue <= 2:
            high.append((idx, rfq_no, uid_no, customer, due_date, days_overdue, vendor_age))
            summary["HIGH"] += 1
        elif days_overdue == 3:
            medium.append((idx, rfq_no, uid_no, customer, due_date, days_overdue, vendor_age))
            summary["MEDIUM"] += 1
        elif days_overdue == 4:
            low.append((idx, rfq_no, uid_no, customer, due_date, days_overdue, vendor_age))
            summary["LOW"] += 1
        else:
            overdue.append((idx, rfq_no, uid_no, customer, due_date, days_overdue, vendor_age))
            summary["OVERDUE"] += 1

        # Vendor pending
        if vendor_age is not None and vendor_age >= 2 and vendor_status in VENDOR_NO_QUOTE:
            vendor_pending.append((idx, rfq_no, uid_no, customer, due_date, vendor_age))
            summary["VENDOR_PENDING"] += 1
        elif vendor_status and vendor_status not in VENDOR_NO_QUOTE:
            summary["QUOTATION_RECEIVED"] += 1

        # Clarifications
        if str(clarification).strip():
            clarifications.append((idx, rfq_no, uid_no, customer, due_date))
            summary["CLARIFICATIONS"] += 1

        # Post-offer queries
        if str(post_offer_query).strip():
            post_offer.append((idx, rfq_no, uid_no, customer, due_date))
            summary["POST_OFFER"] += 1

    # -------------------------
    # BUILD HTML BLOCKS
    # -------------------------
    summary_block = f"""
    <h2>Daily RFQ Summary</h2>
    <p>Total RFQs in Reminder: {total_in_reminder}</p>
    <ul style='list-style:none;padding-left:0;'>
        <li>🔴 High Priority: {summary['HIGH']}</li>
        <li>🟡 Medium Priority: {summary['MEDIUM']}</li>
        <li>🟢 Low Priority: {summary['LOW']}</li>
        <li>🟣 Vendors Not Responded: {summary['VENDOR_PENDING']}</li>
        <li>🟠 Quotation Received: {summary['QUOTATION_RECEIVED']}</li>
        <li>🔵 Client Clarifications: {summary['CLARIFICATIONS']}</li>
        <li>🟠 Post-Offer Client Queries: {summary['POST_OFFER']}</li>
        <li>⚫ Overdue RFQs: {summary['OVERDUE']}</li>
    </ul>
    <hr>
    """
    email_blocks.append(summary_block)

    # Table builder
    def make_table(title, items, mode):
        if not items:
            return ""

        html = f"<h3>{title}</h3>"
        html += "<table style='width:100%;border-collapse:collapse;'>"

        if mode == "vendor":
            html += """
            <tr style='background:#f3f3f3;font-weight:bold;'>
              <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
              <td>Pending Since</td><td>Next Step</td>
            </tr>"""
            for _, rfq, uid, cust, ddt, pend in items:
                html += f"""
                <tr>
                  <td>{rfq}</td><td>{uid}</td><td>{cust}</td>
                  <td>{ddt.strftime('%d-%b-%Y')}</td>
                  <td>{pend}</td>
                  <td>{short_next_step("VENDOR_PENDING", 0, pend)}</td>
                </tr>
                """
        else:
            html += """
            <tr style='background:#f3f3f3;font-weight:bold;'>
              <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
              <td>Days Overdue</td><td>Next Step</td>
            </tr>"""

            for _, rfq, uid, cust, ddt, over, vend in items:
                html += f"""
                <tr>
                  <td>{rfq}</td><td>{uid}</td><td>{cust}</td>
                  <td>{ddt.strftime('%d-%b-%Y')}</td>
                  <td>{over}</td>
                  <td>{short_next_step(mode, over, vend)}</td>
                </tr>
                """

        html += "</table>"
        return html

    email_blocks.append(make_table("🔴 High Priority", high, "HIGH"))
    email_blocks.append(make_table("🟡 Medium Priority", medium, "MEDIUM"))
    email_blocks.append(make_table("🟢 Low Priority", low, "LOW"))
    email_blocks.append(make_table("🟣 Vendor Pending", vendor_pending, "vendor"))
    email_blocks.append(make_table("🔵 Client Clarifications", clarifications, "CLARIFICATION"))
    email_blocks.append(make_table("🟠 Post-Offer Client Queries", post_offer, "POST_OFFER"))
    email_blocks.append(make_table("⚫ Overdue (<=10 days)", overdue, "OVERDUE"))

    return aging_updates, vendor_updates, email_blocks
