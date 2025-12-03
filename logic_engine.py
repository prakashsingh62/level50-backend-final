# logic_engine.py
from datetime import datetime
from typing import List, Tuple

# Threshold (INR)
HIGH_VALUE_THRESHOLD = 500000.0

# Normalize date parsing: try multiple common formats
DATE_FORMATS = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y"]

def parse_date(s):
    if not s:
        return None
    s = s.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    # try iso-ish fallback
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None

def run_engine(rows: List[List[str]]) -> Tuple[List[dict], List[str]]:
    """
    Input:
      rows - 2D list from sheet_reader.fetch_rows() (header row + data rows)

    Output:
      updates -> list of {"row": int, "column": str, "value": any}
      email_content -> list of HTML strings (blocks)
    """

    updates = []
    email_blocks = []

    if not rows or len(rows) < 2:
        return updates, email_blocks

    header = rows[0]
    body = rows[1:]

    # Utility: safe getter by column name (returns empty string if missing)
    def get_val(row, col_name):
        if col_name not in header:
            return ""
        idx = header.index(col_name)
        return row[idx] if idx < len(row) else ""

    # Column names exactly as provided
    COL_CURRENT_STATUS = "CURRENT STATUS"
    COL_FINAL_STATUS = "FINAL STATUS"
    COL_DUE_DATE = "DUE DATE"
    COL_INQUIRY_SENT = "INQUIRY SENT ON"
    COL_VENDOR_QUOT_STATUS = "VENDOR QUOTATION STATUS"
    COL_VEPL_OFFER_VALUE = "VEPL OFFER VALUE"
    COL_VENDOR_FOLLOWUP_AGING = "Vendor Follow-up Aging"
    COL_AGING = "Aging"
    COL_SYSTEM_NOTES = "SYSTEM NOTES"

    now = datetime.now()

    for idx, row in enumerate(body, start=2):  # sheet rows start at 2
        # read fields
        current_status = get_val(row, COL_CURRENT_STATUS).strip().upper()
        final_status = get_val(row, COL_FINAL_STATUS).strip().upper()
        due_date_str = get_val(row, COL_DUE_DATE)
        inquiry_sent_str = get_val(row, COL_INQUIRY_SENT)
        vendor_quoter = get_val(row, COL_VENDOR_QUOT_STATUS).strip().upper()
        vepl_value_str = get_val(row, COL_VEPL_OFFER_VALUE)

        # 1) Compute Aging from DUE DATE and write to 'Aging'
        aging_days = ""
        due_date = parse_date(due_date_str)
        if due_date:
            aging_days = (now - due_date).days
            # write Aging only if integer
            updates.append({
                "row": idx,
                "column": COL_AGING,
                "value": aging_days
            })

        # 2) Compute Vendor Follow-up Aging from INQUIRY SENT ON
        vendor_followup_aging = ""
        inquiry_date = parse_date(inquiry_sent_str)
        if inquiry_date:
            vendor_followup_aging = (now - inquiry_date).days
            updates.append({
                "row": idx,
                "column": COL_VENDOR_FOLLOWUP_AGING,
                "value": vendor_followup_aging
            })

        # 3) High Priority: CURRENT STATUS suggests immediate attention
        if current_status in ("HIGH", "URGENT", "RED"):
            email_blocks.append(
                f"<p><b>Row {idx} — HIGH PRIORITY:</b> CURRENT STATUS = {current_status}.</p>"
            )

        # 4) Vendor pending: no vendor quotation after 2+ days since inquiry
        vendor_pending_condition = False
        if (vendor_quoter == "" or vendor_quoter in ("PENDING", "NO QUOTE", "NOT RECEIVED")):
            if isinstance(vendor_followup_aging, int) and vendor_followup_aging >= 2:
                vendor_pending_condition = True

        if vendor_pending_condition:
            email_blocks.append(
                f"<p><b>Row {idx} — Vendor pending:</b> No quotation after {vendor_followup_aging} days since inquiry.</p>"
            )

        # 5) High value detection (VEPL OFFER VALUE) -> annotate SYSTEM NOTES
        try:
            v = float(vepl_value_str.replace(",", "").strip())
        except Exception:
            v = None

        if v and v >= HIGH_VALUE_THRESHOLD:
            # append a SYSTEM NOTES tag; preserve any existing note by appending
            note_text = "HIGH_VALUE"
            email_blocks.append(
                f"<p><b>Row {idx} — High Value RFQ:</b> VEPL OFFER VALUE = {v:.2f}.</p>"
            )
            # write into SYSTEM NOTES (append)
            updates.append({
                "row": idx,
                "column": COL_SYSTEM_NOTES,
                "value": note_text
            })

    # deduplicate small email blocks or aggregate if needed (kept simple)
    return updates, email_blocks
