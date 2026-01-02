"""
Gemini API client for generating images.
"""

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

    def generate_image(self, prompt: str) -> Image.Image:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text description of the image to generate

        Returns:
            PIL Image object

        Raises:
            ValueError: If prompt is empty or response doesn't contain image
            Exception: For API errors
        """
        if not prompt:
            raise ValueError("Prompt cannot be empty")

        logger.info(f"Generating image with prompt: {prompt}")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt],
            )

            # Extract image from response
            for part in response.parts:
                if part.text is not None:
                    logger.debug(f"Response text: {part.text}")
                elif part.inline_data is not None:
                    image = part.as_image()
                    logger.info(f"Image generated successfully: {image.size[0]}x{image.size[1]}")
                    return image

            raise ValueError("No image data found in API response")

        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            raise
