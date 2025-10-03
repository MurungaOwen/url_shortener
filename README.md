# URL Shortener with Prometheus Metrics

A FastAPI-based URL shortener service with Prometheus metrics integration for Grafana monitoring.

## Project Structure

```
prom-proj/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoint handlers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Application configuration
│   │   ├── metrics.py       # Prometheus metrics definitions
│   │   └── utils.py         # Utility functions
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── __init__.py
│       └── storage.py       # In-memory URL storage
├── .env.example             # Example environment variables
├── requirements.txt         # Python dependencies
└── run.py                   # Application runner
```

## Installation

1. Create a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Copy `.env.example` to `.env` and customize settings:
```bash
cp .env.example .env
```

## Running the Application

```bash
python run.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /shorten` - Create a shortened URL
- `GET /{short_code}` - Redirect to original URL
- `GET /api/urls` - List all URLs
- `DELETE /api/urls/{short_code}` - Delete a URL
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics endpoint
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Prometheus Metrics

The `/metrics` endpoint exposes the following metrics:

### Counters
- `url_shortener_urls_created_total` - Total URLs created
- `url_shortener_custom_code_urls_total` - URLs created with custom codes
- `url_shortener_urls_accessed_total` - URL access count (with labels)
- `url_shortener_urls_not_found_total` - 404 errors
- `url_shortener_urls_deleted_total` - URLs deleted
- `url_shortener_http_requests_total` - Total HTTP requests (with method, endpoint, status)

### Histograms
- `url_shortener_redirect_duration_seconds` - Redirect response time
- `url_shortener_creation_duration_seconds` - URL creation response time
- `url_shortener_http_request_duration_seconds` - HTTP request duration

### Gauges
- `url_shortener_total_urls` - Current number of URLs in storage

## Example Usage

### Create a shortened URL:
```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com"}'
```

### Create with custom code:
```bash
curl -X POST "http://localhost:8000/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com", "custom_code": "example"}'
```

### Access shortened URL:
```bash
curl -L "http://localhost:8000/abc123"
```

### View metrics:
```bash
curl "http://localhost:8000/metrics"
```

## Grafana Integration

Configure Prometheus to scrape the `/metrics` endpoint, then create Grafana dashboards to visualize:
- Request rates and response times
- URL creation/access/deletion trends
- Error rates (404s)
- Active URL count

## Configuration

Environment variables (optional, defaults provided):
- `APP_NAME` - Application name (default: "URL Shortener")
- `APP_VERSION` - Version (default: "1.0.0")
- `HOST` - Server host (default: "localhost")
- `PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: true)
- `SHORT_CODE_LENGTH` - Length of generated codes (default: 6)
- `BASE_URL` - Base URL for shortened links (default: "http://localhost:8000")
