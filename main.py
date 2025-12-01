
from logger import get_logger
from sheet_reader import read_rows
from logic_engine import run_engine
from sheet_writer import write_updates
from templates import build_email
from email_sender import send_email

def main():
    log=get_logger()
    log.info("Starting Level-50 Engine")

    rows=read_rows()
    log.info(f"Read {len(rows)} rows")

    processed=run_engine(rows)
    log.info(f"Processed {len(processed)} rows")

    write_updates(processed)
    log.info("Sheet updated")

    subject,body=build_email(processed)
    send_email(subject,body)
    log.info("Emails sent")

if __name__=="__main__":
    main()
