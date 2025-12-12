import json
import os
from utils.sheet_updater import update_rfq_row

PENDING_FILE = "retry_queue/pending.json"
ERROR_FILE = "retry_queue/error_log.json"

MAX_RETRIES = 10


# ------------------------------------------------------------
# LOAD / SAVE HELPERS
# ------------------------------------------------------------
def load_queue():
    if not os.path.exists(PENDING_FILE):
        return []
    try:
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_queue(queue):
    with open(PENDING_FILE, "w") as f:
        json.dump(queue, f, indent=4)


def log_error(item):
    logs = []
    if os.path.exists(ERROR_FILE):
        try:
            with open(ERROR_FILE, "r") as f:
                logs = json.load(f)
        except:
            logs = []

    logs.append(item)

    with open(ERROR_FILE, "w") as f:
        json.dump(logs, f, indent=4)


# ------------------------------------------------------------
# ADD TASK
# ------------------------------------------------------------
def queue_retry(item):
    queue = load_queue()
    queue.append(item)
    save_queue(queue)


# ------------------------------------------------------------
# RETRY ENGINE (RUNS IN CRON EVERY 5 MINUTES)
# ------------------------------------------------------------
def retry_worker():
    queue = load_queue()
    if not queue:
        return {"status": "empty"}

    still_pending = []

    for item in queue:
        retry_count = item.get("retry_count", 0)

        # Max retry attempts reached
        if retry_count >= MAX_RETRIES:
            item["error"] = "Max retries exceeded"
            log_error(item)
            continue

        try:
            if item.get("type") == "sheet_update":
                update_rfq_row(item["row"], item["payload"])

            else:
                item["error"] = f"Unknown task type: {item.get('type')}"
                log_error(item)
                continue

        except Exception as e:
            # Retain task for retry
            item["retry_count"] = retry_count + 1
            item["last_error"] = str(e)
            still_pending.append(item)
            continue

    save_queue(still_pending)

    return {
        "status": "processed",
        "remaining": len(still_pending)
    }
