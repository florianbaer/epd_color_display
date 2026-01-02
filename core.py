"""
Core image generation and display logic.
Shared by both CLI (main.py) and web app (app.py).
"""

import logging
from typing import Dict, Any, Callable, Optional
from epd_color import EPD
from gemini_client import GeminiImageGenerator
from image_utils import save_image_with_timestamp, prepare_image_for_display

logger = logging.getLogger(__name__)


def generate_and_display_image(
    prompt: str,
    config: Dict[str, Any],
    status_callback: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
    """
    Generate image from prompt and display on EPD.

    Args:
        prompt: Text prompt for image generation
        config: Configuration dict with:
            - api_key: Gemini API key
            - model: Gemini model name (default: gemini-2.5-flash-image)
            - width: Target width (default: 800)
            - height: Target height (default: 480)
            - image_dir: Directory for saved images (default: generated_images)
        status_callback: Optional function(message) for progress updates

    Returns:
        Dict with:
            - success: bool
            - message: str
            - image_path: str (if successful)
            - error: str (if failed)
    """
    epd = None

    def update_status(msg: str):
        """Helper to update status via callback and logger."""
        logger.info(msg)
        if status_callback:
            status_callback(msg)

    try:
        # Validate configuration
        api_key = config.get('api_key')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError("GEMINI_API_KEY not configured in .env file")

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        # Get configuration with defaults
        model = config.get('model', 'gemini-2.5-flash-image')
        width = config.get('width', 800)
        height = config.get('height', 480)
        image_dir = config.get('image_dir', 'generated_images')

        update_status("Initializing Gemini client...")
        generator = GeminiImageGenerator(api_key=api_key, model=model)

        update_status(f"Generating image (this may take 5-15 seconds)...")
        raw_image = generator.generate_image(prompt, width=width, height=height)

        update_status("Saving original image...")
        saved_path = save_image_with_timestamp(raw_image, directory=image_dir)
        logger.info(f"Image saved to: {saved_path}")

        update_status("Preparing image for display...")
        display_image = prepare_image_for_display(raw_image, width, height)

        update_status("Initializing e-paper display...")
        epd = EPD()
        if epd.init() != 0:
            raise RuntimeError("EPD initialization failed - check hardware connections")

        update_status("Converting image to EPD buffer...")
        buffer = epd.getbuffer(display_image)

        update_status("Displaying image on EPD (this may take 15-30 seconds)...")
        epd.display(buffer)

        update_status("Putting display to sleep...")
        epd.sleep()

        return {
            'success': True,
            'message': 'Image generated and displayed successfully!',
            'image_path': saved_path
        }

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        logger.error(f"Generation failed: {error_msg}", exc_info=True)

        # Always try to cleanup EPD
        if epd is not None:
            try:
                epd.sleep()
            except Exception as cleanup_error:
                logger.error(f"EPD cleanup failed: {cleanup_error}")

        return {
            'success': False,
            'error': str(e),
            'message': f'Failed: {error_msg}'
        }
