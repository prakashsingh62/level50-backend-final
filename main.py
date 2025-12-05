import os
import uvicorn

# Railway Cron sets this automatically when running a scheduled job
IS_CRON = os.environ.get("RAILWAY_RUN_CRON") == "1"


# --------------------------------------------------
# 🚀 CRON MODE — RUN DAILY REMINDER ONLY
# --------------------------------------------------
if IS_CRON:
    from daily_sender import run_daily_email

    if __name__ == "__main__":
        print("Running Level-50 Daily Reminder via Cron...")
        run_daily_email()
        print("Daily Reminder Completed.")
    # DO NOT LOAD FASTAPI IN CRON MODE
    # DO NOT LOAD ROUTERS
    # EXIT AFTER EMAIL
else:
    # --------------------------------------------------
    # 🌐 NORMAL SERVER MODE — FASTAPI + ROUTERS
    # --------------------------------------------------
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from run_router import router as run_router
    from router_test import router as test_router
    from router_email import router as email_router

    app = FastAPI(title="Level-50 Automation Engine")

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- ROUTERS ----
    app.include_router(run_router)
    app.include_router(test_router)
    app.include_router(email_router)

    @app.get("/")
    async def root():
        return {"status": "Level-50 backend active"}

    # ---- API SERVER ----
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
