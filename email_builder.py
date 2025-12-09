import datetime

def build_email_html(data):
    """
    Build complete HTML email for Level-50 Reminder.
    'data' is the dict returned from logic_engine.run_level50()
    """

    today = datetime.date.today().strftime("%d-%b-%Y")

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 14px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ padding: 6px; border: 1px solid #ccc; }}
            .section-title {{ font-size: 18px; margin-top: 20px; font-weight: bold; }}
        </style>
    </head>
    <body>

    <h2>Daily RFQ Reminder — {today}</h2>

    <h3>Summary</h3>
    <p>Total RFQs: {data.get('total', 0)}</p>

    <ul>
        <li>High Priority: {len(data.get('high', []))}</li>
        <li>Medium Priority: {len(data.get('medium', []))}</li>
        <li>Low Priority: {len(data.get('low', []))}</li>
        <li>Vendor Pending: {len(data.get('vendor_pending', []))}</li>
        <li>Clarification: {len(data.get('clarification', []))}</li>
        <li>Overdue: {len(data.get('overdue', []))}</li>
    </ul>

    <hr>
    """

    # ---------- TABLE BUILDER ----------
    def section_table(title, rows):
        if not rows:
            return ""

        table = f"""<div class="section-title">{title}</div>
        <table>
            <tr>
                <th>RFQ No</th>
                <th>UID</th>
                <th>Customer</th>
                <th>Due Date</th>
                <th>Next Step</th>
            </tr>
        """

        for r in rows:
            table += f"""
            <tr>
                <td>{r.get('RFQ NO')}</td>
                <td>{r.get('UID')}</td>
                <td>{r.get('CUSTOMER')}</td>
                <td>{r.get('DUE')}</td>
                <td>{r.get('NEXT')}</td>
            </tr>
            """

        table += "</table>"
        return table

    # Add all sections
    html += section_table("High Priority", data.get("high", []))
    html += section_table("Medium Priority", data.get("medium", []))
    html += section_table("Low Priority", data.get("low", []))
    html += section_table("Vendor Pending", data.get("vendor_pending", []))
    html += section_table("Clarification", data.get("clarification", []))
    html += section_table("Overdue", data.get("overdue", []))

    html += "</body></html>"
    return html