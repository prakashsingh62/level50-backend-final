from datetime import datetime

def build_email(processed):
    """
    Level-50 formatted email with section grouping.
    """

    # Sections
    sections = {
        "OVERDUE": [],
        "HIGH": [],
        "MEDIUM": [],
        "LOW": [],
        "NOACTION": [],
        "UNKNOWN": []
    }

    # Group rows into sections
    for r in processed:
        status = r.get("STATUS", "UNKNOWN").upper()
        if status not in sections:
            sections["UNKNOWN"].append(r)
        else:
            sections[status].append(r)

    # Helper date formatting
    def fmt_date(raw):
        try:
            # try dd/mm/yyyy
            if isinstance(raw, str) and "/" in raw:
                return raw
            # if numeric
            if isinstance(raw, (int, float)):
                base = datetime(1899, 12, 30)
                d = base.timestamp() + (float(raw) * 86400)
                return datetime.fromtimestamp(d).strftime("%d/%m/%Y")
        except:
            pass
        return str(raw)

    # Build body
    body = ""
    body += "LEVEL-50 DAILY RFQ SUMMARY\n"
    body += f"Date: {datetime.now().strftime('%d/%m/%Y')}\n"
    body += "-" * 48 + "\n\n"

    def add_section(title, rows):
        nonlocal body
        if not rows:
            return
        body += f"{title}\n"
        body += "-" * len(title) + "\n"
        for r in rows:
            body += (
                f"RFQ: {r.get('RFQ NO')} | "
                f"{r.get('CUSTOMER NAME')} | "
                f"{r.get('VENDOR')} | "
                f"Due: {fmt_date(r.get('DUE DATE'))}\n"
            )
        body += "\n"

    # Order of sections
    add_section("OVERDUE RFQs", sections["OVERDUE"])
    add_section("HIGH PRIORITY (≤2 days)", sections["HIGH"])
    add_section("MEDIUM PRIORITY (3 days)", sections["MEDIUM"])
    add_section("LOW PRIORITY (4 days)", sections["LOW"])
    add_section("NO ACTION", sections["NOACTION"])
    add_section("UNKNOWN / INVALID DATES", sections["UNKNOWN"])

    subject = f"Level-50 RFQ Summary – {datetime.now().strftime('%d/%m/%Y')}"
    return subject, body
