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
    Resize and center image for EPD display.

    Args:
        image: Input PIL Image
        target_width: Target display width (default: 800)
        target_height: Target display height (default: 480)
        background_color: RGB background color (default: white)

    Returns:
        PIL Image resized and centered on target canvas
    """
    # If image is already the correct size, return as-is
    if image.size == (target_width, target_height):
        logger.info("Image already correct size, no processing needed")
        return image

    logger.info(f"Preparing image: {image.size[0]}x{image.size[1]} -> {target_width}x{target_height}")

    # Calculate aspect ratios
    img_ratio = image.width / image.height
    display_ratio = target_width / target_height

    # Determine new size while preserving aspect ratio
    if img_ratio > display_ratio:
        # Image is wider - fit to width
        new_width = target_width
        new_height = int(target_width / img_ratio)
    else:
        # Image is taller - fit to height
        new_height = target_height
        new_width = int(target_height * img_ratio)

    # Resize image with high-quality resampling
    resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    logger.info(f"Resized to: {new_width}x{new_height}")

    # Create canvas and center image
    canvas = Image.new('RGB', (target_width, target_height), background_color)
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    canvas.paste(resized, (x_offset, y_offset))

    logger.info(f"Centered on canvas with offset: ({x_offset}, {y_offset})")
    return canvas


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
