# ------------------------------------------------------------
# PHASE 11 RUNNER — FINAL HARD-SAFE
# MATCHES main_server.py IMPORT
# ------------------------------------------------------------

from pipeline_engine import pipeline


def run_phase11_background(trace_id: str, payload: dict):
    """
    This function name MUST exist.
    main_server.py imports this directly.
    """

    processed = 0
    status = "FAILED"
    error = None

    try:
        result = pipeline.run(payload)
        processed = result.get("processed", 0)
        status = "OK"

    except Exception as e:
        error = str(e)

    return {
        "trace_id": trace_id,
        "status": status,
        "processed": processed,
        "error": error
    }
