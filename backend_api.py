from fastapi import APIRouter
from sheet_reader import read_rows

router = APIRouter()

@router.get("/data")
def get_data():
    return {"rows": read_rows()}
