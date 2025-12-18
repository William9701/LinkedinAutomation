from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TopicInput(BaseModel):
    """Custom topic input for post generation"""
    topic: str = Field(..., description="The topic to discuss")
    prompt: Optional[str] = Field(None, description="Custom prompt/context for the topic")
    category: Optional[str] = Field("General", description="Topic category")


class CustomPostRequest(BaseModel):
    """Request model for custom post creation"""
    topic: Optional[str] = Field(None, description="Topic to discuss")
    prompt: Optional[str] = Field(None, description="Custom prompt for content generation")
    category: Optional[str] = Field("General", description="Topic category")
    image_url: Optional[str] = Field(None, description="URL to image if provided")


class PostResponse(BaseModel):
    """Response model for post creation"""
    success: bool
    message: str
    post_urn: Optional[str] = None
    content: Optional[str] = None
    hashtags: Optional[List[str]] = None


class GeneratePreviewRequest(BaseModel):
    """Request model for content preview generation"""
    topic: str
    prompt: Optional[str] = None
    category: Optional[str] = Field("General", description="Topic category")


class PreviewResponse(BaseModel):
    """Response model for content preview"""
    content: str
    hashtags: List[str]
    image_prompt: Optional[str] = None


class ScheduleItem(BaseModel):
    """Schedule item model"""
    date: str
    time: str
    type: str  # "morning" or "evening"
    status: str  # "scheduled", "cancelled", "posted"


class StatusResponse(BaseModel):
    """API status response"""
    status: str
    total_topics: int
    unused_topics: int
    next_scheduled_post: Optional[str] = None
