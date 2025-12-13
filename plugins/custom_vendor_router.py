# ---------------------------------------------------------
# CUSTOM VENDOR ROUTER PLUGIN
# ---------------------------------------------------------
# Use to reroute vendor queries in custom ways.
# Returning None → use built-in vendor detection logic.
# ---------------------------------------------------------

def custom_vendor_router(ai_output, match_result):
    """
    Add your vendor detection/selection override logic.
    Returning None → fallback to default vendor_router.
    """
    return None
