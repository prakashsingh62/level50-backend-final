"""
Drop-in replacement for logic_engine.py
Level-51 ready: defensive, auto-correcting, safe-run wrapper.

Usage:
    from logic_engine import run_level50
    run_level50(debug=True)
"""

from datetime import datetime
from typing import List, Dict, Tuple, Any
import traceback

# Keep original imports/contract
from sheet_reader import read_sheet
from classify import classify_rows


# --- Helpers --------------------------------------------------------------

COMMON_DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d",
    "%d/%m/%y", "%d-%b-%Y", "%d %b %Y",
    "%d.%m.%Y", "%m/%d/%Y"
]


def try_parse_date(value: Any) -> Tuple[Any, bool]:
    """
    Try multiple date formats and return standardized ISO date string 'YYYY-MM-DD'
    If parsing fails, return original value and False.
    """
    if value is None:
        return (None, False)
    v = str(value).strip()
    if v == "":
        return (None, False)
    # If already ISO-looking
    try:
        # handle already ISO or YYYY-MM-DD
        parsed = datetime.fromisoformat(v)
        return (parsed.date().isoformat(), True)
    except Exception:
        pass

    for fm in COMMON_DATE_FORMATS:
        try:
            parsed = datetime.strptime(v, fm)
            return (parsed.date().isoformat(), True)
        except Exception:
            continue
    # last ditch: try to parse only digits like DDMMYYYY or DDMMyy
    digits = "".join(ch for ch in v if ch.isdigit())
    if len(digits) in (6, 8):
        try:
            if len(digits) == 8:
                parsed = datetime.strptime(digits, "%d%m%Y")
            else:
                parsed = datetime.strptime(digits, "%d%m%y")
            return (parsed.date().isoformat(), True)
        except Exception:
            pass
    return (value, False)


def coerce_number(value: Any) -> Tuple[Any, bool]:
    """
    Try to coerce numeric-looking strings into float/int. Return (coerced, True) or (original, False).
    """
    if value is None:
        return (None, False)
    v = str(value).strip().replace(",", "")
    if v == "":
        return (None, False)
    try:
        if "." in v:
            return (float(v), True)
        else:
            return (int(v), True)
    except Exception:
        try:
            return (float(v), True)
        except Exception:
            return (value, False)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


# --- Row validation & auto-correction ------------------------------------

