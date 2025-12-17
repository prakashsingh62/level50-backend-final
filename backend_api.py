from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api")

@router.post("/run")
def run_pipeline_api():
    try:
        # 🔴 IMPORTANT: import INSIDE function
        from pipeline_engine import run_pipeline

        result = run_pipeline()
        return {
            "status": "OK",
            "result": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
