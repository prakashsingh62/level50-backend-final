import os
from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logic_engine
from typing import List, Optional
import json

app = FastAPI(title="Level 80 Automation API")

# CORS fix - Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class AutomationRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: str = "Production"

# ======================== RFQ ENDPOINTS ========================

@app.get("/rfqs/filter1")
async def get_rfqs_filter1():
    """
    Frontend RFQ Dashboard ke liye data return karega
    """
    try:
        # ✅ Dummy data for testing - Database se replace karna hoga
        rfqs = [
            {
                "sr_no": 1,
                "customer_name": "ABC Corporation",
                "location": "Mumbai",
                "rfq_no": "RFQ-2024-001",
                "rfq_date": "2024-01-15",
                "uid_no": "UID-001",
                "product": "Industrial Valves"
            },
            {
                "sr_no": 2,
                "customer_name": "XYZ Industries",
                "location": "Delhi",
                "rfq_no": "RFQ-2024-002",
                "rfq_date": "2024-01-16",
                "uid_no": "UID-002",
                "product": "Pressure Pumps"
            },
            {
                "sr_no": 3,
                "customer_name": "PQR Engineering",
                "location": "Chennai",
                "rfq_no": "RFQ-2024-003",
                "rfq_date": "2024-01-17",
                "uid_no": "UID-003",
                "product": "Control Systems"
            },
            {
                "sr_no": 4,
                "customer_name": "LMN Manufacturing",
                "location": "Bangalore",
                "rfq_no": "RFQ-2024-004",
                "rfq_date": "2024-01-18",
                "uid_no": "UID-004",
                "product": "Safety Valves"
            },
            {
                "sr_no": 5,
                "customer_name": "DEF Heavy Industries",
                "location": "Pune",
                "rfq_no": "RFQ-2024-005",
                "rfq_date": "2024-01-19",
                "uid_no": "UID-005",
                "product": "Steam Boilers"
            }
        ]
        
        return {
            "status": "success",
            "data": rfqs,
            "count": len(rfqs),
            "message": f"Found {len(rfqs)} RFQs",
            "pagination": {
                "page": 1,
                "totalPages": 1,
                "totalItems": len(rfqs),
                "hasNext": False,
                "hasPrev": False
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching RFQs: {str(e)}",
            "data": [],
            "count": 0
        }

@app.get("/rfqs/{rfq_id}")
async def get_rfq_by_id(rfq_id: str):
    """
    Specific RFQ ka detail laane ke liye
    """
    try:
        # Dummy response - Database se replace karna hoga
        rfq_detail = {
            "rfq_id": rfq_id,
            "customer_name": "ABC Corporation",
            "location": "Mumbai",
            "rfq_no": f"RFQ-2024-{rfq_id.zfill(3)}",
            "rfq_date": "2024-01-15",
            "uid_no": f"UID-{rfq_id.zfill(3)}",
            "product": "Industrial Valves",
            "quantity": 100,
            "unit_price": 1500.50,
            "total_value": 150050.00,
            "status": "Pending",
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:30:00"
        }
        
        return {
            "status": "success",
            "data": rfq_detail
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching RFQ {rfq_id}: {str(e)}",
            "data": None
        }

# ======================== EXISTING ENDPOINTS ========================

@app.get("/")
async def root():
    return {
        "message": "Automation System is LIVE and Ready",
        "endpoints": {
            "rfq_dashboard": "/rfqs/filter1",
            "rfq_detail": "/rfqs/{rfq_id}",
            "automation": "/automation/run"
        },
        "status": "operational"
    }

@app.post("/automation/run")
async def trigger_run(request: AutomationRequest, background_tasks: BackgroundTasks, debug: bool = Query(False)):
    """
    Automation process start karne ke liye
    """
    print("🚀 BYPASS INITIATED: Ignoring length checks and strict analysis")
    
    # Logic engine ko background mein chalao
    background_tasks.add_task(
        logic_engine.run_level50, 
        spreadsheet_id=request.spreadsheet_id, 
        sheet_name=request.sheet_name,
        debug=True  # Debug humesha on rakho jab tak troubleshoot ho raha hai
    )
    
    return {
        "status": "Started", 
        "info": "Automation process started with BYPASS MODE",
        "spreadsheet_id": request.spreadsheet_id,
        "sheet_name": request.sheet_name,
        "timestamp": "2024-01-20T10:30:00"  # Add actual timestamp
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "Level 80 Automation API",
        "timestamp": "2024-01-20T10:30:00",  # Add actual timestamp logic
        "version": "1.0.0"
    }

# ======================== DATABASE CONNECTION HELPER ========================

def get_db_connection():
    """
    Database connection helper function
    Uncomment and configure when database is ready
    """
    # import psycopg2
    # DATABASE_URL = os.environ.get("DATABASE_URL")
    # if not DATABASE_URL:
    #     raise ValueError("DATABASE_URL environment variable not set")
    # return psycopg2.connect(DATABASE_URL)
    pass

# ======================== SERVER STARTUP ========================

if __name__ == "__main__":
    import uvicorn
    
    # Port configuration
    port = int(os.environ.get("PORT", 10000))
    
    print(f"🚀 Starting Level 80 Automation API on port {port}...")
    print(f"📡 API URL: http://0.0.0.0:{port}")
    print(f"🌐 CORS Enabled: All origins allowed")
    print(f"📊 Endpoints available:")
    print(f"   - GET  /                - Health check")
    print(f"   - GET  /rfqs/filter1    - RFQ Dashboard data")
    print(f"   - GET  /rfqs/{{id}}      - Single RFQ detail")
    print(f"   - POST /automation/run  - Start automation")
    print(f"   - GET  /health          - System health")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        reload=False  # Set to True for development
    )
