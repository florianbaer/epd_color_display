"""Application configuration using Pydantic Settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini API
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-image"

    # EPD Display
    epd_width: int = 800
    epd_height: int = 480

    # Storage
    image_dir: str = "generated_images"
    prompt_file: str = "prompt.md"
    prompt_history_file: str = "prompt_history.csv"

    # Scheduler
    auto_generate: bool = True
    schedule_time: str = "19:00"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Timezone
    tz: str = "UTC"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def prompt_path(self) -> Path:
        """Get the full path to the prompt file."""
        return Path(self.prompt_file)

    @property
    def prompt_history_path(self) -> Path:
        """Get the full path to the prompt history file."""
        return Path(self.prompt_history_file)

    @property
    def image_directory(self) -> Path:
        """Get the full path to the image directory."""
        return Path(self.image_dir)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
