from fastapi import APIRouter
from sheet_writer import write_test_row   # same folder import

router = APIRouter()

@router.post("/test/write")
async def test_write():
    """
    Simple Google Sheets test writer
    """
    write_test_row()
    return {"status": "test_row_written"}
