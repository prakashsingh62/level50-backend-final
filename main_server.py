from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging
from logic_engine import LogicEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RFQ Automation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logic_engine = LogicEngine()

class RFQRequest(BaseModel):
    rfq_id: str
    customer_name: Optional[str] = None
    product_details: Optional[Dict[str, Any]] = None
    quantity: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None

def get_timestamp():
    return datetime.now(timezone.utc).isoformat()

@app.get("/")
async def root():
    return {
        "status": "operational",
        "timestamp": get_timestamp(),
        "service": "RFQ Automation API"
    }

@app.get("/health")
async def health():
    sheets_status = logic_engine.test_connection()
    return {
        "status": "healthy" if sheets_status else "degraded",
        "timestamp": get_timestamp(),
        "services": {
            "api": "operational",
            "google_sheets": "connected" if sheets_status else "disconnected"
        }
    }

@app.post("/api/rfq/submit")
async def submit_rfq(request: RFQRequest):
    try:
        rfq_data = {
            "rfq_id": request.rfq_id,
            "customer_name": request.customer_name,
            "product_details": request.product_details,
            "quantity": request.quantity,
            "submission_timestamp": get_timestamp(),
            "status": "submitted",
            **(request.additional_data or {})
        }
        
        result = logic_engine.write_rfq(rfq_data)
        
        if result.get("success"):
            return {
                "status": "success",
                "rfq_id": request.rfq_id,
                "timestamp": get_timestamp(),
                "message": "RFQ submitted successfully",
                "data": {
                    "sheet_row": result.get("row_number"),
                    "sheet_id": result.get("sheet_id")
                }
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rfq/{rfq_id}")
async def get_rfq(rfq_id: str):
    try:
        rfq_data = logic_engine.read_rfq(rfq_id)
        if rfq_data:
            return {
                "status": "success",
                "rfq_id": rfq_id,
                "timestamp": get_timestamp(),
                "data": rfq_data
            }
        else:
            raise HTTPException(status_code=404, detail=f"RFQ {rfq_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/rfq/{rfq_id}/status")
async def update_status(rfq_id: str, status: str):
    try:
        result = logic_engine.update_rfq(rfq_id, {"status": status, "last_updated": get_timestamp()})
        if result.get("success"):
            return {
                "status": "success",
                "rfq_id": rfq_id,
                "timestamp": get_timestamp(),
                "message": f"Status updated to {status}"
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rfqs")
async def list_rfqs(limit: int = 100, offset: int = 0, status: Optional[str] = None):
    try:
        rfqs = logic_engine.list_rfqs(limit=limit, offset=offset, status_filter=status)
        return {
            "status": "success",
            "timestamp": get_timestamp(),
            "count": len(rfqs),
            "data": rfqs
        }
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000, reload=True)
