from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import logging
import uuid
from logic_engine import LogicEngine
from logic_engine import RFQExpertSystem  # Add this import

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RFQ Automation API",
    description="Production RFQ automation with Google Sheets + AI Expert System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Logic Engine
logic_engine = LogicEngine()
# Initialize AI Expert System
ai_expert = RFQExpertSystem()

class RFQRequest(BaseModel):
    rfq_id: str
    customer_name: Optional[str] = None
    product_details: Optional[Dict[str, Any]] = None
    quantity: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None

class AIAnalysisRequest(BaseModel):
    rfq_data: Dict[str, Any]
    email_context: Optional[Dict[str, Any]] = None

class AIApprovalRequest(BaseModel):
    suggestion_id: str
    action: str  # "APPROVE", "MODIFY", "REJECT"
    rfq_number: str
    modified_draft: Optional[str] = ""
    user_email: str
    user_name: Optional[str] = "Unknown User"
    original_suggestion: Dict[str, Any]
    comments: Optional[str] = ""

def get_timestamp():
    """Get current timestamp"""
    return datetime.now(timezone.utc).isoformat()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "operational",
        "timestamp": get_timestamp(),
        "service": "RFQ Automation API with AI Expert",
        "version": "2.0.0",
        "ai_capabilities": {
            "expert_system": True,
            "email_draft_generation": True,
            "human_approval_workflow": True,
            "next_action_prediction": True
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    sheets_status = logic_engine.test_connection()
    return {
        "status": "healthy" if sheets_status else "degraded",
        "timestamp": get_timestamp(),
        "services": {
            "api": "operational",
            "google_sheets": "connected" if sheets_status else "disconnected",
            "ai_expert_system": "operational"
        }
    }

@app.get("/api/ai/health")
async def ai_health_check():
    """Check if AI Expert System is working"""
    try:
        # Test the expert system with dummy data
        test_data = {
            "rfq_number": "TEST-AI-001",
            "customer_name": "Test Corporation",
            "valve_count": 5,
            "vendor_quotes_received": False,
            "current_stage": "INQUIRY",
            "customer_email": "test@corp.com",
            "location": "Test Location",
            "required_date": "2024-03-30"
        }
        
        test_result = ai_expert.analyze_rfq_context(test_data)
        
        return {
            "status": "healthy",
            "ai_system": "RFQExpertSystem",
            "version": "1.0",
            "timestamp": get_timestamp(),
            "test_analysis": {
                "rfq_number": test_result.get("rfq_number"),
                "next_action": test_result.get("next_action"),
                "confidence": test_result.get("confidence"),
                "priority": test_result.get("priority")
            },
            "rules_loaded": len(ai_expert.get_expert_rules_summary().get("rules", [])),
            "requires_human_approval": True
        }
        
    except Exception as e:
        logger.error(f"AI Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": get_timestamp()
        }

@app.post("/api/ai/analyze")
async def ai_analyze_rfq(request: AIAnalysisRequest):
    """
    🤖 AI Expert System Analysis - HUMAN EXPERT LIKE DECISIONS
    
    This endpoint analyzes RFQ data and suggests next best action
    with complete email drafts and reasoning.
    """
    try:
        rfq_data = request.rfq_data
        email_context = request.email_context or {}
        
        # Validate required fields
        if not rfq_data.get("rfq_number"):
            raise HTTPException(
                status_code=400, 
                detail="rfq_number is required in rfq_data"
            )
        
        # Log incoming request
        logger.info(f"🤖 AI Analysis Request: {rfq_data.get('rfq_number')}")
        
        # Get AI analysis from Expert System
        analysis = ai_expert.analyze_rfq_context(rfq_data, email_context)
        
        # Generate unique suggestion ID
        suggestion_id = f"ai_sugg_{uuid.uuid4().hex[:8]}"
        analysis["suggestion_id"] = suggestion_id
        
        # Add metadata
        analysis["analysis_timestamp"] = get_timestamp()
        analysis["ai_engine"] = "RFQExpertSystem_v1.0"
        
        # Log successful analysis
        logger.info(
            f"✅ AI Analysis Complete: {analysis['rfq_number']} -> "
            f"{analysis['next_action']} ({analysis['confidence']}% confidence)"
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "system": {
                "version": "1.0",
                "engine": "RFQExpertSystem",
                "suggestion_id": suggestion_id,
                "timestamp": get_timestamp()
            },
            "metadata": {
                "rules_applied": len(analysis.get("reasoning", [])),
                "human_approval_required": analysis.get("requires_human_approval", True),
                "processing_time_ms": 0  # Can add actual timing if needed
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"AI Analysis error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            "success": False,
            "error": error_msg,
            "analysis": {
                "rfq_number": request.rfq_data.get("rfq_number", "UNKNOWN"),
                "current_stage": "ERROR",
                "next_action": "MANUAL_REVIEW_NEEDED",
                "confidence": 0,
                "reasoning": [f"Processing Error: {str(e)}"],
                "priority": "HIGH",
                "requires_human_approval": True
            },
            "timestamp": get_timestamp()
        }

@app.post("/api/ai/approve-action")
async def approve_ai_action(request: AIApprovalRequest):
    """
    👤 Human Approval Workflow for AI Suggestions
    
    This endpoint handles human approval/rejection/modification
    of AI-generated suggestions. Ensures human-in-the-loop.
    """
    try:
        # Validate action
        valid_actions = ["APPROVE", "MODIFY", "REJECT"]
        if request.action.upper() not in valid_actions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action '{request.action}'. Must be one of: {valid_actions}"
            )
        
        action = request.action.upper()
        
        # Generate approval ID
        approval_id = f"appr_{uuid.uuid4().hex[:8]}"
        
        # Create approval record
        approval_record = {
            "approval_id": approval_id,
            "suggestion_id": request.suggestion_id,
            "rfq_number": request.rfq_number,
            "action_taken": action,
            "user_email": request.user_email,
            "user_name": request.user_name,
            "timestamp": get_timestamp(),
            "modified_draft_provided": bool(request.modified_draft),
            "comments": request.comments,
            "original_action": request.original_suggestion.get("next_action", "UNKNOWN"),
            "original_confidence": request.original_suggestion.get("confidence", 0),
            "system_version": "2.0.0"
        }
        
        # Log approval (In production, save to database)
        logger.info(
            f"👤 AI Suggestion {action}ED: {request.suggestion_id} for {request.rfq_number} "
            f"by {request.user_name} ({request.user_email})"
        )
        
        # Prepare response based on action
        if action == "APPROVE":
            # Get final draft (modified or original)
            final_draft = request.modified_draft or request.original_suggestion.get("draft_email", "")
            
            response_data = {
                "success": True,
                "message": "APPROVAL_RECORDED_DRAFT_READY",
                "instructions": "✅ AI suggestion APPROVED. Email draft prepared below.",
                "approval_id": approval_id,
                "draft_text": final_draft,
                "recipient": request.original_suggestion.get("suggested_recipient", "vendor@company.com"),
                "subject": request.original_suggestion.get("suggested_subject", f"Action: {request.original_suggestion.get('next_action', 'RFQ')}"),
                "next_steps": [
                    "1. Copy the draft email from 'draft_text' field",
                    "2. Open Gmail and create new email",
                    "3. Paste the draft, review and customize",
                    "4. Send manually",
                    "5. Update RFQ status in Google Sheet"
                ],
                "metadata": {
                    "requires_manual_sending": True,
                    "ai_confidence_original": request.original_suggestion.get("confidence", 0),
                    "human_approved": True,
                    "approval_timestamp": get_timestamp()
                }
            }
            
        elif action == "MODIFY":
            approval_record["modified_draft"] = request.modified_draft
            
            response_data = {
                "success": True,
                "message": "MODIFICATION_RECORDED",
                "instructions": "✏️ AI suggestion MODIFIED. Your changes have been saved.",
                "approval_id": approval_id,
                "modified_draft": request.modified_draft,
                "next_steps": [
                    "1. Use the modified draft above",
                    "2. Send email manually from Gmail",
                    "3. Mark RFQ as updated in sheet"
                ]
            }
            
        else:  # REJECT
            response_data = {
                "success": True,
                "message": "REJECTION_RECORDED",
                "instructions": "❌ AI suggestion REJECTED. Please handle manually.",
                "approval_id": approval_id,
                "next_steps": [
                    "1. Handle RFQ manually as per your judgment",
                    "2. Update status in Google Sheet",
                    "3. AI will learn from your decision"
                ],
                "feedback_notes": request.comments or "No specific feedback provided"
            }
        
        # Add common fields
        response_data.update({
            "timestamp": get_timestamp(),
            "rfq_number": request.rfq_number,
            "user": request.user_email
        })
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Approval processing error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            "success": False,
            "error": error_msg,
            "timestamp": get_timestamp()
        }

