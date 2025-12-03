from datetime import date

def build_table(title, rows, color):
    if not rows:
        return ""

    table_html = f"""
    <h3 style="color:{color};font-weight:bold;">{title}</h3>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <tr style="background:#f3f3f3;font-weight:bold;">
            <td>RFQ No</td>
            <td>UID No</td>
            <td>Customer</td>
            <td>Due Date</td>
            <td>Days Overdue</td>
            <td>Next Step</td>
        </tr>
    """

    for r in rows:
        table_html += f"""
        <tr>
            <td>{r['rfq']}</td>
            <td>{r['uid']}</td>
            <td>{r['customer']}</td>
            <td>{r['due']}</td>
            <td>{r['days_overdue']}</td>
            <td>{r['next_step']}</td>
        </tr>
        """

    table_html += "</table>"
    return table_html


def build_email_html(summary, sections):
    today = date.today().strftime("%d-%b-%Y")

    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 14px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        td {{ border: 1px solid #ccc; padding: 6px; word-wrap: break-word; }}
        @media only screen and (max-width: 480px) {{
            table, td {{ width: 100% !important; font-size: 13px !important; }}
        }}
    </style>
    </head>
    <body>
    <h2>Daily RFQ Reminder (Level-50 Smart Assistant)</h2>
    <h3>Daily RFQ Summary — {today}</h3>
    <p>Total RFQs in Reminder: { sum(summary.values()) }</p>

    <ul style="list-style:none;padding:0;">
        <li>🔴 High Priority: {summary['high']}</li>
        <li>🟡 Medium Priority: {summary['medium']}</li>
        <li>🟢 Low Priority: {summary['low']}</li>
        <li>🟣 Vendors Not Responded: {summary['vendor_pending']}</li>
        <li>🔵 Client Clarifications: {summary['clarification']}</li>
        <li>⚫ Overdue RFQs: {summary['overdue']}</li>
    </ul>

    <hr>

    {build_table("High Priority", sections["high"], "#cc0000")}
    {build_table("Medium Priority", sections["medium"], "#e6ac00")}
    {build_table("Low Priority", sections["low"], "#009933")}
    {build_table("Vendor Pending", sections["vendor_pending"], "#6600cc")}
    {build_table("Client Clarifications", sections["clarification"], "#0047b3")}
    {build_table("Overdue RFQs", sections["overdue"], "#000000")}

    </body>
    </html>
    """
    return html
