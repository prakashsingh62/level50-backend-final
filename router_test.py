from fastapi import APIRouter
from sheet_writer import write_test_row

router = APIRouter()


@router.post("/test/write")
def test_write_api():
    """
    Writes a test row into sheet to verify write access.
    """
    write_test_row()
    return {"status": "test_row_written"}
