# Architecture Documentation

## Overview

This URL shortener is built using FastAPI with a clean, modular architecture that separates concerns into distinct layers. The application is designed for learning Prometheus metrics and Grafana monitoring while maintaining production-ready code organization.

## Architecture Layers

```
┌─────────────────────────────────────────────────┐
│              Client (HTTP Requests)              │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│            FastAPI Application (main.py)         │
│  - CORS Middleware                               │
│  - Metrics Middleware (HTTP tracking)            │
│  - Route Registration                            │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│              API Routes (api/routes.py)          │
│  - Request Validation (Pydantic)                 │
│  - Business Logic Orchestration                  │
│  - Response Formatting                           │
└─────────────────────────────────────────────────┘
                       ↓
        ┌──────────────┴──────────────┐
        ↓                              ↓
┌──────────────────┐          ┌──────────────────┐
│  Services Layer  │          │  Metrics Layer   │
│  (storage.py)    │          │  (metrics.py)    │
│                  │          │                  │
│  - URL Storage   │          │  - Counters      │
│  - CRUD Ops      │          │  - Histograms    │
│                  │          │  - Gauges        │
└──────────────────┘          └──────────────────┘
        ↓                              ↓
┌──────────────────┐          ┌──────────────────┐
│   Utils Layer    │          │  Prometheus      │
│   (utils.py)     │          │  Exporter        │
│                  │          │                  │
│  - Hash Gen      │          │  /metrics        │
│  - Validation    │          │  endpoint        │
└──────────────────┘          └──────────────────┘
```

## Component Breakdown

### 1. Entry Point (`run.py`)
- Simple application runner
- Loads configuration from settings
- Starts uvicorn server with hot-reload in debug mode

### 2. Main Application (`app/main.py`)
**Responsibilities:**
- FastAPI app initialization
- Middleware registration (CORS, metrics)
- Route registration
- Application factory pattern

**Key Features:**
- **Metrics Middleware**: Intercepts all HTTP requests to track:
  - Request duration
  - Request count by method, endpoint, and status code
  - Automatic metric recording before returning response

### 3. Configuration (`app/core/config.py`)
**Responsibilities:**
- Centralized configuration management
- Environment variable loading via Pydantic Settings
- Default values for all settings

**Settings:**
- App metadata (name, version)
- Server config (host, port)
- URL shortener config (code length, base URL)
- Environment-based configuration (.env file support)

### 4. Data Models (`app/models/schemas.py`)
**Responsibilities:**
- Request/response validation using Pydantic
- Type safety across the application
- Automatic API documentation generation

**Models:**
- `URLCreate`: Input for creating shortened URLs
- `URLResponse`: Response with short code and URLs
- `URLListResponse`: Paginated list of URLs
- `HealthResponse`: Health check status
- `MessageResponse`: Generic success/error messages

### 5. API Routes (`app/api/routes.py`)
**Responsibilities:**
- HTTP endpoint definitions
- Request handling and validation
- Business logic orchestration
- Metrics recording

**Endpoints:**
- `POST /shorten`: Create shortened URL
  - Validates input
  - Generates/validates short code
  - Stores mapping
  - Records metrics (creation count, timing, custom code usage)

- `GET /{short_code}`: Redirect to original URL
  - Looks up short code
  - Records access metrics (per-code counter, timing)
  - Returns 302 redirect or 404

- `GET /api/urls`: List all URLs
  - Retrieves all mappings
  - Formats for display

- `DELETE /api/urls/{short_code}`: Delete URL
  - Validates existence
  - Removes mapping
  - Updates gauge metrics

- `GET /health`: Health check
  - Returns system status
  - Current URL count

- `GET /metrics`: Prometheus metrics
  - Exports all metrics in Prometheus format
  - Used by Prometheus scraper

### 6. Storage Service (`app/services/storage.py`)
**Responsibilities:**
- URL mapping persistence (in-memory)
- CRUD operations for URLs
- Singleton pattern for global access

**Operations:**
- `save()`: Store URL mapping
- `get()`: Retrieve original URL
- `exists()`: Check if code exists
- `delete()`: Remove mapping
- `get_all()`: Retrieve all mappings
- `count()`: Get total count

**Design Pattern:**
- Singleton instance (`url_storage`)
- Can be easily swapped for database implementation (Redis, PostgreSQL, etc.)

### 7. Utilities (`app/core/utils.py`)
**Responsibilities:**
- Helper functions
- Code generation logic
- Validation utilities

**Functions:**
- `generate_short_code()`: MD5 hash-based code generation with collision handling
- `build_short_url()`: Constructs full shortened URL
- `validate_custom_code()`: Validates user-provided codes

### 8. Metrics (`app/core/metrics.py`)
**Responsibilities:**
- Prometheus metric definitions
- Metric type configuration (counters, histograms, gauges)

