"""API route handlers"""
import time
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, Response
from prometheus_client import generate_latest

from src.models.schemas import (
    URLCreate,
    URLUpdate,
    URLResponse,
    URLDetailResponse,
    URLListResponse,
    URLListItem,
    HealthResponse,
    MessageResponse,
    URLStatsResponse,
    BulkDeleteRequest,
    BulkDeleteResponse,
    URLSearchResponse
)
from src.services.storage import url_storage
from src.core.utils import generate_short_code, build_short_url
from src.core import metrics

router = APIRouter()


@router.post("/shorten", response_model=URLResponse, status_code=201)
async def shorten_url(url_data: URLCreate):
    """
    Create a shortened URL

    Args:
        url_data: URL creation request

    Returns:
        URLResponse with short code and URLs

    Raises:
        HTTPException: If custom code already exists
    """
    start_time = time.time()
    original_url = str(url_data.url)

    # Use custom code if provided, otherwise generate one
    if url_data.custom_code:
        short_code = url_data.custom_code
        if url_storage.exists(short_code):
            raise HTTPException(
                status_code=400,
                detail=f"Custom code '{short_code}' already exists"
            )
        metrics.url_creation_with_custom_code_counter.inc()
    else:
        # Generate short code and handle collisions
        short_code = generate_short_code(original_url)
        attempt = 1
        while url_storage.exists(short_code):
            short_code = generate_short_code(original_url, attempt)
            attempt += 1

    # Save to storage
    url_storage.save(short_code, original_url)

    # Update metrics
    metrics.url_creation_counter.inc()
    metrics.total_urls_gauge.set(url_storage.count())
    metrics.url_creation_duration.observe(time.time() - start_time)

    return URLResponse(
        short_code=short_code,
        original_url=original_url,
        short_url=build_short_url(short_code)
    )


@router.get("/{short_code}")
async def redirect_url(short_code: str):
    """
    Redirect to original URL

    Args:
        short_code: The short code to look up

    Returns:
        RedirectResponse to original URL

    Raises:
        HTTPException: If short code not found
    """
    start_time = time.time()

    original_url = url_storage.get(short_code)

    if not original_url:
        metrics.url_not_found_counter.inc()
        raise HTTPException(status_code=404, detail="URL not found")

    # Update metrics and access count
    url_storage.increment_access(short_code)
    metrics.url_access_counter.labels(short_code=short_code).inc()
    metrics.redirect_duration.observe(time.time() - start_time)

    return RedirectResponse(url=original_url)


@router.get("/api/urls/{short_code}", response_model=URLDetailResponse)
async def get_url_details(short_code: str):
    """
    Get detailed information about a specific URL

    Args:
        short_code: The short code to look up

    Returns:
        URLDetailResponse with URL details

    Raises:
        HTTPException: If short code not found
    """
    details = url_storage.get_with_details(short_code)

    if not details:
        raise HTTPException(status_code=404, detail="URL not found")

    return URLDetailResponse(
        short_code=short_code,
        original_url=details["original_url"],
        short_url=build_short_url(short_code),
        access_count=details["access_count"],
        created_at=details["created_at"]
    )


@router.get("/api/urls", response_model=URLListResponse)
async def list_urls():
    """
    List all shortened URLs with access counts

    Returns:
        URLListResponse with all URLs
    """
    all_urls = url_storage.get_all_with_stats()

    urls = [
        URLListItem(
            short_code=item["short_code"],
            original_url=item["original_url"],
            short_url=build_short_url(item["short_code"]),
            access_count=item["access_count"]
        )
        for item in all_urls
    ]

    return URLListResponse(total=len(urls), urls=urls)


@router.put("/api/urls/{short_code}", response_model=URLResponse)
async def update_url(short_code: str, url_data: URLUpdate):
    """
    Update an existing shortened URL

    Args:
        short_code: The short code to update
        url_data: New URL data

    Returns:
        URLResponse with updated information

    Raises:
        HTTPException: If short code not found
    """
    new_url = str(url_data.url)

    if not url_storage.update(short_code, new_url):
        raise HTTPException(status_code=404, detail="URL not found")

    return URLResponse(
        short_code=short_code,
        original_url=new_url,
        short_url=build_short_url(short_code)
    )


@router.delete("/api/urls/{short_code}", response_model=MessageResponse)
async def delete_url(short_code: str):
    """
    Delete a shortened URL

    Args:
        short_code: The short code to delete

    Returns:
        MessageResponse confirming deletion

    Raises:
        HTTPException: If short code not found
    """
    if not url_storage.delete(short_code):
        raise HTTPException(status_code=404, detail="URL not found")

    # Update metrics
    metrics.url_deletion_counter.inc()
    metrics.total_urls_gauge.set(url_storage.count())

    return MessageResponse(message=f"URL '{short_code}' deleted successfully")


@router.post("/api/urls/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_urls(request: BulkDeleteRequest):
    """
    Delete multiple URLs at once

    Args:
        request: Bulk delete request with list of short codes

    Returns:
        BulkDeleteResponse with deletion results
    """
    deleted_count, failed_codes = url_storage.bulk_delete(request.short_codes)

    # Update metrics
    if deleted_count > 0:
        metrics.url_deletion_counter.inc(deleted_count)
        metrics.total_urls_gauge.set(url_storage.count())

    message = f"Successfully deleted {deleted_count} URL(s)"
    if failed_codes:
        message += f", {len(failed_codes)} failed"

    return BulkDeleteResponse(
        deleted_count=deleted_count,
        failed_codes=failed_codes,
        message=message
    )


@router.get("/api/stats", response_model=URLStatsResponse)
async def get_statistics():
    """
    Get URL statistics including most/least accessed URLs

    Returns:
        URLStatsResponse with statistics
    """
    stats = url_storage.get_stats()
    return URLStatsResponse(**stats)


@router.get("/api/search", response_model=URLSearchResponse)
async def search_urls(q: str):
    """
    Search URLs by short code or original URL

    Args:
        q: Search query string

    Returns:
        URLSearchResponse with matching URLs
    """
    results = url_storage.search(q)

    urls = [
        URLListItem(
            short_code=item["short_code"],
            original_url=item["original_url"],
            short_url=build_short_url(item["short_code"]),
            access_count=item["access_count"]
        )
        for item in results
    ]

    return URLSearchResponse(total=len(urls), urls=urls)


