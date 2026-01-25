"""API routes for image generation."""

import os
import threading
import logging
from fastapi import APIRouter, HTTPException

from ...config import get_settings
from ...models.schemas import GenerationStartResponse
from ...core.generator import generate_and_display_image
from .prompts import read_prompt

logger = logging.getLogger(__name__)
router = APIRouter(tags=["generate"])

# Global state for task tracking
current_task = {
    'status': 'idle',  # idle, running, complete, error
    'message': 'Ready',
    'image_path': None,
    'error': None
}
task_lock = threading.Lock()


def update_task_status(status: str, message: str, **kwargs):
    """Thread-safe task status update."""
    with task_lock:
        current_task['status'] = status
        current_task['message'] = message
        current_task.update(kwargs)


def get_task_status() -> dict:
    """Get current task status (thread-safe)."""
    with task_lock:
        return current_task.copy()


def is_running() -> bool:
    """Check if generation is currently running."""
    with task_lock:
        return current_task['status'] == 'running'


def run_generation():
    """Background task for image generation."""
    update_task_status('running', 'Starting generation...')

    try:
        settings = get_settings()
        prompt = read_prompt()

        # Build configuration from settings
        config = {
            'api_key': settings.gemini_api_key,
            'model': settings.gemini_model,
            'width': settings.epd_width,
            'height': settings.epd_height,
            'image_dir': settings.image_dir
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


def start_generation_thread():
    """Start background generation thread."""
    thread = threading.Thread(target=run_generation)
    thread.daemon = True
    thread.start()


@router.post("/generate", response_model=GenerationStartResponse)
async def generate():
    """Start image generation."""
    if is_running():
        raise HTTPException(status_code=409, detail="Generation already in progress")

    # Start background thread
    start_generation_thread()

    return GenerationStartResponse(status="started", message="Generation started")
