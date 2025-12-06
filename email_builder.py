def build_section(title, rows):
    if not rows:
        return f"""
            <h3 style='color:#888;'>{title}</h3>
            <p style='color:#bbb;'>No items</p>
        """

    items = ""
    for r in rows:
        row_text = " | ".join(str(x) for x in r)
        items += f"<li>{row_text}</li>"

    return f"""
        <h3 style='color:#444;'>{title}</h3>
        <ul>{items}</ul>
    """


def build_list(title, items, highlight=False):
    if not items:
        return ""

    color = "#d9534f" if highlight else "#444"
    li = "".join(f"<li>{i}</li>" for i in items)

    return f"""
        <h3 style='color:{color};'>{title}</h3>
        <ul>{li}</ul>
    """


def build_email(summary, sections, autofix, alerts):
    """
    Produces final Level-51 Daily HTML Email:
    - Summary of RFQ sections
    - Autofix actions taken
    - Critical alerts
    """

    html = """
    <html>
    <body style="font-family:Arial; font-size:14px;">

        <h2 style="color:#2a7ae2;">📌 Level-51 Daily Report</h2>
        <p>This is your automated daily summary + autofix engine report.</p>
        <hr>
    """

    # SUMMARY SECTIONS
    html += build_section("High Priority", sections.get("High Priority", []))
    html += build_section("Medium Priority", sections.get("Medium Priority", []))
    html += build_section("Low Priority", sections.get("Low Priority", []))
    html += build_section("Vendor Pending", sections.get("Vendor Pending", []))
    html += build_section("Client Follow-up", sections.get("Client Follow-up", []))
    html += build_section("Overdue", sections.get("Overdue", []))

    html += "<hr>"

    # AUTOFIX LOG
    html += build_list("🔧 Autofix Actions Performed (Level-51)", autofix)

    # ALERTS (highlighted)
    html += build_list("⚠️ Critical Alerts", alerts, highlight=True)

    html += """
        <br><hr>
        <p style='font-size:12px;color:#888;'>
            Generated automatically by Level-51 RFQ Automation System.
        </p>
    </body>
    </html>
    """

    return html
