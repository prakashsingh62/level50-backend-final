import uvicorn
import os

# Detect if CRON mode
IS_CRON = os.environ.get("RAILWAY_RUN_CRON") == "1"

if IS_CRON:
    # DAILY REMINDER MODE
    from daily_sender import run_daily_email

    if __name__ == "__main__":
        run_daily_email()
else:
    # NORMAL API MODE
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from run_router import router as run_router
    from router_test import router as test_router
    from router_email import router as email_router

    app = FastAPI(title="Level-50 Automation Engine")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ROUTERS
    app.include_router(run_router)
    app.include_router(test_router)
    app.include_router(email_router)

    @app.get("/")
    async def root():
        return {"status": "Level-50 backend active"}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
