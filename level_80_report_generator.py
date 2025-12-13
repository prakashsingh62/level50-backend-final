# =========================================
# Level-80 Report Generator (Phase-1)
# Daily + Weekly Proof Reports
# =========================================

import json
import os
import datetime
from collections import defaultdict

AUDIT_LOG_FILE = "level_80_audit_log.jsonl"
REPORT_DIR = "reports"


def _parse_ts(ts: str):
    return datetime.datetime.strptime(ts, "%d/%m/%Y %H:%M:%S IST")


def _ensure_dirs():
    os.makedirs(f"{REPORT_DIR}/daily", exist_ok=True)
    os.makedirs(f"{REPORT_DIR}/weekly", exist_ok=True)


def _load_audit_logs():
    if not os.path.exists(AUDIT_LOG_FILE):
        return []

    records = []
    with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


# -------------------------------------------------
# DAILY REPORT
# -------------------------------------------------
def generate_daily_report(target_date=None):
    _ensure_dirs()
    records = _load_audit_logs()

    if target_date is None:
        target_date = datetime.date.today()

    daily_records = [
        r for r in records
        if _parse_ts(r["timestamp"]).date() == target_date
    ]

    rows = []
    for r in daily_records:
        rows.extend(r["payload"].get("affected_rows", []))

    report = {
        "date": target_date.strftime("%d/%m/%Y"),
        "total_updates": len(daily_records),
        "rows_updated": sorted(set(rows)),
        "generated_at": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S IST")
    }

    file_path = f"{REPORT_DIR}/daily/report_{target_date.strftime('%d-%m-%Y')}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return file_path


# -------------------------------------------------
# WEEKLY REPORT (Mon–Sun)
# -------------------------------------------------
def generate_weekly_report(reference_date=None):
    _ensure_dirs()
    records = _load_audit_logs()

    if reference_date is None:
        reference_date = datetime.date.today()

    start = reference_date - datetime.timedelta(days=reference_date.weekday())
    end = start + datetime.timedelta(days=6)

    bucket = defaultdict(int)

    for r in records:
        d = _parse_ts(r["timestamp"]).date()
        if start <= d <= end:
            bucket[d.strftime("%d/%m/%Y")] += 1

    report = {
        "week_range": f"{start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}",
        "daily_breakdown": dict(bucket),
        "total_updates": sum(bucket.values()),
        "generated_at": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S IST")
    }

    file_path = (
        f"{REPORT_DIR}/weekly/"
        f"report_week_{start.strftime('%d-%m')}_{end.strftime('%d-%m_%Y')}.json"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return file_path
