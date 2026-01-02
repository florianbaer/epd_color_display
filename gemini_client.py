"""
Gemini API client for generating images.
"""
import io
import logging
from google import genai
from PIL import Image

logger = logging.getLogger(__name__)


class GeminiImageGenerator:
    """Client for generating images using Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-image"):
        """
        Initialize Gemini image generator.

        Args:
            api_key: Gemini API key
            model: Model to use for image generation
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        self.api_key = api_key
        self.model = model
        self.client = genai.Client(api_key=api_key)
        logger.info(f"Initialized Gemini client with model: {model}")

    def generate_image(self, prompt: str, width: int = 800, height: int = 480) -> Image.Image:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of the image to generate
            width: Desired image width (default: 800)
            height: Desired image height (default: 480)

        Returns:
            PIL Image object

        Raises:
            ValueError: If prompt is empty or response doesn't contain image
            Exception: For API errors
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty")

        # Add dimensions to prompt for better control
        full_prompt = f"{prompt}, resolution {width}x{height}, aspect ratio {width}:{height}"
        logger.info(f"Generating image with prompt: {full_prompt}")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[full_prompt],
            )

            # Extract image from response
            for part in response.parts:
                if part.text is not None:
                    logger.debug(f"Response text: {part.text}")
                elif part.inline_data is not None:
                    # Convert Gemini Image to PIL Image
                    gemini_image = part.as_image()
                    # Convert to PIL Image using _pil property or by converting to bytes
                    if hasattr(gemini_image, '_pil'):
                        pil_image = gemini_image._pil
                    else:
                        # Fallback: get the image data and convert
                        image_bytes = part.inline_data.data
                        pil_image = Image.open(io.BytesIO(image_bytes))

                    logger.info(f"Image generated successfully: {pil_image.size[0]}x{pil_image.size[1]}")
                    return pil_image

            raise ValueError("No image data found in API response")

        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            raise
