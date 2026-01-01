import os
from fastapi import FastAPI, BackgroundTasks, Query
from pydantic import BaseModel
from datetime import datetime, timedelta

# Tere existing system ki imports (Inhe mat chhedna)
from main_logic import Phase11Processor, Phase17MasterController
from google_sheets_handler import SheetsHandler

app = FastAPI(title="Level 80 Automation System - Phase 17")

# --- Models ---
class ProcessRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: str
    row_index: int

# --- Helper Logic for Automation ---
def run_autonomous_loop(spreadsheet_id: str, sheet_name: str, is_test: bool):
    """
    Ye function background mein chalta hai.
    1. Sheet scan karta hai.
    2. Overdue RFQs dhoondhta hai.
    3. Phase 17 ka logic trigger karta hai.
    """
    handler = SheetsHandler(spreadsheet_id)
    all_rows = handler.get_all_rows(sheet_name)
    
    # Audit logging for start
    handler.log_to_audit(f"Automation Started. Mode: {'TEST' if is_test else 'LIVE'}")

    today = datetime.now()
    processed_count = 0

    for index, row in enumerate(all_rows, start=2):  # Row 2 se shuru
        try:
            # Maan lo date 'Column D' mein hai, use parse karo
            rfq_date_str = row.get('Date', '') 
            rfq_date = datetime.strptime(rfq_date_str, "%Y-%m-%d") # Format check kar lena
            
            # Logic: Agar 10 din se zyada ho gaye hain aur status 'Closed' nahi hai
            if (today - rfq_date).days >= 10 and row.get('Status') != 'Closed':
                
                if is_test:
                    handler.log_to_audit(f"Test: Row {index} identified as overdue (Days: {(today - rfq_date).days})")
                else:
                    # REAL ACTION: Phase 17 Controller ko call karna
                    controller = Phase17MasterController(spreadsheet_id, sheet_name)
                    controller.process_row(index)
                
                processed_count += 1
        except Exception as e:
            handler.log_to_audit(f"Error in Row {index}: {str(e)}")
            continue

    handler.log_to_audit(f"Automation Finished. Total Processed: {processed_count}")

# --- Endpoints ---

@app.get("/")
async def root():
    return {"message": "Level 80 Automation Backend is Online"}

# 1. Tera Purana Phase 11 Endpoint (Unchanged)
@app.post("/phase11/run")
async def run_phase11(request: ProcessRequest):
    processor = Phase11Processor(request.spreadsheet_id, request.sheet_name)
    result = processor.process_row(request.row_index)
    return {"status": "success", "result": result}

# 2. Naya Phase 17 Autonomous Endpoint (8:00 AM & Manual Test)
@app.post("/automation/run-phase17")
async def trigger_automation(
    background_tasks: BackgroundTasks, 
    spreadsheet_id: str,
    sheet_name: str = "Production",
    test_mode: bool = Query(False, description="True for testing, False for real action")
):
    """
    Ye endpoint roz subah 8 baje hit hoga.
    BackgroundTasks Render ka timeout (60s) bypass kar degi.
    """
    if test_mode:
        # Test mode ko sync rakha hai taaki Postman mein report dikhe
        run_autonomous_loop(spreadsheet_id, sheet_name, is_test=True)
        return {"status": "Test Mode Complete", "message": "Check Audit Sheet for the detailed preview report."}
    
    # Live mode background mein chalega
    background_tasks.add_task(run_autonomous_loop, spreadsheet_id, sheet_name, is_test=False)
    return {
        "status": "Success", 
        "message": "Phase 17 Automation triggered. AI is now scanning overdue RFQs in background."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
