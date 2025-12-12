import re

# ---------------------------------------------------------
# STATUS PATTERN GROUPS (LEVEL-70 + MINI 4.1)
# ---------------------------------------------------------

PATTERNS = {
    "WON": [
        r"order\s+received",
        r"order\s+confirmed",
        r"po\s+given",
        r"po\s+received",
        r"converted\s+to\s+po",
        r"won",
        r"customer\s+confirmed"
    ],
    "LOST": [
        r"order\s+lost",
        r"lost",
        r"closed\s+lost",
        r"not\s+selected",
        r"not\s+considered",
        r"rejected",
        r"no\s+longer\s+required",
        r"cancelled"
    ],
    "SUBMITTED": [
        r"submitted",
        r"offer\s+submitted",
        r"quotation\s+sent",
        r"attached\s+quotation",
        r"offer\s+shared",
        r"mail\s+sent",
        r"sent\s+quotation"
    ],
    "QUERY": [
        r"discount",
        r"clarification",
        r"query",
        r"need\s+revision",
        r"need\s+revised",
        r"need\s+breakdown",
        r"need\s+validity",
        r"please\s+revise",
        r"technical\s+clarification",
        r"delivery\s+clarification"
    ],
    "HOLD": [
        r"put\s+on\s+hold",
        r"keep\s+on\s+hold",
        r"customer\s+on\s+hold",
        r"hold\s+due\s+to",
        r"budget\s+issue"
    ],
    "FOLLOW-UP": [
        r"waiting\s+for\s+customer",
        r"follow\s+up\s+required",
        r"pending\s+from\s+client",
        r"awaiting\s+response",
        r"no\s+response",
        r"client\s+not\s+responding"
    ]
}


# ---------------------------------------------------------
# MAIN STATUS CLASSIFIER
# ---------------------------------------------------------

def classify_status(raw_text: str) -> str:
    """
    Reads raw text from AI output and assigns the correct 
    Level-70 status (WON / LOST / SUBMITTED / QUERY / HOLD / FOLLOW-UP)
    """

    if not raw_text:
        return ""

    text = raw_text.lower().strip()

    # Priority-based scanning
    for status, patterns in PATTERNS.items():
        for p in patterns:
            if re.search(p, text):
                return status

    # Default fallback
    return "SUBMITTED"
