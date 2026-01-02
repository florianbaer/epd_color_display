"""
Main script to generate spring landscape images using Gemini API
and display them on the Waveshare 7.3" e-paper display.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from epd_color import EPD
from gemini_client import GeminiImageGenerator
from image_utils import save_image_with_timestamp, prepare_image_for_display


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main orchestration function."""
    epd = None

    try:
        # Load environment variables
        logger.info("Loading environment configuration...")
        load_dotenv()

        # Get configuration
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            logger.error("GEMINI_API_KEY not found or not set in .env file")
            logger.error("Please edit .env and add your Gemini API key")
            sys.exit(1)

        prompt = os.getenv("IMAGE_PROMPT", "Generate a beautiful spring landscape with blooming flowers, green meadows, and blue sky")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-image")
        image_dir = os.getenv("IMAGE_DIR", "generated_images")
        width = int(os.getenv("EPD_WIDTH", "800"))
        height = int(os.getenv("EPD_HEIGHT", "480"))

        logger.info(f"Configuration loaded - Model: {model}, Resolution: {width}x{height}")

        # Generate image via Gemini API
        logger.info("Initializing Gemini client...")
        generator = GeminiImageGenerator(api_key=api_key, model=model)

        logger.info(f"Generating image at {width}x{height} (this may take 5-15 seconds)...")
        raw_image = generator.generate_image(prompt, width=width, height=height)

        # Save original image with timestamp
        saved_path = save_image_with_timestamp(raw_image, directory=image_dir)
        logger.info(f"Original image saved to: {saved_path}")

        # Prepare image for display (resize and center)
        display_image = prepare_image_for_display(raw_image, 800, 480)

        # Initialize EPD and display
        logger.info("Initializing e-paper display...")
        epd = EPD()
        if epd.init() != 0:
            raise RuntimeError("EPD initialization failed - check hardware connections")

        logger.info("Converting image to EPD buffer...")
        buffer = epd.getbuffer(display_image)

        logger.info("Displaying image on EPD (this may take 15-30 seconds)...")
        epd.display(buffer)

        logger.info("Putting display to sleep...")
        epd.sleep()

        logger.info("✓ Image generated and displayed successfully!")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        if epd is not None:
            try:
                epd.sleep()
            except:
                pass
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        if epd is not None:
            try:
                epd.sleep()
            except:
                pass
        sys.exit(1)


if __name__ == "__main__":
    main()
