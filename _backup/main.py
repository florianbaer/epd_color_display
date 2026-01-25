"""
Main script to generate spring landscape images using Gemini API
and display them on the Waveshare 7.3" e-paper display.

CLI entry point that uses core.py for generation logic.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from core import generate_and_display_image


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    try:
        # Load environment variables
        logger.info("Loading environment configuration...")
        load_dotenv()

        # Read prompt from prompt.md
        prompt_file = Path(__file__).parent / 'prompt.md'
        if not prompt_file.exists():
            logger.error("prompt.md file not found")
            logger.error("Please create prompt.md with your desired prompt")
            sys.exit(1)

        prompt = prompt_file.read_text(encoding='utf-8').strip()
        if not prompt:
            logger.error("prompt.md is empty")
            logger.error("Please add a prompt to prompt.md")
            sys.exit(1)

        # Build configuration
        config = {
            'api_key': os.getenv("GEMINI_API_KEY"),
            'model': os.getenv("GEMINI_MODEL", "gemini-2.5-flash-image"),
            'width': int(os.getenv("EPD_WIDTH", "800")),
            'height': int(os.getenv("EPD_HEIGHT", "480")),
            'image_dir': os.getenv("IMAGE_DIR", "generated_images")
        }

        logger.info(f"Configuration loaded - Model: {config['model']}, Resolution: {config['width']}x{config['height']}")
        logger.info(f"Prompt: {prompt[:80]}...")

        # Generate and display image using core logic
        result = generate_and_display_image(prompt, config)

        if result['success']:
            logger.info(f"✓ {result['message']}")
            sys.exit(0)
        else:
            logger.error(f"✗ {result['message']}")
            if 'error' in result:
                logger.error(f"Error details: {result['error']}")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