**Metric Categories:**

**Counters** (monotonically increasing):
- `url_creation_counter`: Total URLs created
- `url_creation_with_custom_code_counter`: Custom code usage
- `url_access_counter`: Per-code access (with label)
- `url_not_found_counter`: 404 errors
- `url_deletion_counter`: Deletions
- `http_requests_total`: All HTTP requests (labeled)

**Histograms** (distribution of values):
- `redirect_duration`: Redirect latency buckets
- `url_creation_duration`: Creation latency buckets
- `http_request_duration`: General request latency

**Gauges** (can go up/down):
- `total_urls_gauge`: Current URL count in storage

## Data Flow Examples

### Creating a Shortened URL

1. **Client** sends POST to `/shorten` with JSON body
2. **Metrics Middleware** starts timer
3. **Route Handler** receives request
4. **Pydantic** validates `URLCreate` model
5. **Utils** generates short code (or validates custom)
6. **Storage** checks for collisions, saves mapping
7. **Metrics** increments counters, updates gauge, records timing
8. **Route Handler** returns `URLResponse`
9. **Metrics Middleware** records HTTP metrics

### Accessing a Shortened URL

1. **Client** sends GET to `/{short_code}`
2. **Metrics Middleware** starts timer
3. **Route Handler** receives short_code parameter
4. **Storage** looks up original URL
5. If found:
   - **Metrics** increments access counter for this code
   - **Metrics** records redirect duration
   - Returns 302 redirect
6. If not found:
   - **Metrics** increments not_found counter
   - Returns 404 error
7. **Metrics Middleware** records HTTP metrics

### Prometheus Scraping

1. **Prometheus** sends GET to `/metrics`
2. **Route Handler** calls `generate_latest()`
3. **Prometheus Client** collects all metric values
4. Returns text format with all metrics
5. **Prometheus** stores time-series data
6. **Grafana** queries Prometheus for visualization

## Design Patterns Used

### 1. **Factory Pattern**
- `create_app()` function builds and configures FastAPI instance
- Allows multiple app instances with different configs

### 2. **Singleton Pattern**
- `url_storage` provides single shared storage instance
- `settings` provides single configuration object

### 3. **Dependency Injection** (via FastAPI)
- Pydantic models injected into route handlers
- Automatic validation and parsing

### 4. **Middleware Pattern**
- Metrics middleware wraps all requests
- CORS middleware handles cross-origin requests
- Chainable, reusable components

### 5. **Repository Pattern**
- `URLStorage` class abstracts data access
- Easy to swap implementations (memory → Redis → DB)

## Scalability Considerations

### Current Architecture (Learning/Development)
- **In-memory storage**: Fast but not persistent or distributed
- **Single process**: No horizontal scaling
- **No caching**: Every request hits storage

### Production Improvements
1. **Replace Storage**:
   - Redis for fast, persistent, distributed storage
   - PostgreSQL for relational data with indexes
   - DynamoDB for serverless scaling

2. **Add Caching**:
   - Redis cache for hot URLs
   - LRU eviction for memory management

3. **Horizontal Scaling**:
   - Stateless design allows multiple instances
   - Load balancer distributes traffic
   - Shared storage backend

4. **Advanced Metrics**:
   - APM tools (DataDog, New Relic)
   - Distributed tracing (Jaeger)
   - Custom business metrics

## Monitoring with Prometheus & Grafana

### Prometheus Setup
1. Configure Prometheus to scrape `/metrics` endpoint
2. Set scrape interval (e.g., 15s)
3. Store time-series data

### Grafana Dashboards
**Suggested Panels:**
- **Request Rate**: `rate(url_shortener_http_requests_total[5m])`
- **Error Rate**: `rate(url_shortener_urls_not_found_total[5m])`
- **P95 Latency**: `histogram_quantile(0.95, redirect_duration)`
- **Active URLs**: `url_shortener_total_urls`
- **Top URLs**: `topk(10, url_shortener_urls_accessed_total)`
- **Creation vs Access**: Compare creation and access counters

### Alerts
- High error rate: `rate(url_not_found[5m]) > 10`
- Slow redirects: `redirect_duration > 1s`
- High request rate: `rate(http_requests_total[1m]) > 1000`

## Extension Points

### Easy to Add
1. **Database Backend**: Implement new storage class with same interface
2. **Rate Limiting**: Add middleware for request throttling
3. **Authentication**: JWT middleware for API access control
4. **URL Expiration**: Add TTL field and background cleanup
5. **Click Analytics**: Track timestamp, user-agent, geo-location
6. **Custom Domains**: Multi-tenant with domain routing

### Code Modularity Benefits
- **Testable**: Each layer can be unit tested independently
- **Maintainable**: Clear separation of concerns
- **Extensible**: New features added without modifying core
- **Readable**: Self-documenting structure and naming