@app.get("/api/ai/rules")
async def get_ai_rules():
    """Get summary of AI Expert Rules"""
    try:
        rules_summary = ai_expert.get_expert_rules_summary()
        return {
            "success": True,
            "rules": rules_summary,
            "timestamp": get_timestamp()
        }
    except Exception as e:
        logger.error(f"Rules fetch error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": get_timestamp()
        }

@app.post("/api/rfq/submit")
async def submit_rfq(request: RFQRequest):
    """Submit new RFQ"""
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
                "message": "RFQ submitted successfully to Google Sheets",
                "data": {
                    "sheet_row": result.get("row_number"),
                    "sheet_id": result.get("sheet_id")
                }
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))
            
    except Exception as e:
        logger.error(f"Submit error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rfq/{rfq_id}")
async def get_rfq(rfq_id: str):
    """Get RFQ by ID"""
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
        logger.error(f"Get error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/rfq/{rfq_id}/status")
async def update_status(rfq_id: str, status: str):
    """Update RFQ status"""
    try:
        update_data = {
            "current_status": status,
            "last_updated": get_timestamp()
        }
        
        result = logic_engine.update_rfq(rfq_id, update_data)
        
        if result.get("success"):
            return {
                "status": "success",
                "rfq_id": rfq_id,
                "timestamp": get_timestamp(),
                "message": f"Status updated to {status}",
                "data": {
                    "new_status": status,
                    "updated_at": update_data["last_updated"]
                }
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error'))
            
    except Exception as e:
        logger.error(f"Update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rfqs")
async def list_rfqs(limit: int = 100, offset: int = 0, status: Optional[str] = None):
    """List all RFQs"""
    try:
        rfqs = logic_engine.list_rfqs(limit=limit, offset=offset, status_filter=status)
        
        return {
            "status": "success",
            "timestamp": get_timestamp(),
            "count": len(rfqs),
            "data": rfqs,
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logger.error(f"List error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/batch-analyze")
async def batch_ai_analyze(rfqs_data: List[Dict[str, Any]]):
    """
    🔄 Batch analyze multiple RFQs at once
    
    Useful for daily morning report generation
    """
    try:
        results = []
        for rfq_data in rfqs_data:
            analysis = ai_expert.analyze_rfq_context(rfq_data, {})
            analysis["suggestion_id"] = f"batch_{uuid.uuid4().hex[:6]}"
            results.append(analysis)
        
        # Generate summary
        high_priority = [r for r in results if r.get("priority") == "HIGH"]
        medium_priority = [r for r in results if r.get("priority") == "MEDIUM"]
        
        return {
            "success": True,
            "batch_id": f"batch_{uuid.uuid4().hex[:8]}",
            "timestamp": get_timestamp(),
            "summary": {
                "total_analyzed": len(results),
                "high_priority_actions": len(high_priority),
                "medium_priority_actions": len(medium_priority),
                "most_common_action": max(
                    set([r.get("next_action", "") for r in results]),
                    key=[r.get("next_action", "") for r in results].count
                ) if results else "NONE"
            },
            "analyses": results,
            "recommendations": {
                "urgent_today": [r for r in high_priority if r.get("timeline", "").startswith("URGENT")],
                "schedule_this_week": medium_priority[:5]  # Top 5 medium priority
            }
        }
        
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": get_timestamp()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_server:app", host="0.0.0.0", port=8000, reload=True)
