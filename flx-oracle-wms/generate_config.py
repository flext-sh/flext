#!/usr/bin/env python3
"""Generate config files from .env for flx-oracle-wms."""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


# Load environment variables
load_dotenv()


def generate_tap_config() -> dict[str, Any]:
    """Generate tap configuration."""
    return {
        "base_url": os.getenv("WMS_BASE_URL", "https://test.oracle.com/wms/api/v1"),
        "username": os.getenv("WMS_USERNAME", "test_user"),
        "password": os.getenv("WMS_PASSWORD", "test_password"),
        "timeout": int(os.getenv("WMS_TIMEOUT", "300")),
        "page_size": int(os.getenv("WMS_PAGE_SIZE", "1000")),
        "start_date": os.getenv("WMS_START_DATE", "2024-01-01T00:00:00Z"),
    }


def generate_target_config() -> dict[str, Any]:
    """Generate target configuration."""
    return {
        "base_url": os.getenv("WMS_BASE_URL", "https://test.oracle.com/wms/api/v1"),
        "username": os.getenv("WMS_USERNAME", "test_user"),
        "password": os.getenv("WMS_PASSWORD", "test_password"),
        "enable_kpi_calculation": True,
        "enable_alerts": True,
        "expiry_alert_days": 30,
        "output_path": os.getenv("WMS_OUTPUT_PATH", "./output"),
        "output_format": os.getenv("WMS_OUTPUT_FORMAT", "json"),
    }


def generate_pipeline_config() -> dict[str, Any]:
    """Generate pipeline configuration."""
    return {
        "name": "Oracle WMS Integration",
        "tap_config_path": "./config/tap_config.json",
        "target_config_path": "./config/target_config.json",
        "state_path": "./state.json",
        "catalog_path": "./catalog.json",
        "pipelines": [
            {
                "name": "test_pipeline",
                "description": "Test pipeline for E2E validation",
                "streams": ["inventory", "orders"],
                "enabled": True,
            }
        ],
        "monitoring": {
            "enabled": True,
            "metrics_port": int(os.getenv("WMS_METRICS_PORT", "9090")),
            "log_level": os.getenv("WMS_LOG_LEVEL", "INFO"),
        },
    }


def main() -> None:
    """Generate all config files."""
    # Create config directory
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    # Generate tap config
    tap_config = generate_tap_config()
    with (config_dir / "tap_config.json").open("w") as f:
        json.dump(tap_config, f, indent=2)

    # Generate target config
    target_config = generate_target_config()
    with (config_dir / "target_config.json").open("w") as f:
        json.dump(target_config, f, indent=2)

    # Generate pipeline config
    pipeline_config = generate_pipeline_config()
    with (config_dir / "pipeline_config.json").open("w") as f:
        json.dump(pipeline_config, f, indent=2)


if __name__ == "__main__":
    main()
