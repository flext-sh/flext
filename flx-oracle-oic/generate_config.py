#!/usr/bin/env python3
"""Generate config.json from .env file for flx-oracle-oic."""

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

    # FLX Adapter configuration
    adapter_config = {
        "adapter_name": "flx-oracle-oic",
        "adapter_type": "http",
        "instance_id": os.getenv("OIC_INSTANCE_ID"),
        "region": os.getenv("OIC_REGION"),
        "environment": os.getenv("OIC_ENVIRONMENT", "test"),
    }

    # HTTP Client configuration
    http_config = {
        "timeout": int(os.getenv("HTTP_TIMEOUT", "120")),
        "verify_ssl": os.getenv("HTTP_VERIFY_SSL", "true").lower() == "true",
        "max_retries": int(os.getenv("HTTP_MAX_RETRIES", "1")),
        "retry_delay": int(os.getenv("HTTP_RETRY_DELAY", "2")),
        "user_agent": os.getenv("HTTP_USER_AGENT", "FLX-OIC-HTTP-Client/1.0"),
    }

    # Performance settings
    performance_config = {
        "buffer_size_bytes": int(os.getenv("HTTP_BUFFER_SIZE_BYTES", "8192")),
        "keepalive_timeout_seconds": float(
            os.getenv("HTTP_KEEPALIVE_TIMEOUT_SECONDS", "30.0")
        ),
    }

    # Debug settings
    debug_config = {
        "debug": os.getenv("OIC_DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "output_format": os.getenv("OUTPUT", "TABLE"),
    }

    # Combine all configurations
    config = {
        **oauth_config,
        **adapter_config,
        **http_config,
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
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    main()
