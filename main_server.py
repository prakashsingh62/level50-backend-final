import os
from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logic_engine 

app = FastAPI(title="Level 80 Automation API")

# CORS fix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AutomationRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: str = "Production"

@app.get("/")
async def root():
    return {"message": "Automation System is LIVE and Ready"}

@app.post("/automation/run")
async def trigger_run(request: AutomationRequest, background_tasks: BackgroundTasks, debug: bool = Query(False)):
    # 🚨 FORCE BYPASS: Code level par hi logic ko chill mode mein dalna
    print("🚀 BYPASS INITIATED: Ignoring length checks and strict analysis")
    
    # Logic engine ko background mein chalao
    # Note: logic_engine.run_level50 ke andar jo checks hain wo 
    # environment variables se bypass honge agar logic_engine sahi se coded hai.
    background_tasks.add_task(
        logic_engine.run_level50, 
        spreadsheet_id=request.spreadsheet_id, 
        sheet_name=request.sheet_name,
        debug=True # Debug humesha on rakho jab tak troubleshoot ho raha hai
    )
    return {
        "status": "Started", 
        "info": "Automation process started with BYPASS MODE"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
