import re

# ---------------------------------------------------------
# PATTERNS THAT REQUIRE VENDOR INVOLVEMENT
# ---------------------------------------------------------

VENDOR_QUERY_KEYWORDS = [
    r"\bgad\b",
    r"general\s+arrangement",
    r"final\s+price",
    r"best\s+price",
    r"revised\s+boq",
    r"technical\s+clarification",
    r"tech\s+clarification",
    r"technical\s+details",
    r"delivery\s+clarification",
    r"delivery\s+schedule",
    r"datasheet",
    r"drawing",
    r"spec",
    r"specification",
]


# ---------------------------------------------------------
# CHECK IF QUERY NEEDS VENDOR
# ---------------------------------------------------------

def requires_vendor(raw_text: str) -> bool:
    """
    Determines if customer's query must be forwarded to a vendor.
    """
    if not raw_text:
        return False

    t = raw_text.lower()

    for pattern in VENDOR_QUERY_KEYWORDS:
        if re.search(pattern, t):
            return True

    return False


# ---------------------------------------------------------
# EXTRACT VENDOR EMAIL FROM MAIL THREAD
# ---------------------------------------------------------

def extract_vendor_email(vendor_name: str, thread_emails: list) -> str:
    """
    thread_emails structure:
    [
        { "from": "abc@vendor.com", "body": "...", "timestamp": 1689402000 },
        ...
    ]

    Returns the most recent email sent by vendor.
    """

    vendor_name_lower = vendor_name.lower()

    # 1) Most recent vendor email (sorted by timestamp descending)
    for mail in sorted(thread_emails, key=lambda x: x.get("timestamp", 0), reverse=True):
        sender = mail.get("from", "").lower()
        if vendor_name_lower in sender:
            return sender

    # 2) Partial match fallback (e.g., vendor name first word)
    if vendor_name_lower:
        first_word = vendor_name_lower.split()[0]
        for mail in thread_emails:
            sender = mail.get("from", "").lower()
            if first_word in sender:
                return sender

    return ""  # not found


# ---------------------------------------------------------
# CREATE VENDOR MAIL PAYLOAD
# ---------------------------------------------------------

def build_vendor_mail(rfq_no: str, uid_no: str, vendor_email: str, customer_query: str):
    """
    Returns a dictionary to be used by email_builder (only AFTER confirmation).
    """
    
    subject = f"Query from Customer – RFQ {rfq_no} / UID {uid_no}"

    body = (
        f"Dear Vendor,\n\n"
        f"We have received the following query from the customer for RFQ {rfq_no} / UID {uid_no}:\n\n"
        f"\"{customer_query}\"\n\n"
        f"Request you to kindly provide the required clarification/information at the earliest.\n\n"
        f"Regards,\n"
        f"Inside Sales Team\n"
    )

    return {
        "to": vendor_email,
        "subject": subject,
        "body": body,
        "rfq": rfq_no,
        "uid": uid_no,
    }


# ---------------------------------------------------------
# MAIN ROUTER ENGINE (LEVEL-70)
# ---------------------------------------------------------

def vendor_query_router(ai_text: str, matched_row: dict, thread_emails: list):
    """
    ai_text       → AI parsed text from customer email
    matched_row   → output from Step-3:
                     {
                        "row": 12,
                        "vendor_name": "KSB",
                        "rfq": "202400123",
                        "uid": "45098"
                     }
    thread_emails → all vendor messages in same thread

    RETURNS (always with confirmation gate):
    {
       "requires_vendor": True/False,
       "status": "awaiting_confirmation" | "no_vendor_needed",
       "vendor_email": "abc@vendor.com",
       "mail_payload": {},
       "error": ""
    }
    """

    # -----------------------------------------------------
    # 1) Check whether vendor involvement is needed
    # -----------------------------------------------------

    if not requires_vendor(ai_text):
        return {
            "requires_vendor": False,
            "status": "no_vendor_needed",
            "vendor_email": "",
            "mail_payload": {},
            "error": ""
        }

    # -----------------------------------------------------
    # 2) Extract vendor info from sheet (matched_row)
    # -----------------------------------------------------

    vendor_name = matched_row.get("vendor_name", "")
    rfq_no = matched_row.get("rfq", "")
    uid_no = matched_row.get("uid", "")

    # -----------------------------------------------------
    # 3) Extract vendor email from mailbox thread
    # -----------------------------------------------------

    vendor_email = extract_vendor_email(vendor_name, thread_emails)

    if not vendor_email:
        return {
            "requires_vendor": True,
            "status": "awaiting_confirmation",
            "vendor_email": "",
            "mail_payload": {},
            "error": "vendor_email_missing"
        }

    # -----------------------------------------------------
    # 4) Build vendor mail payload (NOT SENT — confirmation required)
    # -----------------------------------------------------

    mail_payload = build_vendor_mail(
        rfq_no=rfq_no,
        uid_no=uid_no,
        vendor_email=vendor_email,
        customer_query=ai_text
    )

    return {
        "requires_vendor": True,
        "status": "awaiting_confirmation",   # Confirmation gate ON
        "vendor_email": vendor_email,
        "mail_payload": mail_payload,
        "error": ""
    }
