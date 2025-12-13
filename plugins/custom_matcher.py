# ---------------------------------------------------------
# CUSTOM MATCHER PLUGIN (Optional Override)
# ---------------------------------------------------------
# Return:
# - custom match result dict
# - OR None to use the default Level-70 matcher
# ---------------------------------------------------------

def custom_matcher(ai_output, sheet_rows):
    """
    Add your custom RFQ/UID matching logic here.
    Returning None → fallback to default matcher.
    """
    return None
