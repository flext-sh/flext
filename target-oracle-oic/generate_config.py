#!/usr/bin/env python3
"""Generate config.json from .env file for target-oracle-oic."""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def generate_config() -> dict[str, Any]:
    """Generate config.json from environment variables."""
    # OAuth2 configuration
    oauth_config = {
        "base_url": os.getenv("OIC_IDCS_CLIENT_AUD", "").rstrip("/"),
        "oauth_client_id": os.getenv("OIC_IDCS_CLIENT_ID"),
        "oauth_client_secret": os.getenv("OIC_IDCS_CLIENT_SECRET"),
        "oauth_token_url": f"{os.getenv('OIC_IDCS_URL')}/oauth2/v1/token",
        "oauth_scope": os.getenv("OIC_IDCS_CLIENT_AUD"),
    }

    # Target-specific configuration
    target_config = {
        "import_mode": os.getenv("OIC_IMPORT_MODE", "create_or_update"),
        "activate_integrations": os.getenv("OIC_ACTIVATE_INTEGRATIONS", "false").lower()
        == "true",
        "overwrite_existing": os.getenv("OIC_OVERWRITE_EXISTING", "false").lower()
        == "true",
        "validate_before_import": os.getenv(
            "OIC_VALIDATE_BEFORE_IMPORT", "true"
        ).lower()
        == "true",
    }

    # Performance settings
    performance_config = {
        "batch_size": int(os.getenv("OIC_BATCH_SIZE", "10")),
        "max_concurrent_uploads": int(os.getenv("OIC_MAX_CONCURRENT_UPLOADS", "3")),
        "request_timeout": int(os.getenv("OIC_TIMEOUT", "60")),
    }

    # Debug settings
    debug_config = {
        "debug": os.getenv("OIC_DEBUG", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

    # Combine all configurations
    config = {
        **oauth_config,
        **target_config,
        **performance_config,
        **debug_config,
    }

    # Remove None values
    return {k: v for k, v in config.items() if v is not None}


def main() -> None:
    """Execute the config generation process."""
    config = generate_config()

    # Check if config.json already exists
    config_path = Path("config.json")
    if config_path.exists():
        response = input().strip().lower()
        if response != "y":
            return

    # Write config.json
    config_file = Path(config_path)
    with config_file.open("w") as f:
        json.dump(config, f, indent=2)


if __name__ == "__main__":
    main()
