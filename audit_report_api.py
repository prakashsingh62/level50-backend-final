from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api")

@router.get("/audit/report")
def get_audit_report():
    try:
        # Lazy import (SAFE)
        from level_80_report_generator import get_audit_rows

        return {
            "rows": get_audit_rows()
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
