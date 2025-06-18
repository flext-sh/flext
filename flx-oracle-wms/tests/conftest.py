"""Pytest configuration for flx-oracle-wms tests."""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from flx_oracle_wms.config import PipelineConfig, PipelineDefinition


@pytest.fixture
def tap_config() -> dict[str, Any]:
    """Return a test tap configuration."""
    return {
        "base_url": "https://test.oracle.com/wms/api/v1",
        "username": "test_user",
        "password": "test_pass",
        "timeout": 30,
        "page_size": 100,
        "start_date": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def target_config() -> dict[str, Any]:
    """Return a test target configuration."""
    return {
        "base_url": "https://test.oracle.com/wms/api/v1",
        "username": "test_user",
        "password": "test_pass",
        "enable_kpi_calculation": True,
        "enable_alerts": True,
        "output_path": "./test_output",
        "output_format": "json",
    }


@pytest.fixture
def temp_config_dir() -> Generator[Path]:
    """Create a temporary configuration directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def pipeline_config(
    temp_config_dir: Path, tap_config: dict, target_config: dict
) -> PipelineConfig:
    """Create a test pipeline configuration."""
    # Write config files
    tap_config_path = temp_config_dir / "tap_config.json"
    tap_config_path.write_text(json.dumps(tap_config))

    target_config_path = temp_config_dir / "target_config.json"
    target_config_path.write_text(json.dumps(target_config))

    state_path = temp_config_dir / "state.json"
    catalog_path = temp_config_dir / "catalog.json"

    # Create pipeline config
    return PipelineConfig(
        name="Test WMS Integration",
        tap_config_path=tap_config_path,
        target_config_path=target_config_path,
        state_path=state_path,
        catalog_path=catalog_path,
        pipelines=[
            PipelineDefinition(
                name="test_pipeline",
                description="Test pipeline",
                streams=["inventory", "orders"],
                enabled=True,
            ),
            PipelineDefinition(
                name="disabled_pipeline",
                description="Disabled pipeline",
                streams=["tasks"],
                enabled=False,
            ),
        ],
    )


@pytest.fixture
def sample_catalog() -> dict[str, Any]:
    """Return a sample catalog."""
    return {
        "streams": [
            {
                "stream": "inventory",
                "tap_stream_id": "inventory",
                "schema": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string"},
                        "quantity": {"type": "integer"},
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "table-key-properties": ["item_id"],
                            "forced-replication-method": "INCREMENTAL",
                            "valid-replication-keys": ["updated_at"],
                        },
                    }
                ],
            },
            {
                "stream": "orders",
                "tap_stream_id": "orders",
                "schema": {
                    "type": "object",
                    "properties": {
                        "order_id": {"type": "string"},
                        "customer_id": {"type": "string"},
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "table-key-properties": ["order_id"],
                        },
                    }
                ],
            },
        ]
    }


@pytest.fixture
def sample_state() -> dict[str, Any]:
    """Return a sample state."""
    return {
        "bookmarks": {
            "inventory": {
                "replication_key": "updated_at",
                "replication_key_value": "2024-01-01T00:00:00Z",
            }
        }
    }


@pytest.fixture
def singer_messages() -> list[str]:
    """Return sample Singer messages."""
    return [
        json.dumps(
            {
                "type": "SCHEMA",
                "stream": "inventory",
                "schema": {},
                "key_properties": ["item_id"],
            }
        ),
        json.dumps(
            {
                "type": "RECORD",
                "stream": "inventory",
                "record": {"item_id": "1", "quantity": 100},
            }
        ),
        json.dumps(
            {
                "type": "RECORD",
                "stream": "inventory",
                "record": {"item_id": "2", "quantity": 50},
            }
        ),
        json.dumps(
            {
                "type": "STATE",
                "value": {
                    "bookmarks": {"inventory": {"updated_at": "2024-01-02T00:00:00Z"}}
                },
            }
        ),
    ]
