import re

# ---------------------------------------------------------------------
# LEVEL-70 RULE:
# NP rows must be skipped ONLY by the automation pipeline.
#
# - ANY USER with Google Sheet access can manually edit NP rows.
# - Automation (AI) must NEVER match, process, or update NP rows.
#
# This Hard Skip Rule ensures automation ignores NP rows, while
# manual edits in Google Sheets remain fully allowed and unrestricted.
# ---------------------------------------------------------------------


# ---------------------------------------------------------
# NORMALIZATION HELPERS
# ---------------------------------------------------------

def normalize_rfq(rfq_raw: str) -> str:
    if not rfq_raw:
        return ""
    rfq = rfq_raw.strip().upper().replace(" ", "").replace("RFQ", "")
    rfq = re.sub(r"[^0-9]", "", rfq)
    return rfq


def normalize_uid(uid_raw: str) -> str:
    if not uid_raw:
        return ""
    uid = uid_raw.strip().upper()
    uid = uid.replace("UID", "").replace("/", "").replace("-", "")
    uid = re.sub(r"[^0-9]", "", uid)
    return uid


# ---------------------------------------------------------
# MATCHING ENGINE — MAIN FUNCTION
# ---------------------------------------------------------

def find_matching_row(rows, input_rfq: str, input_uid: str):
    norm_rfq = normalize_rfq(input_rfq)
    norm_uid = normalize_uid(input_uid)

    uid_matches = []
    rfq_matches = []

    # -----------------------------------------------------
    # SCAN ALL ROWS
    # -----------------------------------------------------
    for idx, row in enumerate(rows, start=1):

        # Skip short rows
        if len(row) < 12:
            continue

        # --------------------------------------------------
        # HARD SKIP RULE — Automation must NOT touch NP rows
        # --------------------------------------------------
        try:
            concern_person = row[11].strip().upper()
        except:
            concern_person = ""

        if concern_person == "NP":
            continue

        # Extract normalized sheet values
        sheet_rfq = normalize_rfq(row[4]) if len(row) > 4 else ""
        sheet_uid = normalize_uid(row[7]) if len(row) > 7 else ""

        # UID highest priority
        if norm_uid and sheet_uid == norm_uid:
            uid_matches.append(idx)

        # RFQ match
        if norm_rfq and sheet_rfq == norm_rfq:
            rfq_matches.append(idx)

    # -----------------------
    # MATCH PRIORITY LOGIC
    # -----------------------

    if len(uid_matches) == 1:
        row_num = uid_matches[0]
        if row_num in rfq_matches:
            return {
                "status": "success",
                "row": row_num,
                "confidence": 1.0,
                "matched_by": "BOTH",
                "reason": "UID + RFQ matched"
            }
        return {
            "status": "success",
            "row": row_num,
            "confidence": 0.95,
            "matched_by": "UID",
            "reason": "Matched by UID"
        }

    if len(uid_matches) > 1:
        return {"status": "multiple", "row": None, "confidence": 0, "matched_by": "UID"}

    if len(rfq_matches) == 1:
        return {
            "status": "success",
            "row": rfq_matches[0],
            "confidence": 0.85,
            "matched_by": "RFQ"
        }

    if len(rfq_matches) > 1:
        return {"status": "multiple", "row": None, "matched_by": "RFQ"}

    return {
        "status": "not_found",
        "row": None,
        "matched_by": "NONE",
        "reason": "No RFQ/UID match found (NP rows skipped)"
    }
