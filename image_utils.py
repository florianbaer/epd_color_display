"""
Image processing utilities for EPD display.
"""

import os
from datetime import datetime
from PIL import Image
import logging

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
