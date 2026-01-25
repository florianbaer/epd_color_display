"""
FastAPI application entry point for EPD Color Display backend.
"""

import os
import logging
import atexit
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .api.routes import prompts, generate, system
from .api.websocket import manager
from .core.scheduler import scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    settings = get_settings()

    # Ensure prompt.md exists
    if not settings.prompt_path.exists():
        settings.prompt_path.write_text(
            "Generate a beautiful spring landscape with blooming flowers, green meadows, and blue sky",
            encoding='utf-8'
        )
        logger.info("Created default prompt.md")

    # Ensure image directory exists
    Path(settings.image_dir).mkdir(parents=True, exist_ok=True)

    # Configure and start scheduler
    def scheduled_generation():
        """Run scheduled generation if not already running."""
        from .api.routes.generate import is_running, start_generation_thread
        if not is_running():
            start_generation_thread()
        else:
            logger.warning("Generation already in progress, skipping scheduled run")

    scheduler.configure(
        enabled=settings.auto_generate,
        schedule_time=settings.schedule_time,
        timezone=settings.tz,
        generation_callback=scheduled_generation
    )
    scheduler.start()

    logger.info("Application started")

    yield

    # Shutdown
    scheduler.shutdown()
    logger.info("Application shutdown")


# Create FastAPI application
app = FastAPI(
    title="E-Paper Display Image Generator API",
    description="API for managing prompts and generating images for e-paper displays",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
        "http://localhost",       # Production nginx
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers with /api/v1 prefix
api_prefix = "/api/v1"
app.include_router(prompts.router, prefix=api_prefix)
app.include_router(generate.router, prefix=api_prefix)
app.include_router(system.router, prefix=api_prefix)


@app.websocket(f"{api_prefix}/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, handle incoming messages if needed
            data = await websocket.receive_text()
            # Echo back for ping/pong if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == '__main__':
    import uvicorn

    settings = get_settings()
    logger.info(f"Starting FastAPI server on {settings.host}:{settings.port}")

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )
