"""API routes for system status and scheduler."""

import os
import logging
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse

from ...config import get_settings
from ...models.schemas import (
    GenerationStatus,
    SchedulerStatus,
    HealthResponse,
    ImageInfo,
    ImageGalleryResponse
)
from ...core.scheduler import scheduler
from ...utils.image import get_images_from_directory
from .generate import get_task_status

logger = logging.getLogger(__name__)
router = APIRouter(tags=["system"])


@router.get("/status", response_model=GenerationStatus)
async def get_status():
    """Get current generation status."""
    status = get_task_status()
    return GenerationStatus(**status)


@router.get("/scheduler", response_model=SchedulerStatus)
async def get_scheduler_status():
    """Get scheduler configuration and status."""
    status = scheduler.get_status()
    return SchedulerStatus(**status)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", version="1.0.0")


@router.get("/images", response_model=ImageGalleryResponse)
async def get_images(limit: int = 50):
    """Get list of generated images for gallery."""
    settings = get_settings()
    images_data = get_images_from_directory(settings.image_dir, limit=limit)

    images = []
    for img in images_data:
        images.append(ImageInfo(
            filename=img['filename'],
            path=img['path'],
            url=f"/api/v1/images/{img['filename']}",
            created_at=img['created_at'],
            size_bytes=img['size_bytes']
        ))

    return ImageGalleryResponse(images=images, total=len(images))


@router.get("/images/{filename}")
async def get_image(filename: str):
    """Serve a generated image file."""
    settings = get_settings()
    image_path = Path(settings.image_dir) / filename

    if not image_path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Image not found")

    # Security: ensure the path is within the image directory
    try:
        image_path.resolve().relative_to(Path(settings.image_dir).resolve())
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")

    return FileResponse(image_path, media_type="image/png")
