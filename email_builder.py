def build_email(summary, sections):
    html = f"""
    <h2>Daily RFQ Reminder</h2>
    <p><b>High:</b> {summary['high']} |
       <b>Medium:</b> {summary['medium']} |
       <b>Low:</b> {summary['low']} |
       <b>Vendor Pending:</b> {summary['vendor_pending']} |
       <b>Post Offer:</b> {summary['post_offer']} |
       <b>Overdue:</b> {summary['overdue']}</p>

    <hr>
    """

    for section, rows in sections.items():
        if not rows:
            continue

        html += f"<h3>{section.upper()}</h3>"
        html += """
        <table border='1' cellpadding='6' cellspacing='0'>
        <tr>
            <th>RFQ No</th>
            <th>UID No</th>
            <th>Customer</th>
            <th>Due</th>
            <th>Days Overdue</th>
            <th>Next Step</th>
        </tr>
        """

        for r in rows:
            html += f"""
            <tr>
                <td>{r['rfq']}</td>
                <td>{r['uid']}</td>
                <td>{r['customer']}</td>
                <td>{r['due']}</td>
                <td>{r['days_overdue']}</td>
                <td>{r['next_step']}</td>
            </tr>
            """

        html += "</table><br>"

    return html
