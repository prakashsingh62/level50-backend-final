import traceback
from sheet_reader import read_rows
from logic_engine import process_sheet
from email_builder import build_email_html
from email_sender import send_email


# ----------------------------------------------------
# DAILY REMINDER ENTRYPOINT
# This must run ONCE and exit immediately.
# ----------------------------------------------------
def run_daily_sender():
    try:
        print("Daily sender started...")

        # 1) Read all rows from Google Sheet
        rows = read_rows()
        print(f"Loaded {len(rows)} rows")

        # 2) Process logic
        result = process_sheet(rows)
        summary = result["summary"]
        sections = result["sections"]

        # 3) Build HTML
        html = build_email_html(summary, sections)
        print("HTML email generated")

        # 4) Send the email
        send_email(
            subject="Daily RFQ Reminder",
            html_content=html
        )

        print("Daily sender completed successfully.")

    except Exception as e:
        print("ERROR in daily sender:", e)
        traceback.print_exc()


# ----------------------------------------------------
# Ensure Railway Cron executes directly and exits.
# ----------------------------------------------------
if __name__ == "__main__":
    run_daily_sender()
