from datetime import datetime, timedelta

def run_engine(rows):
    """
    rows = values read from Google Sheet using sheet_reader.fetch_rows()

    Returns:
        updates: [
            {"row": 5, "column": "STATUS", "value": "HIGH"},
            {"row": 8, "column": "AGING", "value": "2"},
        ]

        email_content: [
            "<h3>High Priority</h3> ....",
            "<h3>Vendor Pending</h3> ...."
        ]
    """

    updates = []
    email_blocks = []

    if not rows or len(rows) < 2:
        return updates, email_blocks

    header = rows[0]
    body = rows[1:]

    # Utility function to safely extract column value
    def get(row, col_name, default=""):
        if col_name not in header:
            return default
        idx = header.index(col_name)
        return row[idx] if idx < len(row) else default

    # -----------------------------------------
    # PROCESS ALL ROWS
    # -----------------------------------------
    for row_index, row in enumerate(body, start=2):      # Row 2 = Sheet row 2
        status = get(row, "STATUS", "")
        due_date_str = get(row, "DUE DATE", "")
        vendor_resp = get(row, "VENDOR RESPONSE", "")
        rfq_value = get(row, "VALUE", "")

        # ---- Compute aging (example engine) ----
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%d-%m-%Y")
                aging_days = (datetime.now() - due_date).days
            except:
                aging_days = ""
        else:
            aging_days = ""

        # Populate AGING column if computed
        if isinstance(aging_days, int) and aging_days >= 0:
            updates.append({
                "row": row_index,
                "column": "AGING",
                "value": aging_days
            })

        # -----------------------------------------
        # HIGH PRIORITY RULE (example)
        # -----------------------------------------
        if status == "HIGH":
            email_blocks.append(
                f"<p><b>Row {row_index}</b> — High Priority RFQ pending.</p>"
            )

        # -----------------------------------------
        # VENDOR PENDING RULE (example)
        # -----------------------------------------
        if vendor_resp == "" and isinstance(aging_days, int) and aging_days >= 2:
            email_blocks.append(
                f"<p><b>Row {row_index}</b> — Vendor pending for {aging_days} days.</p>"
            )

        # -----------------------------------------
        # VALUE-BASED LOGIC (example)
        # -----------------------------------------
        try:
            v = float(rfq_value)
            if v > 500000:
                updates.append({
                    "row": row_index,
                    "column": "FLAG",
                    "value": "HIGH_VALUE"
                })
        except:
            pass

    return updates, email_blocks
