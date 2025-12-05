# logic_engine.py
# COMPLETE PATCHED VERSION (FINAL)

from classify import classify_rows


def normalize_sections_for_email(sections: dict) -> dict:
    """
    Guarantee consistent ordering and naming of sections for both
    Daily and Manual Reminder emails.
    """

    return {
        "HIGH": sections.get("HIGH", []),
        "MEDIUM": sections.get("MEDIUM", []),
        "LOW": sections.get("LOW", []),

        # Vendor Pending may exist under 2 possible keys depending on logic engine version
        "VENDOR_PENDING": sections.get(
            "VENDOR_PENDING",
            sections.get("VENDORS_NOT_RESPONDED", [])
        ),

        "QUOTATION_RECEIVED": sections.get("QUOTATION_RECEIVED", []),
        "CLIENT_CLARIFICATIONS": sections.get("CLIENT_CLARIFICATIONS", []),

        # Some older logic engines used POST_OFFER instead of POST_OFFER_QUERIES
        "POST_OFFER_QUERIES": sections.get(
            "POST_OFFER_QUERIES",
            sections.get("POST_OFFER", [])
        ),

        "OVERDUE": sections.get("OVERDUE", []),
    }


def normalize_summary(summary: dict) -> dict:
    """
    Guarantee summary keys always exist to avoid KeyError and 
    ensure daily + manual emails stay identical.
    """

    return {
        "HIGH": summary.get("HIGH", 0),
        "MEDIUM": summary.get("MEDIUM", 0),
        "LOW": summary.get("LOW", 0),

        "VENDOR_PENDING": summary.get(
            "VENDOR_PENDING",
            summary.get("VENDORS_NOT_RESPONDED", 0)
        ),

        "QUOTATION_RECEIVED": summary.get("QUOTATION_RECEIVED", 0),
        "CLIENT_CLARIFICATIONS": summary.get("CLIENT_CLARIFICATIONS", 0),

        "POST_OFFER_QUERIES": summary.get(
            "POST_OFFER_QUERIES",
            summary.get("POST_OFFER", 0)
        ),

        "OVERDUE": summary.get("OVERDUE", 0),
    }


def process_sheet(rows):
    """
    Main Logic Engine for Level-50/51.
    Input: raw sheet rows list
    Output: { summary, sections }
    """

    # Step 1 — Classify using your classify.py logic
    summary, sections = classify_rows(rows)

    # Step 2 — Normalize keys so HTML output is always identical
    summary = normalize_summary(summary)
    sections = normalize_sections_for_email(sections)

    # Step 3 — Output is now standardized for email + router usage
    return {
        "summary": summary,
        "sections": sections
    }
