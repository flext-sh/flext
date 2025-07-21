"""Test configuration for flext-oracle-wms.

Provides pytest fixtures and configuration for testing Oracle WMS integration
using real Oracle connections and WMS API patterns.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


# Test environment setup
@pytest.fixture(autouse=True)
def set_test_environment() -> Generator[None]:
    """Set test environment variables."""
    os.environ["FLEXT_ENV"] = "test"
    os.environ["FLEXT_LOG_LEVEL"] = "debug"
    os.environ["ORACLE_WMS_TEST_MODE"] = "true"
    yield
    # Cleanup
    os.environ.pop("FLEXT_ENV", None)
    os.environ.pop("FLEXT_LOG_LEVEL", None)
    os.environ.pop("ORACLE_WMS_TEST_MODE", None)


# Oracle WMS connection fixtures
@pytest.fixture
def oracle_wms_config() -> dict[str, Any]:
    """Oracle WMS connection configuration for testing."""
    return {
        "host": "localhost",
        "port": 1521,
        "database": "WMS",
        "username": "wms_user",
        "password": "wms_pass",
        "service_name": "WMSPDB1",
        "encoding": "UTF-8",
        "pool_size": 5,
        "pool_timeout": 30,
    }


@pytest.fixture
async def oracle_wms_connection(
    oracle_wms_config: dict[str, Any],
) -> AsyncGenerator[Any]:
    """Oracle WMS connection for testing."""
    # Convert dict config to proper OracleWMSConfig object
    from pydantic import HttpUrl

    from flext_oracle_wms.client import OracleWMSClient
    from flext_oracle_wms.config_module import OracleWMSConfig

    config = OracleWMSConfig(
        base_url=HttpUrl("https://test.example.com"),
        username=oracle_wms_config["username"],
        password=oracle_wms_config["password"],
        batch_size=oracle_wms_config.get("pool_size", 5),
        timeout_seconds=oracle_wms_config.get("pool_timeout", 30),
    )

    client = OracleWMSClient(config)
    # OracleWMSClient doesn't have async connect/disconnect methods
    # It uses context manager pattern instead
    yield client
    client.close()


# WMS API fixtures
@pytest.fixture
def wms_api_config() -> dict[str, Any]:
    """WMS API configuration for testing."""
    return {
        "base_url": "http://localhost:8080/wms",
        "api_version": "v1",
        "timeout": 30,
        "retries": 3,
        "auth": {
            "type": "basic",
            "username": "wms_api_user",
            "password": "wms_api_pass",
        },
    }


@pytest.fixture
async def wms_api_client(wms_api_config: dict[str, Any]) -> AsyncGenerator[Any]:
    """WMS API client for testing."""

    # Mock WMS API client for testing since api_client module doesn't exist
    class MockWMSAPIClient:
        def __init__(self, config: dict[str, Any]) -> None:
            self.config = config

        async def close(self) -> None:
            """Close the client connection."""

    client = MockWMSAPIClient(wms_api_config)
    yield client
    await client.close()


# WMS entity fixtures
@pytest.fixture
def sample_inventory_data() -> list[dict[str, Any]]:
    """Sample inventory data for testing."""
    return [
        {
            "item_id": "ITEM001",
            "location": "A01-B02-C03",
            "quantity": 100,
            "unit": "EA",
            "status": "AVAILABLE",
            "last_updated": "2023-01-01T12:00:00Z",
        },
        {
            "item_id": "ITEM002",
            "location": "A01-B02-C04",
            "quantity": 250,
            "unit": "EA",
            "status": "RESERVED",
            "last_updated": "2023-01-01T13:00:00Z",
        },
        {
            "item_id": "ITEM003",
            "location": "A02-B01-C01",
            "quantity": 75,
            "unit": "CS",
            "status": "AVAILABLE",
            "last_updated": "2023-01-01T14:00:00Z",
        },
    ]


@pytest.fixture
def sample_shipment_data() -> dict[str, Any]:
    """Sample shipment data for testing."""
    return {
        "shipment_id": "SHIP001",
        "order_id": "ORD001",
        "customer_id": "CUST001",
        "status": "PLANNED",
        "priority": "HIGH",
        "planned_ship_date": "2023-01-02",
        "carrier": "UPS",
        "tracking_number": None,
        "items": [
            {
                "item_id": "ITEM001",
                "quantity": 10,
                "location": "A01-B02-C03",
            },
            {
                "item_id": "ITEM002",
                "quantity": 5,
                "location": "A01-B02-C04",
            },
        ],
    }


@pytest.fixture
def sample_receipt_data() -> dict[str, Any]:
    """Sample receipt data for testing."""
    return {
        "receipt_id": "REC001",
        "purchase_order": "PO001",
        "vendor_id": "VEND001",
        "receipt_date": "2023-01-01",
        "status": "RECEIVED",
        "items": [
            {
                "item_id": "ITEM004",
                "quantity": 500,
                "unit": "EA",
                "location": "RECEIVING",
                "lot_number": "LOT001",
                "expiry_date": "2024-01-01",
            },
        ],
    }


# WMS query fixtures
@pytest.fixture
def wms_queries() -> dict[str, str]:
    """WMS SQL queries for testing."""
    return {
        "inventory_by_item": """
            SELECT item_id, location, quantity, status, last_updated
            FROM wms_inventory
            WHERE item_id = :item_id
            ORDER BY location
        """,
        "inventory_by_location": """
            SELECT item_id, quantity, status, last_updated
            FROM wms_inventory
            WHERE location = :location
            ORDER BY item_id
        """,
        "shipments_by_status": """
            SELECT shipment_id, order_id, customer_id, status, planned_ship_date
            FROM wms_shipments
            WHERE status = :status
            ORDER BY planned_ship_date
        """,
        "receipts_by_date": """
            SELECT receipt_id, purchase_order, vendor_id, receipt_date, status
            FROM wms_receipts
            WHERE receipt_date >= :start_date
            AND receipt_date <= :end_date
            ORDER BY receipt_date DESC
        """,
        "allocation_summary": """
            SELECT item_id, SUM(quantity) as total_allocated
            FROM wms_allocations
            WHERE status = 'ACTIVE'
            GROUP BY item_id
            ORDER BY total_allocated DESC
        """,
    }


# WMS operation fixtures
@pytest.fixture
def allocation_request() -> dict[str, Any]:
    """Allocation request for testing."""
    return {
        "order_id": "ORD002",
        "customer_id": "CUST002",
        "priority": "NORMAL",
        "items": [
            {
                "item_id": "ITEM001",
                "quantity": 50,
                "allocation_rule": "FIFO",
            },
            {
                "item_id": "ITEM002",
                "quantity": 25,
                "allocation_rule": "FEFO",
            },
        ],
    }


@pytest.fixture
def picking_list_data() -> dict[str, Any]:
    """Picking list data for testing."""
    return {
        "pick_list_id": "PICK001",
        "shipment_id": "SHIP001",
        "picker_id": "USER001",
        "status": "ASSIGNED",
        "priority": "HIGH",
        "estimated_time": 30,
        "tasks": [
            {
                "task_id": "TASK001",
                "item_id": "ITEM001",
                "location": "A01-B02-C03",
                "quantity": 10,
                "sequence": 1,
            },
            {
                "task_id": "TASK002",
                "item_id": "ITEM002",
                "location": "A01-B02-C04",
                "quantity": 5,
                "sequence": 2,
            },
        ],
    }


# Integration test fixtures
@pytest.fixture
def integration_test_config() -> dict[str, Any]:
    """Integration test configuration."""
    return {
        "test_database": "WMS_TEST",
        "test_schema": "TEST_SCHEMA",
        "cleanup_after_test": True,
        "timeout": 60,
        "parallel_connections": 3,
    }


@pytest.fixture
def performance_test_config() -> dict[str, Any]:
    """Performance test configuration."""
    return {
        "concurrent_operations": 10,
        "test_duration": 30,
        "operations_per_second": 5,
        "memory_threshold": "512MB",
        "response_time_threshold": 2.0,
    }


# Error simulation fixtures
@pytest.fixture
def error_scenarios() -> list[dict[str, Any]]:
    """Error scenarios for testing."""
    return [
        {
            "name": "connection_timeout",
            "error_type": "ConnectionTimeoutError",
            "simulation": "network_delay",
            "expected_behavior": "retry_with_backoff",
        },
        {
            "name": "insufficient_inventory",
            "error_type": "InsufficientInventoryError",
            "simulation": "allocation_failure",
            "expected_behavior": "partial_allocation",
        },
        {
            "name": "invalid_location",
            "error_type": "LocationNotFoundError",
            "simulation": "location_mismatch",
            "expected_behavior": "error_response",
        },
        {
            "name": "database_deadlock",
            "error_type": "DatabaseDeadlockError",
            "simulation": "concurrent_updates",
            "expected_behavior": "retry_operation",
        },
    ]


# Data validation fixtures
@pytest.fixture
def validation_rules() -> dict[str, Any]:
    """Data validation rules for testing."""
    return {
        "item_id": {
            "required": True,
            "format": "alphanumeric",
            "max_length": 20,
        },
        "location": {
            "required": True,
            "format": "A##-B##-C##",
            "max_length": 15,
        },
        "quantity": {
            "required": True,
            "type": "decimal",
            "min_value": 0,
            "max_value": 999999.99,
        },
        "unit": {
            "required": True,
            "allowed_values": ["EA", "CS", "PL", "LB", "KG"],
        },
    }


# Pytest markers for test categorization
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "wms: WMS-specific tests")
    config.addinivalue_line("markers", "oracle: Oracle database tests")
    config.addinivalue_line("markers", "api: API integration tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow tests")


# Mock services
@pytest.fixture
def mock_wms_service() -> object:
    """Mock WMS service for testing."""

    class MockWMSService:
        def __init__(self) -> None:
            self.inventory: dict[str, dict[str, Any]] = {}
            self.shipments: dict[str, dict[str, Any]] = {}
            self.allocations: dict[str, dict[str, Any]] = {}

        async def get_inventory(self, item_id: str) -> dict[str, Any]:
            return self.inventory.get(
                item_id,
                {
                    "item_id": item_id,
                    "total_quantity": 0,
                    "available_quantity": 0,
                    "locations": [],
                },
            )

        async def allocate_inventory(
            self,
            order_id: str,
            items: list[dict[str, Any]],
        ) -> dict[str, Any]:
            allocation_id = f"ALLOC_{len(self.allocations) + 1:03d}"

            allocation = {
                "allocation_id": allocation_id,
                "order_id": order_id,
                "status": "ALLOCATED",
                "items": items,
                "allocated_at": "2023-01-01T12:00:00Z",
            }

            self.allocations[allocation_id] = allocation
            return allocation

        async def create_shipment(
            self,
            shipment_data: dict[str, Any],
        ) -> dict[str, Any]:
            shipment_id = f"SHIP_{len(self.shipments) + 1:03d}"
            shipment = {
                **shipment_data,
                "shipment_id": shipment_id,
                "created_at": "2023-01-01T12:00:00Z",
            }
            self.shipments[shipment_id] = shipment
            return shipment

        async def update_inventory(
            self,
            item_id: str,
            location: str,
            quantity_change: float,
        ) -> dict[str, Any]:
            key = f"{item_id}_{location}"
            current = self.inventory.get(
                key,
                {
                    "item_id": item_id,
                    "location": location,
                    "quantity": 0,
                },
            )

            current["quantity"] += quantity_change
            current["last_updated"] = "2023-01-01T12:00:00Z"
            self.inventory[key] = current

            return current

    return MockWMSService()


@pytest.fixture
def mock_oracle_wms_adapter() -> object:
    """Mock Oracle WMS adapter for testing."""

    class MockOracleWMSAdapter:
        def __init__(self) -> None:
            self.connected = False
            self.queries_executed: list[dict[str, Any]] = []

        async def connect(self) -> bool:
            self.connected = True
            return True

        async def disconnect(self) -> bool:
            self.connected = False
            return True

        async def execute_query(
            self,
            query: str,
            parameters: dict[str, Any] | None = None,
        ) -> list[dict[str, Any]]:
            self.queries_executed.append(
                {
                    "query": query,
                    "parameters": parameters,
                    "timestamp": "2023-01-01T12:00:00Z",
                },
            )

            # Return mock data based on query type
            if "inventory" in query.lower():
                return [
                    {
                        "item_id": "ITEM001",
                        "location": "A01-B02-C03",
                        "quantity": 100,
                        "status": "AVAILABLE",
                    },
                ]
            if "shipment" in query.lower():
                return [
                    {
                        "shipment_id": "SHIP001",
                        "status": "PLANNED",
                        "order_id": "ORD001",
                    },
                ]
            return []

        async def execute_procedure(
            self,
            procedure_name: str,
            parameters: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            return {
                "procedure": procedure_name,
                "parameters": parameters,
                "result": "success",
                "execution_time": 0.5,
            }

    return MockOracleWMSAdapter()
