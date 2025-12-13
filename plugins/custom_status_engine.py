# ---------------------------------------------------------
# CUSTOM STATUS ENGINE PLUGIN
# ---------------------------------------------------------
# Use this to override WON/LOST/SUBMITTED/QUERY logic
# Returning None → default status engine runs.
# ---------------------------------------------------------

def custom_status_engine(ai_output, match_result):
    """
    Add custom status determination logic.
    Return a status dict or None for fallback.
    """
    return None