def clean_and_validate_row(row: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Return (cleaned_row, diagnostics)
    diagnostics contains keys: fixed_fields (list), invalid_fields (list), actions (list)
    """
    cleaned = {}
    diagnostics = {"fixed_fields": [], "invalid_fields": [], "actions": []}

    # Copy & normalize keys => uppercase keys to be robust to casing
    for k, v in row.items():
        key = str(k).strip()
        cleaned[key] = v

    # Trim and normalize commonly used fields (case-insensitive access)
    def g(field):
        # return original key if exists (best effort)
        for candidate in (field, field.upper(), field.lower(), field.title()):
            if candidate in cleaned:
                return candidate
        # fallback: return field as-is (may not exist)
        return field

    # CONCERN PERSON handling
    cp_key = g("CONCERN PERSON")
    cp_val = normalize_text(cleaned.get(cp_key, "")).upper()
    if cp_val == "NP":
        diagnostics["actions"].append("SKIP_NP")
        cleaned["_LEVEL51_SKIP"] = True
        return (cleaned, diagnostics)  # skip further cleaning for NP rows

    # DATES: RFQ DATE, UID DATE, DUE DATE
    for df in ("RFQ DATE", "UID DATE", "DUE DATE"):
        k = g(df)
        raw = cleaned.get(k, None)
        parsed, ok = try_parse_date(raw)
        if ok:
            if parsed != raw:
                diagnostics["fixed_fields"].append(df)
                cleaned[k] = parsed
        else:
            # if missing due date, mark invalid - but do not crash
            if raw in (None, "", "None"):
                diagnostics["invalid_fields"].append(df)
                cleaned[k] = None
            else:
                # keep original but flag
                diagnostics["invalid_fields"].append(df)
                cleaned[k] = raw

    # NUMERIC fields: attempt coercion for common numeric-like fields
    for nf in ("RFQ VALUE", "QUANTITY", "PRICE", "UID NO"):
        k = g(nf)
        if k in cleaned:
            coerced, ok = coerce_number(cleaned.get(k))
            if ok:
                cleaned[k] = coerced
                diagnostics["fixed_fields"].append(k)
            else:
                # keep original but note
                diagnostics.setdefault("non_numeric", []).append(k)

    # VENDOR normalization
    v_key = g("VENDOR")
    vendor_raw = normalize_text(cleaned.get(v_key, ""))
    if vendor_raw == "":
        # leave blank but flag for possible human review
        diagnostics["invalid_fields"].append("VENDOR")
    else:
        cleaned[v_key] = vendor_raw

    # SALES PERSON normalization
    sp_key = g("SALES PERSON")
    sp = normalize_text(cleaned.get(sp_key, ""))
    cleaned[sp_key] = sp

    # Standard metadata
    cleaned["_LEVEL51_AUTOFIXED"] = bool(diagnostics["fixed_fields"])
    cleaned["_LEVEL51_INVALID_FIELDS"] = diagnostics["invalid_fields"]
    cleaned["_LEVEL51_ACTIONS"] = diagnostics["actions"]

    # final return
    return (cleaned, diagnostics)


# --- Main runner ---------------------------------------------------------

def run_level50(debug: bool = False) -> Dict[str, Any]:
    """
    Safe wrapper around existing pipeline:
      - reads sheet
      - runs cleaning/auto-fix
      - filters/skips invalid rows safely
      - calls classify_rows on cleaned rows
    Returns structured summary and sections.
    """
    start_time = datetime.utcnow()
    try:
        raw_rows = read_sheet()
    except Exception as e:
        # fatal read failure — return error status with traceback
        tb = traceback.format_exc()
        return {
            "status": "error",
            "error": "read_sheet_failed",
            "message": str(e),
            "traceback": tb
        }

    cleaned_rows: List[Dict[str, Any]] = []
    diagnostics_list = []
    counts = {
        "total": len(raw_rows),
        "skipped_np": 0,
        "autofixed": 0,
        "invalid": 0,
        "kept": 0,
        "errors": 0
    }

    for idx, r in enumerate(raw_rows):
        try:
            cleaned, diag = clean_and_validate_row(r)
            diagnostics_list.append(diag)
            # Skip NP rows
            if cleaned.get("_LEVEL51_SKIP"):
                counts["skipped_np"] += 1
                continue

            if cleaned.get("_LEVEL51_AUTOFIXED"):
                counts["autofixed"] += 1

            if diag["invalid_fields"]:
                counts["invalid"] += 1
                # keep invalid rows too, but flagged — classification stage will decide
            cleaned_rows.append(cleaned)
            counts["kept"] += 1
        except Exception:
            counts["errors"] += 1
            # store an error-row with minimal info so pipeline doesn't break
            diagnostics_list.append({"error_row_index": idx, "trace": traceback.format_exc()})
            # continue, do not crash

    # Now call classify_rows in a guarded way
    try:
        summary, sections = classify_rows(cleaned_rows)
    except Exception as e:
        # classification failed; return diagnostics so you can fix classify_rows separately
        tb = traceback.format_exc()
        return {
            "status": "error",
            "error": "classify_rows_failed",
            "message": str(e),
            "traceback": tb,
            "diagnostics": {
                "counts": counts,
                "sample_diagnostics": diagnostics_list[:10],
                "cleaned_rows_sample": cleaned_rows[:5]
            }
        }

    # Build Level-51 summary overlay
    summary_overlay = {
        "level51": {
            "total_raw_rows": counts["total"],
            "kept_rows": counts["kept"],
            "skipped_np": counts["skipped_np"],
            "autofixed_rows": counts["autofixed"],
            "rows_with_invalid_fields": counts["invalid"],
            "processing_errors": counts["errors"]
        }
    }

    # Merge returned summary with overlay (overlay wins for these keys)
    final_summary = summary.copy() if isinstance(summary, dict) else {"summary": summary}
    final_summary.update(summary_overlay)

    # Debug printing
    if debug:
        print("DEBUG: run_level50 summary overlay =", summary_overlay)
        print("DEBUG: sample diagnostics (first 10) =")
        for i, d in enumerate(diagnostics_list[:10], 1):
            print(f"  {i}. {d}")
        print("DEBUG: cleaned_rows sample (first 5) =")
        for i, cr in enumerate(cleaned_rows[:5], 1):
            print(f"  {i}. {cr}")

    end_time = datetime.utcnow()
    elapsed = (end_time - start_time).total_seconds()

    return {
        "status": "success",
        "summary": final_summary,
        "sections": sections,
        "total_rows_raw": counts["total"],
        "total_rows_processed": counts["kept"],
        "level51_diagnostics": {
            "counts": counts
        },
        "time_seconds": elapsed
    }
