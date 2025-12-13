# ------------------------------------------------------------
# LEVEL-70 RULE CONFIG (EDIT ANYTIME, NO CRASH)
# ------------------------------------------------------------

rules = {

    # --------------------------------------------------------
    # STATUS ENGINE RULES
    # --------------------------------------------------------
    "status_rules": {
        "keywords": {
            "won": ["order confirmed", "po attached", "po released"],
            "lost": ["not approved", "rejected", "lost", "not considered"],
            "submitted": ["attached quotation", "sending offer", "quotation attached"],
            "query": ["clarification", "discount", "revise", "revision", "gad", "final price"]
        },
        "default": "submitted"   # fallback status
    },

    # --------------------------------------------------------
    # FOLLOW-UP ENGINE RULES
    # --------------------------------------------------------
    "followup_rules": {
        "high_value_limit": 500000,
        "default_followup_offset": 2,     # days
        "query_offset": 1,               # follow-up after 1 day for query/revision
        "submitted_offset": 2,
        "revised_offer_offset": 1
    },

    # --------------------------------------------------------
    # MATCHING RULES (STEP-3)
    # --------------------------------------------------------
    "matching_rules": {
        "skip_concern_person": ["NP"],    # NP rows must be skipped
        "rfq_column": 4,                  # Column E (0-indexed)
        "uid_column": 7                   # Column H (0-indexed)
    },

    # --------------------------------------------------------
    # VENDOR QUERY DETECTION
    # --------------------------------------------------------
    "vendor_query_rules": {
        "keywords": ["discount", "clarification", "revise", "revision", "gad", "final price"],
        "gad_keywords": ["gad", "drawing", "outline", "dimension"],
        "price_keywords": ["final price", "best price", "lowest", "discount"],
        "needs_vendor_mail": True
    },

    # --------------------------------------------------------
    # COLUMN MAPPINGS FOR SHEET UPDATE
    # --------------------------------------------------------
    "column_map": {
        "vendor_status": 33,
        "quotation_date": 19,
        "remarks": 34,
        "followup_date": 35
    }

}
