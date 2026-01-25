"""API routes for prompt management."""

import csv
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException

from ...config import get_settings
from ...models.schemas import (
    PromptRequest,
    PromptResponse,
    PromptHistoryItem,
    PromptHistoryResponse,
    SuccessResponse
)
from ...utils.image import log_prompt_to_csv
from ..websocket import manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prompts", tags=["prompts"])


def read_prompt() -> str:
    """Read prompt from prompt.md file."""
    settings = get_settings()
    prompt_path = settings.prompt_path
    if prompt_path.exists():
        return prompt_path.read_text(encoding='utf-8').strip()
    return "Generate a beautiful landscape"


def write_prompt(prompt: str):
    """Write prompt to prompt.md file."""
    settings = get_settings()
    settings.prompt_path.write_text(prompt, encoding='utf-8')


@router.get("/current", response_model=PromptResponse)
async def get_current_prompt():
    """Get the current prompt."""
    prompt = read_prompt()
    return PromptResponse(prompt=prompt)


@router.put("/current", response_model=SuccessResponse)
async def update_current_prompt(request: PromptRequest):
    """Update the current prompt."""
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
        await manager.broadcast({'type': 'prompt_update', 'prompt': prompt})

        return SuccessResponse(success=True, message="Prompt saved successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=PromptHistoryResponse)
async def get_prompt_history(limit: int = 3):
    """Get the last N prompts from history."""
    settings = get_settings()
    prompts = []

    if settings.prompt_history_path.exists():
        with open(settings.prompt_history_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            for row in reversed(rows[-limit:]):
                prompts.append(PromptHistoryItem(
                    timestamp=row['timestamp'],
                    prompt=row['prompt']
                ))

    return PromptHistoryResponse(prompts=prompts)
