"""Main FastAPI application"""
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.config import settings
from src.core import metrics
from src.api.routes import router
from src.services.storage import url_storage
from src.models.schemas import HealthResponse
from fastapi.responses import Response as FastAPIResponse, FileResponse, RedirectResponse
from prometheus_client import generate_latest


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application

    Returns:
        Configured FastAPI app instance
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="A URL shortener service with Prometheus metrics for Grafana monitoring",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add metrics middleware
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        """Track HTTP request metrics"""
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code

        metrics.http_requests_total.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()

        metrics.http_request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        return response

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "endpoints": {
                "GET /ui": "Web UI Dashboard",
                "POST /shorten": "Create shortened URL",
                "GET /{short_code}": "Redirect to original URL",
                "GET /api/urls": "List all URLs with stats",
                "GET /api/urls/{short_code}": "Get URL details",
                "PUT /api/urls/{short_code}": "Update a URL",
                "DELETE /api/urls/{short_code}": "Delete a URL",
                "POST /api/urls/bulk-delete": "Delete multiple URLs",
                "GET /api/stats": "Get statistics",
                "GET /api/search?q={query}": "Search URLs",
                "GET /health": "Health check",
                "GET /metrics": "Prometheus metrics",
                "GET /docs": "API documentation (Swagger UI)",
                "GET /redoc": "API documentation (ReDoc)"
            }
        }

    # Health check endpoint (must be before router to avoid conflict with /{short_code})
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """
        Health check endpoint

        Returns:
            HealthResponse with status and URL count
        """
        return HealthResponse(
            status="healthy",
            total_urls=url_storage.count()
        )

    # Metrics endpoint (must be before router to avoid conflict with /{short_code})
    @app.get("/metrics")
    async def get_metrics():
        """
        Prometheus metrics endpoint

        Returns:
            Prometheus metrics in text format
        """
        # Update system metrics before returning
        metrics.update_system_metrics()
        return FastAPIResponse(content=generate_latest(), media_type="text/plain")

    # UI Routes
    @app.get("/ui")
    async def ui_redirect():
        """Redirect to UI"""
        return RedirectResponse(url="/static/index.html")

    @app.get("/favicon.ico")
    async def favicon():
        """Serve favicon"""
        return FileResponse("static/favicon.ico", media_type="image/x-icon")

    # Include routes (must be AFTER /health and /metrics to avoid conflicts)
    app.include_router(router)

    # Mount static files for frontend UI (must be last)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    return app


# Create app instance
app = create_app()
