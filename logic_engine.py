# logic_engine.py
from classify import classify_rows

def normalize_summary(summary):
    """
    Ensures summary dict always has identical keys for HTML.
    Missing keys become empty lists.
    """
    expected_keys = [
        "high_priority",
        "medium_priority",
        "low_priority",
        "vendor_pending",
        "client_followup",
        "overdue"
    ]

    normalized = {}
    for key in expected_keys:
        normalized[key] = summary.get(key, [])

    return normalized


def normalize_sections_for_email(sections):
    """
    Guarantees section order + formatting for identical HTML output.
    """
    ordered_keys = [
        "High Priority",
        "Medium Priority",
        "Low Priority",
        "Vendor Pending",
        "Client Follow-up",
        "Overdue"
    ]

    normalized = {}
    for key in ordered_keys:
        normalized[key] = sections.get(key, [])

    return normalized


def process_sheet(rows):
    """
    Main Level-50 Logic Engine
    Step 1 → Classify rows using classify.py
    Step 2 → Normalize keys for identical HTML output
    Step 3 → Return standardized format for routers + email sender
    """

    # Step 1 — classify
    summary, sections = classify_rows(rows)

    # Step 2 — normalize for HTML
    summary = normalize_summary(summary)
    sections = normalize_sections_for_email(sections)

    # Step 3 — final output (FIXED BRACKET)
    return {
        "summary": summary,
        "sections": sections
    }


def run_level50(rows):
    """
    Backward-compatibility wrapper.
    Older routers expect run_level50() to exist.
    """
    return process_sheet(rows)
