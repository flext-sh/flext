#!/usr/bin/env python3
"""Generate config.json from .env file for tap-oracle-oic."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_config():
    """Generate config.json from environment variables."""
    # OAuth2 configuration
    oauth_config = {
        "base_url": os.getenv("OIC_IDCS_CLIENT_AUD", "").rstrip("/"),
        "oauth_client_id": os.getenv("OIC_IDCS_CLIENT_ID"),
        "oauth_client_secret": os.getenv("OIC_IDCS_CLIENT_SECRET"),
        "oauth_token_url": f"{os.getenv('OIC_IDCS_URL')}/oauth2/v1/token",
        "oauth_scope": os.getenv("OIC_IDCS_CLIENT_AUD"),
    }

    # API configuration
    api_config = {
        "api_version": os.getenv("OIC_API_VERSION", "v1"),
        "page_size": int(os.getenv("OIC_PAGE_SIZE", "100")),
        "request_timeout": int(os.getenv("OIC_TIMEOUT", "60")),
        "max_retries": int(os.getenv("HTTP_MAX_RETRIES", "3")),
    }

    # Extraction configuration
    entities = os.getenv("OIC_ENTITIES", "connections,integrations,packages,lookups")
    extraction_config = {
        "start_date": os.getenv("OIC_START_DATE", "2024-01-01T00:00:00Z"),
        "entities": entities.split(",") if entities else [],
        "enable_incremental": os.getenv("OIC_ENABLE_INCREMENTAL", "true").lower()
        == "true",
    }

    # Performance settings
    performance_config = {
        "max_concurrent_requests": int(os.getenv("OIC_MAX_CONCURRENT_REQUESTS", "5")),
        "batch_size": int(os.getenv("OIC_BATCH_SIZE", "1000")),
    }

    # Debug settings
    debug_config = {
        "debug": os.getenv("OIC_DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

    # Combine all configurations
    config = {
        **oauth_config,
        **api_config,
        **extraction_config,
        **performance_config,
        **debug_config,
    }

    # Remove None values
    return {k: v for k, v in config.items() if v is not None}


def main() -> None:
    """Main function."""
    config = generate_config()

    # Check if config.json already exists
    config_path = Path("config.json")
    if config_path.exists():
        response = input().strip().lower()
        if response != "y":
            return

    # Write config.json
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    main()
