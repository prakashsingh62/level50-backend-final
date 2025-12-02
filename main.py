from logger import get_logger
from sheet_reader import read_rows
from logic_engine import run_engine
from sheet_writer import write_updates
from templates import build_email
from email_sender import send_email
import sys
import time
import traceback

RETRY_ATTEMPTS = 2
RETRY_DELAY = 2  # seconds

def _retry(fn, attempts=RETRY_ATTEMPTS, delay=RETRY_DELAY, *args, **kwargs):
    last_exc = None
    for i in range(1, attempts + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_exc = e
            logger = get_logger()
            logger.warning(f"Attempt {i} for {fn.__name__} failed: {e}")
            if i < attempts:
                time.sleep(delay)
    # re-raise the last exception
    raise last_exc

def main():
    log = get_logger()
    log.info("Starting Level-50 Engine")

    try:
        rows = _retry(read_rows)
        log.info(f"Read {len(rows)} rows")

        processed = run_engine(rows)
        if processed is None:
            log.error("run_engine returned None — aborting")
            sys.exit(2)
        log.info(f"Processed {len(processed)} rows")

        # Apply updates only if there is something to update
        if processed:
            _retry(write_updates, args=(processed,))
            log.info("Sheet updated")
        else:
            log.info("No rows to update — skipping sheet write")

        # Build & send email only if there is content
        if processed:
            email_result = build_email(processed)
            if not email_result or not isinstance(email_result, (list, tuple)) or len(email_result) != 2:
                log.error("build_email did not return (subject, body) — skipping send")
            else:
                subject, body = email_result
                _retry(send_email, args=(subject, body))
                log.info("Emails sent")
        else:
            log.info("No processed rows — skipping email build/send")

    except Exception as e:
        # Log full traceback for debugging
        log.error("Fatal error in main(): %s", str(e))
        tb = traceback.format_exc()
        log.debug(tb)
        # Exit non-zero so process managers / Railway detect failure
        sys.exit(1)

if __name__ == "__main__":
    main()
