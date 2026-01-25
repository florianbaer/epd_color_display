"""
FastAPI web application for managing prompts and generating EPD images.
"""

import os
import logging
import threading
import atexit
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import csv
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from core import generate_and_display_image
from image_utils import log_prompt_to_csv

app = FastAPI(title="E-Paper Display Image Generator")
load_dotenv()

# Global state for task tracking
current_task = {
    'status': 'idle',  # idle, running, complete, error
    'message': 'Ready',
    'image_path': None,
    'error': None
}
task_lock = threading.Lock()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

PROMPT_FILE = Path(__file__).parent / 'prompt.md'
PROMPT_HISTORY_FILE = Path(__file__).parent / 'prompt_history.csv'


# Pydantic models
class PromptRequest(BaseModel):
    prompt: str


def read_prompt() -> str:
    """Read prompt from prompt.md file."""
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding='utf-8').strip()
    return "Generate a beautiful landscape"


def write_prompt(prompt: str):
    """Write prompt to prompt.md file."""
    PROMPT_FILE.write_text(prompt, encoding='utf-8')


def update_task_status(status: str, message: str, **kwargs):
    """Thread-safe task status update."""
    with task_lock:
        current_task['status'] = status
        current_task['message'] = message
        current_task.update(kwargs)


def run_generation():
    """Background task for image generation."""
    update_task_status('running', 'Starting generation...')

    try:
        prompt = read_prompt()

        # Build configuration from environment
        config = {
            'api_key': os.getenv('GEMINI_API_KEY'),
            'model': os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-image'),
            'width': int(os.getenv('EPD_WIDTH', '800')),
            'height': int(os.getenv('EPD_HEIGHT', '480')),
            'image_dir': os.getenv('IMAGE_DIR', 'generated_images')
        }

        # Status callback to update progress
        def status_callback(msg: str):
            update_task_status('running', msg)

        # Run generation
        result = generate_and_display_image(prompt, config, status_callback)

        if result['success']:
            update_task_status('complete', result['message'],
                             image_path=result.get('image_path'))
        else:
            update_task_status('error', result['message'],
                             error=result.get('error'))

    except Exception as e:
        logger.error(f"Generation thread error: {e}", exc_info=True)
        update_task_status('error', f'Unexpected error: {str(e)}', error=str(e))


def scheduled_generation():
    """Run scheduled image generation at configured time."""
    logger.info("Starting scheduled image generation...")

    # Check if already running
    with task_lock:
        if current_task['status'] == 'running':
            logger.warning("Generation already in progress, skipping scheduled run")
            return

    # Start generation in background thread
    thread = threading.Thread(target=run_generation)
    thread.daemon = True
    thread.start()


# Initialize scheduler
scheduler = BackgroundScheduler()

# Configure schedule from environment
auto_generate = os.getenv('AUTO_GENERATE', 'true').lower() == 'true'
schedule_time = os.getenv('SCHEDULE_TIME', '19:00')

if auto_generate:
    try:
        hour, minute = schedule_time.split(':')
        scheduler.add_job(
            func=scheduled_generation,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            id='daily_generation',
            name='Daily image generation',
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"Scheduled daily generation at {schedule_time}")

        # Shut down scheduler on exit
        atexit.register(lambda: scheduler.shutdown())
    except Exception as e:
        logger.error(f"Failed to configure scheduler: {e}")
else:
    logger.info("Automatic generation disabled (AUTO_GENERATE=false)")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Main page."""
    prompt = read_prompt()
    with task_lock:
        status = current_task.copy()

    # Read and render HTML template
    template_path = Path(__file__).parent / 'templates' / 'index.html'
    html_content = template_path.read_text(encoding='utf-8')

    # Simple template rendering (replace placeholders)
    html_content = html_content.replace('{{ prompt }}', prompt)
    html_content = html_content.replace('{{ status.status }}', status['status'])
    html_content = html_content.replace('{{ status.message }}', status['message'])

    return html_content


@app.post("/save-prompt")
async def save_prompt(request: PromptRequest):
    """Save prompt to prompt.md."""
    try:
        prompt = request.prompt.strip()

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        if len(prompt) > 1000:
            raise HTTPException(status_code=400, detail="Prompt too long (max 1000 characters)")

        write_prompt(prompt)
        log_prompt_to_csv(prompt)
        logger.info(f"Prompt saved: {prompt[:50]}...")

        # Broadcast to all connected WebSocket clients
        await manager.broadcast({'type': 'prompt_updated', 'prompt': prompt})

        return {"success": True, "message": "Prompt saved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prompt-history")
async def get_prompt_history(limit: int = 3):
    """Get the last N prompts from history."""
    prompts = []
    if PROMPT_HISTORY_FILE.exists():
        with open(PROMPT_HISTORY_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            for row in reversed(rows[-limit:]):
                prompts.append({'timestamp': row['timestamp'], 'prompt': row['prompt']})
    return {"prompts": prompts}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/generate")
async def generate():
    """Start image generation."""
    with task_lock:
        if current_task['status'] == 'running':
            raise HTTPException(status_code=409, detail="Generation already in progress")

    # Start background thread
    thread = threading.Thread(target=run_generation)
    thread.daemon = True
    thread.start()

    return {"status": "started", "message": "Generation started"}


@app.get("/status")
async def status():
    """Get current generation status."""
    with task_lock:
        return current_task.copy()


@app.get("/scheduler-status")
async def scheduler_status():
    """Get scheduler configuration and status."""
    jobs = scheduler.get_jobs()
    next_run = jobs[0].next_run_time.isoformat() if jobs else None

    return {
        "enabled": auto_generate,
        "schedule_time": schedule_time,
        "next_run": next_run,
        "timezone": os.getenv('TZ', 'System default')
    }


if __name__ == '__main__':
    import uvicorn

    # Ensure prompt.md exists
    if not PROMPT_FILE.exists():
        write_prompt("Generate a beautiful spring landscape with blooming flowers, green meadows, and blue sky")
        logger.info("Created default prompt.md")

    # Run FastAPI app with uvicorn
    logger.info("Starting FastAPI web server...")
    logger.info("Access the app at http://localhost")
    uvicorn.run(
        app,
        host="0.0.0.0",  # Allow network access
        port=8080,
        log_level="info"
    )
