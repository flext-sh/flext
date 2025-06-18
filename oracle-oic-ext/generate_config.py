#!/usr/bin/env python3
"""Generate config.json from .env file for oracle-oic-ext."""

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

    # Extension-specific configuration
    extension_config = {
        "instance_id": os.getenv("OIC_INSTANCE_ID"),
        "region": os.getenv("OIC_REGION"),
        "environment": os.getenv("OIC_ENVIRONMENT", "test"),
    }

    # Monitoring configuration
    monitoring_config = {
        "enable_monitoring": os.getenv("OIC_ENABLE_MONITORING", "true").lower()
        == "true",
        "monitoring_interval": int(os.getenv("OIC_MONITORING_INTERVAL", "60")),
        "alert_threshold": int(os.getenv("OIC_ALERT_THRESHOLD", "90")),
    }

    # Lifecycle configuration
    lifecycle_config = {
        "auto_activate": os.getenv("OIC_AUTO_ACTIVATE", "false").lower() == "true",
        "health_check_interval": int(os.getenv("OIC_HEALTH_CHECK_INTERVAL", "300")),
    }

    # Debug settings
    debug_config = {
        "debug": os.getenv("OIC_DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

    # Combine all configurations
    config = {
        **oauth_config,
        **extension_config,
        **monitoring_config,
        **lifecycle_config,
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
