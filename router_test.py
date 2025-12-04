from fastapi import APIRouter
from sheet_writer import write_test_row

router = APIRouter()

@router.post("/test/write")
def test_write_api():
    result = write_test_row()
    return {"status": "success", "written": result}
