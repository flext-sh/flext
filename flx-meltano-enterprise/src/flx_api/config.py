"""
FastAPI-specific configuration.
"""

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """API-specific settings."""

    # API Configuration
    port: int = Field(default=8081, env="FLX_API_PORT")
    workers: int = Field(default=4, env="FLX_API_WORKERS")

    # CORS
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8080",
        ],
        env="FLX_CORS_ORIGINS",
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100)
    rate_limit_period: int = Field(default=60)  # seconds

    # WebSocket
    ws_heartbeat_interval: int = Field(default=30)  # seconds
    ws_max_connections: int = Field(default=1000)

    # JWT (reuse from main config)
    jwt_secret: str = Field(..., env="FLX_JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration: int = Field(default=3600)

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
api_settings = APISettings()
