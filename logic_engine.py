from sheet_reader import read_sheet
from classify import classify_rows


def run_level50(debug=False):
    rows = read_sheet()

    if debug:
        print("DEBUG: Rows fetched =", len(rows))

    summary, sections = classify_rows(rows)

    return {
        "status": "success",
        "summary": summary,
        "sections": sections,
        "total_rows": len(rows)
    }
