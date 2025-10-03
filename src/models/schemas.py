"""Pydantic models for request/response validation"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


class URLCreate(BaseModel):
    """Schema for creating a shortened URL"""

    url: HttpUrl = Field(..., description="The original URL to shorten")
    custom_code: Optional[str] = Field(
        None,
        description="Optional custom short code",
        min_length=3,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$"
    )


class URLUpdate(BaseModel):
    """Schema for updating a shortened URL"""

    url: HttpUrl = Field(..., description="The new original URL")


class URLResponse(BaseModel):
    """Schema for URL response"""

    short_code: str = Field(..., description="The generated short code")
    original_url: str = Field(..., description="The original URL")
    short_url: str = Field(..., description="The complete shortened URL")


class URLDetailResponse(BaseModel):
    """Schema for detailed URL information"""

    short_code: str = Field(..., description="The short code")
    original_url: str = Field(..., description="The original URL")
    short_url: str = Field(..., description="The complete shortened URL")
    access_count: int = Field(..., description="Number of times accessed")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class URLListItem(BaseModel):
    """Schema for URL list item"""

    short_code: str
    original_url: str
    short_url: str
    access_count: Optional[int] = 0


class URLListResponse(BaseModel):
    """Schema for list of URLs"""

    total: int = Field(..., description="Total number of URLs")
    urls: list[URLListItem]


class HealthResponse(BaseModel):
    """Schema for health check response"""

    status: str
    total_urls: int


class MessageResponse(BaseModel):
    """Generic message response"""

    message: str


class URLStatsResponse(BaseModel):
    """Schema for URL statistics"""

    total_urls: int
    total_accesses: int
    most_accessed: Optional[List[dict]] = []
    least_accessed: Optional[List[dict]] = []


class BulkDeleteRequest(BaseModel):
    """Schema for bulk delete request"""

    short_codes: List[str] = Field(..., description="List of short codes to delete")


class BulkDeleteResponse(BaseModel):
    """Schema for bulk delete response"""

    deleted_count: int
    failed_codes: List[str] = []
    message: str


class URLSearchResponse(BaseModel):
    """Schema for URL search results"""

    total: int
    urls: List[URLListItem]
