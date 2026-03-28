"""API routes for system status and scheduler."""

import asyncio
import io
import os
import logging
import threading
from functools import partial
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
import PIL.Image as PILImage

from ...config import get_settings
from ...models.schemas import (
    GenerationStatus,
    SchedulerStatus,
    HealthResponse,
    ImageInfo,
    ImageGalleryResponse,
    FeedImageInfo,
    FeedGroup,
    FeedResponse,
    SuccessResponse,
    UploadResponse,
)
from ...core.scheduler import scheduler
from ...core.generator import display_existing_image
from ...utils.image import (
    get_images_from_directory,
    get_images_grouped_by_prompt,
    get_uploaded_images,
    prepare_image_for_display,
    save_image_with_timestamp,
    save_image_metadata,
)
from .generate import get_task_status, is_running, update_task_status

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
_CHUNK_SIZE = 64 * 1024

# Safe upper bound for PIL decompression (~8000x8000 RGBA)
PILImage.MAX_IMAGE_PIXELS = 89_478_485

# Magic bytes for supported image formats
_MAGIC_SIGNATURES: list[tuple[bytes, int, bytes | None, str]] = [
    # (prefix, offset_for_extra, extra_bytes, mime)
    (b"\x89PNG", 0, None, "image/png"),
    (b"\xff\xd8\xff", 0, None, "image/jpeg"),
    (b"RIFF", 0, b"WEBP", "image/webp"),  # extra check at offset 8
    (b"GIF87a", 0, None, "image/gif"),
    (b"GIF89a", 0, None, "image/gif"),
]


def _sniff_mime(data: bytes) -> str | None:
    for prefix, _, extra, mime in _MAGIC_SIGNATURES:
        if data[: len(prefix)] == prefix:
            if extra is not None and data[8: 8 + len(extra)] != extra:
                continue
            return mime
    return None


async def _read_limited(file: UploadFile, max_bytes: int) -> bytes:
    """Stream-read an upload file, rejecting if it exceeds max_bytes."""
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(_CHUNK_SIZE)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise HTTPException(status_code=413, detail="File too large (max 20 MB)")
        chunks.append(chunk)
    return b"".join(chunks)

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


@router.get("/gallery/feed", response_model=FeedResponse)
async def get_gallery_feed(limit: int = 100):
    """Get images grouped by prompt for feed display."""
    settings = get_settings()
    groups_data = get_images_grouped_by_prompt(settings.image_dir, limit=limit, exclude_uploads=True)

    groups = []
    total_images = 0
    for g in groups_data:
        images = [
            FeedImageInfo(
                filename=img["filename"],
                url=f"/api/v1/images/{img['filename']}",
                created_at=img["created_at"],
                size_bytes=img["size_bytes"],
            )
            for img in g["images"]
        ]
        total_images += len(images)
        groups.append(FeedGroup(
            prompt=g["prompt"],
            generated_at=g["generated_at"],
            images=images,
        ))

    return FeedResponse(groups=groups, total_images=total_images)


@router.get("/gallery/uploads", response_model=ImageGalleryResponse)
async def get_gallery_uploads(limit: int = 100):
    """Get uploaded images ordered by date."""
    settings = get_settings()
    images_data = get_uploaded_images(settings.image_dir, limit=limit)
    images = [
        ImageInfo(
            filename=img["filename"],
            path=img["path"],
            url=f"/api/v1/images/{img['filename']}",
            created_at=img["created_at"],
            size_bytes=img["size_bytes"],
        )
        for img in images_data
    ]
    return ImageGalleryResponse(images=images, total=len(images))


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    label: str = Form(default="Uploaded"),
):
    """Upload an image to the gallery."""
    # Stream-read with hard size cap (prevents memory DoS before any processing)
    data = await _read_limited(file, MAX_UPLOAD_BYTES)

    # Validate actual file content via magic bytes (content_type header is client-controlled)
    if _sniff_mime(data) not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported image type")

    loop = asyncio.get_event_loop()
    try:
        # Decode in thread pool — PIL is CPU-bound and would block the event loop
        image = await loop.run_in_executor(
            None,
            lambda: PILImage.open(io.BytesIO(data)).convert("RGB"),
        )
    except PILImage.DecompressionBombError:
        raise HTTPException(status_code=400, detail="Image dimensions are too large")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not decode image")

    settings = get_settings()
    prepared = await loop.run_in_executor(
        None,
        partial(prepare_image_for_display, image, settings.epd_width, settings.epd_height),
    )
    image_path = save_image_with_timestamp(prepared, settings.image_dir, prefix="upload")
    save_image_metadata(image_path, prompt=label.strip() or "Uploaded", model="upload")

    filename = Path(image_path).name
    return UploadResponse(
        success=True,
        filename=filename,
        url=f"/api/v1/images/{filename}",
        message="Image uploaded successfully",
    )


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


def run_display_image(image_path: str):
    """Background task for displaying an existing image."""
    update_task_status('running', 'Starting image display...')

    try:
        settings = get_settings()

        # Build configuration from settings
        config = {
            'width': settings.epd_width,
            'height': settings.epd_height,
        }

        # Status callback to update progress
        def status_callback(msg: str):
            update_task_status('running', msg)

        # Run display
        result = display_existing_image(image_path, config, status_callback)

        if result['success']:
            update_task_status('complete', result['message'],
                             image_path=result.get('image_path'))
        else:
            update_task_status('error', result['message'],
                             error=result.get('error'))

    except Exception as e:
        logger.error(f"Display thread error: {e}", exc_info=True)
        update_task_status('error', f'Unexpected error: {str(e)}', error=str(e))


@router.post("/display/{filename}", response_model=SuccessResponse)
async def display_image(filename: str):
    """Display an existing image on the e-paper display."""
    settings = get_settings()
    image_path = Path(settings.image_dir) / filename

    # Check if image exists
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    # Security: ensure the path is within the image directory
    try:
        image_path.resolve().relative_to(Path(settings.image_dir).resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check if generation/display is already in progress
    if is_running():
        raise HTTPException(status_code=409, detail="Operation already in progress")

    # Start background thread to display image
    thread = threading.Thread(target=run_display_image, args=(str(image_path),))
    thread.daemon = True
    thread.start()

    return SuccessResponse(success=True, message="Display started")
