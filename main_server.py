import os
from fastapi import FastAPI, BackgroundTasks, Query
from pydantic import BaseModel
import logic_engine 

app = FastAPI()

class AutomationRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: str = "Production"

@app.get("/")
async def root():
    return {"message": "Level 80 System Online"}

@app.post("/automation/run")
async def trigger_run(request: AutomationRequest, background_tasks: BackgroundTasks, debug: bool = Query(False)):
    background_tasks.add_task(
        logic_engine.run_level50, 
        spreadsheet_id=request.spreadsheet_id, 
        sheet_name=request.sheet_name,
        debug=debug
    )
    return {"status": "Started", "info": "Scanning in background"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
