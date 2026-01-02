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

    # Step 1: Resize to target width while maintaining aspect ratio
    aspect_ratio = image.height / image.width
    new_height = int(target_width * aspect_ratio)
    resized = image.resize((target_width, new_height), Image.Resampling.LANCZOS)
    logger.info(f"Resized to width {target_width}: {resized.width}x{resized.height}")

    # Step 2: Crop to exact target dimensions (centered crop)
    if resized.height > target_height:
        # Crop height (center crop)
        top = (resized.height - target_height) // 2
        bottom = top + target_height
        cropped = resized.crop((0, top, target_width, bottom))
        logger.info(f"Cropped height from {resized.height} to {target_height} (removed {top} from top)")
    elif resized.height < target_height:
        # Pad height with background color
        canvas = Image.new('RGB', (target_width, target_height), background_color)
        y_offset = (target_height - resized.height) // 2
        canvas.paste(resized, (0, y_offset))
        cropped = canvas
        logger.info(f"Padded height from {resized.height} to {target_height}")
    else:
        cropped = resized

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
