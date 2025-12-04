from fastapi import APIRouter
from sheet_reader import read_sheet
from logic_engine import prepare_rows_for_email
from email_builder import build_email_html

router = APIRouter()


@router.post("/email")
def email_preview():
    """
    Returns final formatted HTML email WITHOUT sending it.
    """
    rows = read_sheet()
    summary, sections = prepare_rows_for_email(rows)

    html = build_email_html(summary, sections)

    return {
        "status": "email_preview_generated",
        "html": html
    }
