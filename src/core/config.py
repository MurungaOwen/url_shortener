"""Application configuration"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    app_name: str = "URL Shortener"
    app_version: str = "1.0.0"
    host: str = "localhost"
    port: int = 8000
    debug: bool = True

    # URL shortener settings
    short_code_length: int = 6
    base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
