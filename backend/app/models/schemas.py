"""Pydantic models for API request/response schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    """Request model for updating a prompt."""
    prompt: str = Field(..., min_length=1, max_length=1000)


class PromptResponse(BaseModel):
    """Response model for a prompt."""
    prompt: str


class PromptHistoryItem(BaseModel):
    """A single prompt history entry."""
    timestamp: str
    prompt: str


class PromptHistoryResponse(BaseModel):
    """Response model for prompt history."""
    prompts: List[PromptHistoryItem]


class GenerationStatus(BaseModel):
    """Current generation task status."""
    status: str = Field(..., description="Status: idle, running, complete, error")
    message: str
    image_path: Optional[str] = None
    error: Optional[str] = None


class GenerationStartResponse(BaseModel):
    """Response when generation is started."""
    status: str
    message: str


class SchedulerStatus(BaseModel):
    """Scheduler configuration and status."""
    enabled: bool
    schedule_time: str
    next_run: Optional[str] = None
    timezone: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0.0"


class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool
    message: str


class ImageInfo(BaseModel):
    """Information about a generated image."""
    filename: str
    path: str
    url: str
    created_at: str
    size_bytes: int


class ImageGalleryResponse(BaseModel):
    """Response model for image gallery."""
    images: List[ImageInfo]
    total: int


class FeedImageInfo(BaseModel):
    """Image info within a feed group (no prompt needed)."""
    filename: str
    url: str
    created_at: str
    size_bytes: int


class FeedGroup(BaseModel):
    """A group of images generated from the same prompt."""
    prompt: str
    generated_at: str
    images: List[FeedImageInfo]


class FeedResponse(BaseModel):
    """Response model for gallery feed."""
    groups: List[FeedGroup]
    total_images: int
    has_more: bool


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    type: str
    data: Optional[dict] = None


class UploadResponse(BaseModel):
    """Response after a successful image upload."""
    success: bool
    filename: str
    url: str
    message: str
