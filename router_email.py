from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
import traceback

from sheet_reader import read_sheet
from logic_engine import run_level50
from email_sender import send_email

router = APIRouter()

SALES_RECIPIENT = "sales@ventilengineering.com"


def build_html_email(result: dict) -> str:
    summary = result.get("summary", {})
    level51 = summary.get("level51", {})
    sections = result.get("sections", {})

    # Icons for summary
    ICONS = {
        "HIGH": "🔴",
        "MEDIUM": "🟠",
        "LOW": "🟢",
        "VENDOR_PENDING": "🟣",
        "QUOTATION_RECEIVED": "🟡",
        "CLIENT_CLARIFICATIONS": "🔵",
        "POST_OFFER": "🟤",
        "OVERDUE": "⚫",
    }

    # Safe getter
    def g(k, src):
        return src.get(k, 0)

    # -----------------------
    # BUILD SECTION TABLES
    # -----------------------

    def make_table(rows, columns, zebra=True):
        body_html = ""
        i = 0
        for r in rows:
            bg = "#fafafa" if (i % 2 == 0 and zebra) else "white"
            i += 1

            cells = "".join(
                f"<td style='padding:8px; border-bottom:1px solid #eee;'>{r.get(col,'')}</td>"
                for col in columns
            )
            body_html += f"<tr style='background:{bg};'>{cells}</tr>"

        if body_html == "":
            body_html = """
                <tr>
                    <td colspan="20" style="text-align:center; padding:10px; color:#777;">
                        No records found.
                    </td>
                </tr>
            """
        return body_html

    # -----------------------
    # MAKE ALL 7 SECTIONS
    # -----------------------

    high_table = make_table(
        sections.get("HIGH", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "DAYS OVERDUE", "NEXT STEP"]
    )

    medium_table = make_table(
        sections.get("MEDIUM", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "DAYS OVERDUE", "NEXT STEP"]
    )

    low_table = make_table(
        sections.get("LOW", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "DAYS OVERDUE", "NEXT STEP"]
    )

    vendor_table = make_table(
        sections.get("VENDOR_PENDING", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "PENDING SINCE", "NEXT STEP"]
    )

    quotation_table = make_table(
        sections.get("QUOTATION_RECEIVED", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "NEXT STEP"]
    )

    clarification_table = make_table(
        sections.get("CLIENT_CLARIFICATIONS", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "NEXT STEP"]
    )

    post_offer_table = make_table(
        sections.get("POST_OFFER", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "NEXT STEP"]
    )

    overdue_table = make_table(
        sections.get("OVERDUE", []),
        ["RFQ NO", "UID NO", "CUSTOMER NAME", "DUE DATE", "DAYS OVERDUE", "NEXT STEP"]
    )

    # ======================================================
    # FINAL HTML TEMPLATE (DAILY MAIL PERFECT CLONE)
    # ======================================================

    html = f"""
    <html>
    <body style="font-family:Arial, sans-serif; color:#333;">
        <div style="max-width:900px; margin:auto; padding:20px;">

            <h2 style="text-align:center; margin-bottom:5px;">
                Manual RFQ Reminder (Level-50 Smart Assistant)
            </h2>
            <h3 style="text-align:center; margin-top:0; color:#444;">
                Daily RFQ Summary
            </h3>

            <hr style="margin:20px 0;">

            <!-- SUMMARY ICON LIST -->
            <h3>Total RFQs in Reminder: {summary.get("TOTAL", "N/A")}</h3>

            <ul style="list-style:none; padding-left:0; font-size:15px; line-height:24px;">
                <li>{ICONS['HIGH']} High Priority: {g("HIGH", summary)}</li>
                <li>{ICONS['MEDIUM']} Medium Priority: {g("MEDIUM", summary)}</li>
                <li>{ICONS['LOW']} Low Priority: {g("LOW", summary)}</li>
                <li>{ICONS['VENDOR_PENDING']} Vendors Not Responded: {g("VENDOR_PENDING", summary)}</li>
                <li>{ICONS['QUOTATION_RECEIVED']} Quotation Received: {g("QUOTATION_RECEIVED", summary)}</li>
                <li>{ICONS['CLIENT_CLARIFICATIONS']} Client Clarifications: {g("CLIENT_CLARIFICATIONS", summary)}</li>
                <li>{ICONS['POST_OFFER']} Post-Offer Client Queries: {g("POST_OFFER", summary)}</li>
                <li>{ICONS['OVERDUE']} Overdue RFQs: {g("OVERDUE", summary)}</li>
            </ul>

            <hr style="margin:25px 0;">

            <!-- HIGH PRIORITY -->
            <h3>{ICONS['HIGH']} High Priority</h3>
            <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
                <tr style="background:#f2f2f2; font-weight:bold;">
                    <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                    <td>Days Overdue</td><td>Next Step</td>
                </tr>
                {high_table}
            </table>

            <!-- MEDIUM -->
            <h3 style="margin-top:40px;">{ICONS['MEDIUM']} Medium Priority</h3>
            <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
                <tr style="background:#f2f2f2; font-weight:bold;">
                    <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                    <td>Days Overdue</td><td>Next Step</td>
                </tr>
                {medium_table}
            </table>

            <!-- LOW -->
            <h3 style="margin-top:40px;">{ICONS['LOW']} Low Priority</h3>
            <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
                <tr style="background:#f2f2f2; font-weight:bold;">
                    <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                    <td>Days Overdue</td><td>Next Step</td>
                </tr>
                {low_table}
            </table>

            <!-- VENDOR PENDING -->
            <h3 style="margin-top:40px;">{ICONS['VENDOR_PENDING']} Vendor Pending</h3>
            <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
                <tr style="background:#f2f2f2; font-weight:bold;">
                    <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                    <td>Pending Since</td><td>Next Step</td>
                </tr>
                {vendor_table}
            </table>

            <!-- QUOTATION RECEIVED -->
            <h3 style="margin-top:40px;">{ICONS['QUOTATION_RECEIVED']} Quotation Received</h3>
            <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
                <tr style="background:#f2f2f2; font-weight:bold;">
                    <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td><td>Next Step</td>
                </tr>
                {quotation_table}
            </table>

            <!-- CLIENT CLARIFICATIONS -->
            <h3 style="margin-top:40px;">{ICONS['CLIENT_CLARIFICATIONS']} Client Clarifications</h3>
            <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
                <tr style="background:#f2f2f2; font-weight:bold;">
                    <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td><td>Next Step</td>
                </tr>
                {clarification_table}
            </table>

            <!-- POST-OFFER -->
            <h3 style="margin-top:40px;">{ICONS['POST_OFFER']} Post-Offer Client Queries</h3>
            <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
                <tr style="background:#f2f2f2; font-weight:bold;">
                    <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td><td>Next Step</td>
                </tr>
                {post_offer_table}
            </table>

            <!-- OVERDUE -->
            <h3 style="margin-top:40px;">{ICONS['OVERDUE']} Overdue (≤10 days)</h3>
            <table width="100%" style="border-collapse:collapse; border:1px solid #ddd;">
                <tr style="background:#f2f2f2; font-weight:bold;">
                    <td>RFQ No</td><td>UID No</td><td>Customer</td><td>Due Date</td>
                    <td>Days Overdue</td><td>Next Step</td>
                </tr>
                {overdue_table}
            </table>

        </div>
    </body>
    </html>
    """

    return html


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
            "engine_summary": engine_output.get("summary"),
            "sections": list(engine_output.get("sections", {}).keys()),
            "send_result": send_result
        }

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex) + "\n" + traceback.format_exc()
        )
