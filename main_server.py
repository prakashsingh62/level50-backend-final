import os
from fastapi import FastAPI, BackgroundTasks, Query
import logic_engine  # Ye ab error nahi dega

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Automation System Online"}

@app.post("/automation/run")
async def trigger_run(background_tasks: BackgroundTasks, debug: bool = Query(False)):
    # Render ka timeout bypass karne ke liye background task
    background_tasks.add_task(logic_engine.run_level50, debug=debug)
    return {"status": "Started", "info": "Running in background to avoid Render timeout"}

if __name__ == "__main__":
    import uvicorn
    # Render ke environment port 10000 ko apne aap utha lega
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
