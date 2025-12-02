# main_server.py
# Level-50 FastAPI backend entrypoint
# Clean, Railway-safe, uses backend_api.py

from fastapi import FastAPI
from logger import get_logger
from backend_api import router as backend_router

log = get_logger()

def create_app():
    app = FastAPI(
        title="Level-50 Automation Backend",
        version="1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Mount all Level-50 API endpoints
    app.include_router(backend_router, prefix="")

    log.info("FastAPI Level-50 backend initialized")
    return app

app = create_app()

# No __main__ block needed because Railway uses:
# uvicorn main_server:app --host 0.0.0.0 --port $PORT
