import os
from fastapi import FastAPI, BackgroundTasks, Query
from pydantic import BaseModel

# Tere GitHub ke actual code ke hisaab se imports
import logic_engine 

app = FastAPI(title="Level 50/80 Automation System")

class ProcessRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: str
    row_index: int

@app.get("/")
async def root():
    return {"message": "System Online - Connected to Logic Engine"}

# --- Level 50/80 Automation Endpoint ---
@app.post("/automation/run-logic")
async def trigger_logic(
    background_tasks: BackgroundTasks, 
    debug_mode: bool = Query(False)
):
    """
    Ye endpoint tere logic_engine.py ke run_level50() function ko call karega.
    """
    # Background mein chalao taaki Render timeout na de
    background_tasks.add_task(logic_engine.run_level50, debug=debug_mode)
    
    return {
        "status": "Started", 
        "message": f"logic_engine.run_level50 started in background (Debug: {debug_mode})"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
