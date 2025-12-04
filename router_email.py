from fastapi import APIRouter, HTTPException
import traceback

from sheet_reader import read_sheet
from logic_engine import run_level50
from email_sender import send_email

router = APIRouter()

SALES_RECIPIENT = "sales@ventilengineering.com"


# ---------------------------------------------------------
# Build Gmail-safe HTML tables
# ---------------------------------------------------------

def build_table(rows, columns):
    if not rows:
        return """
            <tr>
                <td colspan="20" style="padding:10px; text-align:center; color:#777;">
                    No records found.
                </td>
            </tr>
        """

    html = ""
    row_index = 0
    for row in rows:
        bg = "#fafafa" if row_index % 2 == 0 else "white"
        row_index += 1

        html += "<tr style='background:{};'>".format(bg)
        for col in columns:
            html += "<td style='padding:8px; border-bottom:1px solid #eee;'>{}</td>".format(row.get(col, ""))
        html += "</tr>"

    return html


# ---------------------------------------------------------
# Build COMPLETE Gmail-safe Email HTML
# ---------------------------------------------------------

def build_html_email(result: dict):

    summary = result.get("summary", {})
    sections = result.get("sections", {})

    # Individual section tables
    high_html = build_table(
        sections.get("HIGH", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "DAYS OVERDUE", "NEXT STEP"]
    )

    medium_html = build_table(
        sections.get("MEDIUM", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "DAYS OVERDUE", "NEXT STEP"]
    )

    low_html = build_table(
        sections.get("LOW", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "DAYS OVERDUE", "NEXT STEP"]
    )

    vendor_html = build_table(
        sections.get("VENDOR_PENDING", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "PENDING SINCE", "NEXT STEP"]
    )

    quotation_html = build_table(
        sections.get("QUOTATION_RECEIVED", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "NEXT STEP"]
    )

    clarification_html = build_table(
        sections.get("CLIENT_CLARIFICATIONS", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "NEXT STEP"]
    )

    post_offer_html = build_table(
        sections.get("POST_OFFER", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "NEXT STEP"]
    )

    overdue_html = build_table(
        sections.get("OVERDUE", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "DAYS OVERDUE", "NEXT STEP"]
    )

    # ---------------------------
    # Render the FULL HTML email
    # ---------------------------

    html = f"""
<html>
<body style="margin:0; padding:0; font-family:Arial, sans-serif; color:#333;">
    <div style="max-width:900px; margin:0 auto; padding:20px;">

        <h2 style="text-align:center; margin-bottom:5px; font-size:24px;">
            Daily RFQ Reminder (Level-50 Smart Assistant)
        </h2>

        <h3 style="text-align:center; margin-top:0; font-size:18px; color:#444;">
            Daily RFQ Summary
        </h3>

        <h3 style="text-align:center; margin-top:20px; margin-bottom:20px;">
            Total RFQs in Reminder: {summary.get("TOTAL", "N/A")}
        </h3>

        <hr style="margin:20px 0;">

        <ul style="list-style:none; padding-left:0; font-size:15px; line-height:26px;">
            <li>🔴 High Priority: {summary.get("HIGH", 0)}</li>
            <li>🟠 Medium Priority: {summary.get("MEDIUM", 0)}</li>
            <li>🟢 Low Priority: {summary.get("LOW", 0)}</li>
            <li>🟣 Vendors Not Responded: {summary.get("VENDOR_PENDING", 0)}</li>
            <li>🟡 Quotation Received: {summary.get("QUOTATION_RECEIVED", 0)}</li>
            <li>🔵 Client Clarifications: {summary.get("CLIENT_CLARIFICATIONS", 0)}</li>
            <li>🟤 Post-Offer Client Queries: {summary.get("POST_OFFER", 0)}</li>
            <li>⚫ Overdue RFQs: {summary.get("OVERDUE", 0)}</li>
        </ul>

        <hr style="margin:25px 0;">


        <!-- HIGH PRIORITY -->
        <h3 style="margin-top:40px;">🔴 High Priority</h3>
        <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
            <tr style="background:#f2f2f2; font-weight:bold;">
                <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                <td>Days Overdue</td><td>Next Step</td>
            </tr>
            {high_html}
        </table>


        <!-- MEDIUM PRIORITY -->
        <h3 style="margin-top:40px;">🟠 Medium Priority</h3>
        <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
            <tr style="background:#f2f2f2; font-weight:bold;">
                <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                <td>Days Overdue</td><td>Next Step</td>
            </tr>
            {medium_html}
        </table>


        <!-- LOW PRIORITY -->
        <h3 style="margin-top:40px;">🟢 Low Priority</h3>
        <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
            <tr style="background:#f2f2f2; font-weight:bold;">
                <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                <td>Days Overdue</td><td>Next Step</td>
            </tr>
            {low_html}
        </table>


        <!-- VENDOR PENDING -->
        <h3 style="margin-top:40px;">🟣 Vendor Pending</h3>
        <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
            <tr style="background:#f2f2f2; font-weight:bold;">
                <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                <td>Pending Since</td><td>Next Step</td>
            </tr>
            {vendor_html}
        </table>


        <!-- QUOTATION RECEIVED -->
        <h3 style="margin-top:40px;">🟡 Quotation Received</h3>
        <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
            <tr style="background:#f2f2f2; font-weight:bold;">
                <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td><td>Next Step</td>
            </tr>
            {quotation_html}
        </table>


        <!-- CLIENT CLARIFICATIONS -->
        <h3 style="margin-top:40px;">🔵 Client Clarifications</h3>
        <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
            <tr style="background:#f2f2f2; font-weight:bold;">
                <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td><td>Next Step</td>
            </tr>
            {clarification_html}
        </table>


        <!-- POST-OFFER -->
        <h3 style="margin-top:40px;">🟤 Post-Offer Client Queries</h3>
        <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
            <tr style="background:#f2f2f2; font-weight:bold;">
                <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td><td>Next Step</td>
            </tr>
            {post_offer_html}
        </table>


        <!-- OVERDUE -->
        <h3 style="margin-top:40px;">⚫ Overdue</h3>
        <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
            <tr style="background:#f2f2f2; font-weight:bold;">
                <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                <td>Days Overdue</td><td>Next Step</td>
            </tr>
            {overdue_html}
        </table>

    </div>
</body>
</html>
"""

    return html


# ---------------------------------------------------------
# FINAL ENDPOINT
# ---------------------------------------------------------

@router.post("/manual-reminder")
def manual_reminder():
    try:
        _ = read_sheet()

        engine_output = run_level50(debug=False)

        html_body = build_html_email(engine_output)

        send_result = send_email(
            SALES_RECIPIENT,
            "Manual RFQ Reminder — Level-50 Smart Assistant",
            html_body,
            is_html=True
        )

        return {
            "status": "sent",
            "recipient": SALES_RECIPIENT,
            "summary": engine_output.get("summary"),
            "sections_sent": list(engine_output.get("sections", {}).keys()),
            "send_result": send_result
        }

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex) + "\n" + traceback.format_exc()
        )
