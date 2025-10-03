"""Utility functions"""
import hashlib
from src.core.config import settings


def generate_short_code(url: str, attempt: int = 0) -> str:
    """
    Generate a short code from URL using MD5 hash

    Args:
        url: The original URL
        attempt: Collision counter for generating alternative codes

    Returns:
        A short code of configured length
    """
    input_string = f"{url}{attempt}" if attempt > 0 else url
    hash_object = hashlib.md5(input_string.encode())
    return hash_object.hexdigest()[:settings.short_code_length]


def build_short_url(short_code: str) -> str:
    """
    Build the complete shortened URL

    Args:
        short_code: The short code

    Returns:
        Complete shortened URL
    """
    return f"{settings.base_url}/{short_code}"


def validate_custom_code(code: str) -> bool:
    """
    Validate custom short code format

    Args:
        code: The custom code to validate

    Returns:
        True if valid, False otherwise
    """
    if not code:
        return False
    if len(code) < 3 or len(code) > 20:
        return False
    # Only allow alphanumeric, underscore, and hyphen
    return code.replace('_', '').replace('-', '').isalnum()
