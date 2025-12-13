# --------------------------------------------------------
# TURBO UPGRADE 2 — Batch Writer + Parallel Executor +
# Real-Time Performance Logger
# --------------------------------------------------------

from concurrent.futures import ThreadPoolExecutor
import time

executor = ThreadPoolExecutor(max_workers=5)


# --------------------------------------------------------
# PERFORMANCE LOGGING
# --------------------------------------------------------
def turbo_log(message):
    print(f"[TURBO] {message}")


# --------------------------------------------------------
# PARALLEL TASK HELPER
# --------------------------------------------------------
def run_parallel(tasks: list):
    """
    tasks = [function, function, function]
    Runs all functions in parallel.
    """
    futures = [executor.submit(fn) for fn in tasks]
    return [f.result() for f in futures]


# --------------------------------------------------------
# BATCH WRITER FOR MULTI-ROW UPDATES
# --------------------------------------------------------
def build_bulk_update_requests(rows_data):
    """
    rows_data = [
      { "row": 20, "updates": {"vendor_status": "...", ... } },
      { "row": 55, "updates": {...} }
    ]
    """
    requests = []

    for item in rows_data:
        row_index = item["row"] - 1
        updates = item["updates"]

        if "vendor_status" in updates:
            requests.append({
                "updateCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": row_index,
                        "endRowIndex": row_index + 1,
                        "startColumnIndex": 33,
                        "endColumnIndex": 34
                    },
                    "rows": [
                        {"values": [{"userEnteredValue": {"stringValue": updates["vendor_status"]}}]}
                    ],
                    "fields": "userEnteredValue"
                }
            })

        if "quotation_date" in updates:
            requests.append({
                "updateCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": row_index,
                        "endRowIndex": row_index + 1,
                        "startColumnIndex": 19,
                        "endColumnIndex": 20
                    },
                    "rows": [
                        {"values": [{"userEnteredValue": {"stringValue": updates["quotation_date"]}}]}
                    ],
                    "fields": "userEnteredValue"
                }
            })

        if "remarks" in updates:
            requests.append({
                "updateCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": row_index,
                        "endRowIndex": row_index + 1,
                        "startColumnIndex": 34,
                        "endColumnIndex": 35
                    },
                    "rows": [
                        {"values": [{"userEnteredValue": {"stringValue": updates["remarks"]}}]}
                    ],
                    "fields": "userEnteredValue"
                }
            })

        if "followup_date" in updates:
            requests.append({
                "updateCells": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": row_index,
                        "endRowIndex": row_index + 1,
                        "startColumnIndex": 35,
                        "endColumnIndex": 36
                    },
                    "rows": [
                        {"values": [{"userEnteredValue": {"stringValue": updates["followup_date"]}}]}
                    ],
                    "fields": "userEnteredValue"
                }
            })

    return requests
