"""Image processing utilities for EPD display."""

import os
import csv
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from PIL import Image
import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


def prepare_image_for_display(
    image: Image.Image,
    target_width: int = 800,
    target_height: int = 480,
    background_color: tuple = (255, 255, 255)
) -> Image.Image:
    """
    Resize image to target width and crop to exact dimensions.

    Args:
        image: Input PIL Image
        target_width: Target display width (default: 800)
        target_height: Target display height (default: 480)
        background_color: RGB background color (not used in crop mode)

    Returns:
        PIL Image resized to target width and cropped to exact dimensions
    """
    # If image is already the correct size, return as-is
    if image.size == (target_width, target_height):
        logger.info("Image already correct size, no processing needed")
        return image

    logger.info(f"Preparing image: {image.size[0]}x{image.size[1]} -> {target_width}x{target_height}")

    # Calculate scaling to ensure both dimensions are at least target size
    scale_width = target_width / image.width
    scale_height = target_height / image.height
    # Use the larger scale to ensure we cover the entire target area
    scale = max(scale_width, scale_height)

    # Step 1: Resize to ensure both dimensions are at least target size
    new_width = int(image.width * scale)
    new_height = int(image.height * scale)
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    logger.info(f"Resized to: {resized.width}x{resized.height}")

    # Step 2: Center crop to exact target dimensions
    left = (resized.width - target_width) // 2
    top = (resized.height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    cropped = resized.crop((left, top, right, bottom))
    logger.info(f"Cropped to: {cropped.width}x{cropped.height}")

    return cropped


def save_image_with_timestamp(
    image: Image.Image,
    directory: str = "generated_images",
    prefix: str = "landscape"
) -> str:
    """
    Save image with timestamp filename.

    Args:
        image: PIL Image to save
        directory: Directory to save to (default: "generated_images")
        prefix: Filename prefix (default: "landscape")

    Returns:
        Absolute path to saved file
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Generate timestamp filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.png"
    filepath = os.path.join(directory, filename)

    # Save as PNG
    image.save(filepath, "PNG")
    abs_path = os.path.abspath(filepath)

    logger.info(f"Saved image to: {abs_path}")
    return abs_path


def get_last_prompt_from_csv(csv_path: str) -> str | None:
    """
    Get the last prompt from a CSV history file.

    Args:
        csv_path: Path to the CSV file

    Returns:
        The last prompt string, or None if file doesn't exist or is empty
    """
    if not os.path.exists(csv_path):
        return None

    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        if len(rows) > 1 and len(rows[-1]) > 1:  # Has header + at least one entry
            return rows[-1][1]
    return None


def log_prompt_to_csv(
    prompt: str,
    csv_path: str = None
) -> str:
    """
    Append prompt with timestamp to CSV history file.

    Skips writing if the prompt is identical to the previous entry.

    Args:
        prompt: The prompt text to log
        csv_path: Path to CSV file (default: prompt_history.csv in project root)

    Returns:
        Path to the CSV file
    """
    if csv_path is None:
        csv_path = str(get_settings().prompt_history_path)

    file_exists = os.path.exists(csv_path)

    if get_last_prompt_from_csv(csv_path) == prompt:
        logger.debug(f"Skipping duplicate prompt in CSV")
        return csv_path

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'prompt'])
        writer.writerow([timestamp, prompt])

    logger.info(f"Logged prompt to: {csv_path}")
    return csv_path


def save_image_metadata(image_path: str, prompt: str, model: str = "") -> str:
    """
    Write a JSON sidecar file alongside an image with generation metadata.

    Returns:
        Path to the written JSON file.
    """
    json_path = os.path.splitext(image_path)[0] + ".json"
    metadata = {
        "prompt": prompt,
        "generated_at": datetime.now().isoformat(),
        "model": model,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved image metadata to: {json_path}")
    return json_path


def read_image_metadata(image_path: str) -> dict | None:
    """Read the JSON sidecar for an image, returning None if it doesn't exist."""
    json_path = os.path.splitext(image_path)[0] + ".json"
    if not os.path.exists(json_path):
        return None
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        logger.warning(f"Failed to read metadata: {json_path}")
        return None


def get_images_grouped_by_prompt(directory: str, limit: int = 100, exclude_uploads: bool = True) -> list[dict]:
    """
    Scan PNGs, read sidecars, group by prompt text.

    Returns list of groups sorted newest-first:
        [{"prompt": str, "generated_at": str, "images": [dict, ...]}]
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []

    png_files = list(dir_path.glob("*.png"))
    png_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    png_files = png_files[:limit]

    groups: dict[str, list[dict]] = defaultdict(list)
    group_timestamps: dict[str, str] = {}

    for img_path in png_files:
        stat = img_path.stat()
        meta = read_image_metadata(str(img_path))

        if exclude_uploads and meta and meta.get("model") == "upload":
            continue

        prompt = meta["prompt"] if meta and meta.get("prompt") else ""
        generated_at = meta.get("generated_at", "") if meta else ""

        img_info = {
            "filename": img_path.name,
            "path": str(img_path.absolute()),
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size_bytes": stat.st_size,
        }
        groups[prompt].append(img_info)

        # Track newest timestamp per group
        ts = generated_at or img_info["created_at"]
        if prompt not in group_timestamps or ts > group_timestamps[prompt]:
            group_timestamps[prompt] = ts

    # Build result sorted newest-first
    result = []
    for prompt, images in groups.items():
        result.append({
            "prompt": prompt,
            "generated_at": group_timestamps[prompt],
            "images": images,
        })
    result.sort(key=lambda g: g["generated_at"], reverse=True)
    return result


def get_uploaded_images(directory: str, limit: int = 100) -> list[dict]:
    """
    Return images whose JSON sidecar has model == "upload", sorted newest-first.
    Filters before sorting so stat() is only called once per matched file.
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        return []

    # Filter first (cheap metadata read), cache stat to avoid double syscall
    candidates: list[tuple[os.stat_result, Path]] = []
    for img_path in dir_path.glob("*.png"):
        meta = read_image_metadata(str(img_path))
        if not meta or meta.get("model") != "upload":
            continue
        candidates.append((img_path.stat(), img_path))

    candidates.sort(key=lambda x: x[0].st_mtime, reverse=True)

    return [
        {
            "filename": img_path.name,
            "path": str(img_path.absolute()),
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size_bytes": stat.st_size,
        }
        for stat, img_path in candidates[:limit]
    ]


def get_images_from_directory(directory: str, limit: int = 50) -> list[dict]:
    """
    Get list of images from a directory with metadata.

    Args:
        directory: Directory to scan for images
        limit: Maximum number of images to return

    Returns:
        List of dicts with filename, path, created_at, size_bytes
    """
    images = []
    dir_path = Path(directory)

    if not dir_path.exists():
        return images

    # Get all PNG files
    png_files = list(dir_path.glob("*.png"))

    # Sort by modification time (newest first)
    png_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    for img_path in png_files[:limit]:
        stat = img_path.stat()
        images.append({
            'filename': img_path.name,
            'path': str(img_path.absolute()),
            'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'size_bytes': stat.st_size
        })

    return images
