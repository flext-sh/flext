"""Pytest configuration for target-oracle-wms tests."""

import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture()
def config() -> dict[str, Any]:
    """Return a test configuration."""
    return {
        "base_url": "https://test.oracle.com/wms/api/v1",
        "username": "test_user",
        "password": "test_pass",
        "timeout": 30,
        "enable_kpi_calculation": True,
        "enable_alerts": True,
        "expiry_alert_days": 30,
        "output_path": "./test_output",
        "output_format": "json",
    }


@pytest.fixture()
def temp_output_dir() -> Generator[Path]:
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture()
def sample_inventory_records() -> list[dict]:
    """Return sample inventory records."""
    return [
        {
            "item_id": "ITEM001",
            "item_description": "Test Item 1",
            "quantity": 100,
            "location": "A-01-01",
            "lot_number": "LOT001",
            "expiry_date": "2024-12-31",
            "unit_cost": 10.50,
        },
        {
            "item_id": "ITEM002",
            "item_description": "Test Item 2",
            "quantity": 50,
            "location": "A-01-02",
            "lot_number": "LOT002",
            "expiry_date": "2024-06-30",
            "unit_cost": 25.00,
        },
    ]


@pytest.fixture()
def sample_order_records() -> list[dict]:
    """Return sample order records."""
    return [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
            "order_date": "2024-01-01T10:00:00Z",
            "status": "SHIPPED",
            "total_amount": 1000.00,
            "ship_date": "2024-01-02T15:00:00Z",
        },
        {
            "order_id": "ORD002",
            "customer_id": "CUST002",
            "order_date": "2024-01-02T11:00:00Z",
            "status": "PENDING",
            "total_amount": 500.00,
            "ship_date": None,
        },
    ]


@pytest.fixture()
def sample_task_records() -> list[dict]:
    """Return sample task records."""
    return [
        {
            "task_id": "TASK001",
            "task_type": "PICK",
            "worker_id": "WORK001",
            "status": "COMPLETED",
            "start_time": "2024-01-01T08:00:00Z",
            "end_time": "2024-01-01T08:30:00Z",
            "items_processed": 50,
        },
        {
            "task_id": "TASK002",
            "task_type": "PACK",
            "worker_id": "WORK002",
            "status": "IN_PROGRESS",
            "start_time": "2024-01-01T09:00:00Z",
            "end_time": None,
            "items_processed": 25,
        },
    ]


@pytest.fixture()
def singer_schema() -> dict:
    """Return a sample Singer schema."""
    return {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "quantity": {"type": "integer"},
            "price": {"type": "number"},
            "updated_at": {"type": "string", "format": "date-time"},
        },
    }
