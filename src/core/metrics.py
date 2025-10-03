"""Prometheus metrics definitions"""
from prometheus_client import Counter, Histogram, Gauge


# URL Creation Metrics
url_creation_counter = Counter(
    'url_shortener_urls_created_total',
    'Total number of shortened URLs created'
)

url_creation_with_custom_code_counter = Counter(
    'url_shortener_custom_code_urls_total',
    'Total number of URLs created with custom codes'
)

# URL Access Metrics
url_access_counter = Counter(
    'url_shortener_urls_accessed_total',
    'Total number of times shortened URLs were accessed',
    ['short_code']
)

url_not_found_counter = Counter(
    'url_shortener_urls_not_found_total',
    'Total number of times a non-existent URL was requested'
)

# URL Deletion Metrics
url_deletion_counter = Counter(
    'url_shortener_urls_deleted_total',
    'Total number of URLs deleted'
)

# Performance Metrics
redirect_duration = Histogram(
    'url_shortener_redirect_duration_seconds',
    'Time spent processing redirect requests',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

url_creation_duration = Histogram(
    'url_shortener_creation_duration_seconds',
    'Time spent creating shortened URLs',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# State Metrics
total_urls_gauge = Gauge(
    'url_shortener_total_urls',
    'Current number of URLs in the database'
)

# HTTP Metrics
http_requests_total = Counter(
    'url_shortener_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration = Histogram(
    'url_shortener_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)
