# 🧪 FLX Meltano Enterprise - Test Suite

> **Module**: Comprehensive test suite for FLX Meltano Enterprise platform with data pipeline testing and Singer SDK validation | **Audience**: Data Engineers, QA Engineers, Pipeline Testing Specialists | **Status**: Production Ready

## 📋 **Overview**

Enterprise-grade test suite for the FLX Meltano Enterprise platform, providing comprehensive testing coverage including unit tests, integration tests with real data pipelines, performance testing, and Singer SDK compliance validation. This test suite demonstrates best practices for testing enterprise data platforms and ETL/ELT operations.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [FLX Meltano Enterprise](../README.md) → **📂 Current**: Test Suite

---

## 🎯 **Module Purpose**

This test module provides comprehensive validation for the FLX Meltano Enterprise platform, ensuring reliability, performance, and correctness of all data pipeline operations, Singer SDK integrations, and enterprise data processing workflows in production environments.

### **Key Testing Areas**

- **Unit Testing** - Core platform logic and component validation
- **Integration Testing** - End-to-end data pipeline testing
- **Performance Testing** - Data throughput and processing performance
- **Singer SDK Testing** - Tap and target compliance validation
- **Monitoring Testing** - Observability and alerting validation
- **Security Testing** - Data security and access control validation

---

## 📁 **Test Structure**

```
tests/
├── unit/
│   ├── test_meltano_wrapper.py       # Meltano wrapper core logic tests
│   ├── test_engine_core.py           # Engine core functionality tests
│   ├── test_event_bus.py             # Event bus and messaging tests
│   ├── test_grpc_server.py           # gRPC server implementation tests
│   └── test_monitoring_systems.py    # Monitoring and metrics tests
├── integration/
│   ├── test_pipeline_execution.py    # Complete pipeline execution tests
│   ├── test_singer_sdk_integration.py # Singer SDK integration tests
│   ├── test_data_flow_validation.py  # Data flow and transformation tests
│   ├── test_external_services.py     # External service integration tests
│   └── test_api_endpoints.py         # API endpoint integration tests
├── performance/
│   ├── test_data_throughput.py       # Data processing throughput tests
│   ├── test_concurrent_pipelines.py  # Concurrent pipeline execution tests
│   ├── test_memory_optimization.py   # Memory usage optimization tests
│   └── test_scalability_limits.py    # Platform scalability testing
├── singer/
│   ├── test_tap_compliance.py        # Singer tap compliance validation
│   ├── test_target_compliance.py     # Singer target compliance validation
│   ├── test_catalog_discovery.py     # Catalog discovery functionality
│   └── test_state_management.py      # State management validation
├── monitoring/
│   ├── test_health_checks.py         # Platform health monitoring tests
│   ├── test_metrics_collection.py    # Metrics collection validation
│   ├── test_alerting_system.py       # Alerting system functionality
│   └── test_tracing_integration.py   # Distributed tracing tests
├── security/
│   ├── test_authentication.py        # Authentication system tests
│   ├── test_authorization.py         # Authorization and RBAC tests
│   ├── test_data_encryption.py       # Data encryption validation
│   └── test_audit_logging.py         # Audit logging verification
├── fixtures/
│   ├── pipeline_fixtures.py          # Pipeline test data fixtures
│   ├── singer_fixtures.py            # Singer SDK test fixtures
│   └── monitoring_fixtures.py        # Monitoring test data fixtures
├── conftest.py                       # Pytest configuration and fixtures
├── pytest.ini                        # Pytest configuration settings
└── meltano_test_config.yaml          # Meltano test environment configuration
```

---

## 🔧 **Test Categories**

### **1. Unit Tests (unit/)**

#### **Meltano Wrapper Testing (test_meltano_wrapper.py)**

```python
"""Unit tests for Meltano wrapper core functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import tempfile

from flx_meltano_enterprise.engine.meltano_wrapper import MeltanoWrapper
from flx_meltano_enterprise.exceptions import (
    MeltanoExecutionError,
    PipelineConfigurationError,
    ExtractorNotFoundError
)

class TestMeltanoWrapper:
    """Test Meltano wrapper core functionality."""

    @pytest.fixture
    def meltano_config(self):
        """Meltano configuration for testing."""
        return {
            "project_root": "/tmp/meltano_test",
            "environment": "test",
            "state_backend": "filesystem",
            "logging_level": "DEBUG"
        }

    @pytest.fixture
    def meltano_wrapper(self, meltano_config):
        """Meltano wrapper instance with test configuration."""
        return MeltanoWrapper(meltano_config)

    def test_wrapper_initialization_with_valid_config(self, meltano_config):
        """Test wrapper initialization with valid configuration."""
        # Act
        wrapper = MeltanoWrapper(meltano_config)

        # Assert
        assert wrapper.project_root == Path("/tmp/meltano_test")
        assert wrapper.environment == "test"
        assert wrapper.state_backend == "filesystem"
        assert wrapper.logging_level == "DEBUG"

    def test_wrapper_initialization_with_invalid_config(self):
        """Test wrapper initialization fails with invalid configuration."""
        # Act & Assert
        with pytest.raises(PipelineConfigurationError):
            MeltanoWrapper({
                "project_root": "",  # Invalid empty project root
                "environment": "test"
            })

    @pytest.mark.asyncio
    async def test_discover_extractors(self, meltano_wrapper):
        """Test extractor discovery functionality."""
        # Arrange
        with patch.object(meltano_wrapper, '_execute_meltano_command') as mock_exec:
            mock_exec.return_value = {
                "extractors": [
                    {"name": "tap-postgres", "namespace": "tap_postgres"},
                    {"name": "tap-mysql", "namespace": "tap_mysql"},
                    {"name": "tap-oracle-wms", "namespace": "tap_oracle_wms"}
                ]
            }

            # Act
            extractors = await meltano_wrapper.discover_extractors()

            # Assert
            assert len(extractors) == 3
            assert any(e["name"] == "tap-oracle-wms" for e in extractors)
            mock_exec.assert_called_once_with(["discover", "extractors"])

    @pytest.mark.asyncio
    async def test_discover_loaders(self, meltano_wrapper):
        """Test loader discovery functionality."""
        # Arrange
        with patch.object(meltano_wrapper, '_execute_meltano_command') as mock_exec:
            mock_exec.return_value = {
                "loaders": [
                    {"name": "target-postgres", "namespace": "target_postgres"},
                    {"name": "target-oracle-oic", "namespace": "target_oracle_oic"},
                    {"name": "target-jsonl", "namespace": "target_jsonl"}
                ]
            }

            # Act
            loaders = await meltano_wrapper.discover_loaders()

            # Assert
            assert len(loaders) == 3
            assert any(l["name"] == "target-oracle-oic" for l in loaders)
            mock_exec.assert_called_once_with(["discover", "loaders"])

    @pytest.mark.asyncio
    async def test_run_pipeline_success(self, meltano_wrapper):
        """Test successful pipeline execution."""
        # Arrange
        pipeline_config = {
            "extractor": "tap-oracle-wms",
            "loader": "target-postgres",
            "select": ["items.*", "orders.*"],
            "state": {}
        }

        with patch.object(meltano_wrapper, '_execute_meltano_command') as mock_exec:
            mock_exec.return_value = {
                "status": "success",
                "records_extracted": 1500,
                "records_loaded": 1500,
                "execution_time": 45.2,
                "state": {"bookmarks": {"items": {"updated_at": "2025-06-19T10:00:00Z"}}}
            }

            # Act
            result = await meltano_wrapper.run_pipeline(pipeline_config)

            # Assert
            assert result["status"] == "success"
            assert result["records_extracted"] == 1500
            assert result["records_loaded"] == 1500
            assert "state" in result

            expected_cmd = [
                "run", "tap-oracle-wms", "target-postgres",
                "--select", "items.*,orders.*"
            ]
            mock_exec.assert_called_once_with(expected_cmd, pipeline_config.get("state"))

    @pytest.mark.asyncio
    async def test_run_pipeline_extractor_not_found(self, meltano_wrapper):
        """Test pipeline execution with non-existent extractor."""
        # Arrange
        pipeline_config = {
            "extractor": "tap-nonexistent",
            "loader": "target-postgres"
        }

        with patch.object(meltano_wrapper, '_execute_meltano_command') as mock_exec:
            mock_exec.side_effect = ExtractorNotFoundError("Extractor 'tap-nonexistent' not found")

            # Act & Assert
            with pytest.raises(ExtractorNotFoundError):
                await meltano_wrapper.run_pipeline(pipeline_config)

    @pytest.mark.asyncio
    async def test_test_extractor_connection(self, meltano_wrapper):
        """Test extractor connection testing."""
        # Arrange
        extractor_config = {
            "name": "tap-oracle-wms",
            "settings": {
                "wms_base_url": "https://wms.company.com",
                "username": "test_user",
                "password": "test_password"
            }
        }

        with patch.object(meltano_wrapper, '_execute_meltano_command') as mock_exec:
            mock_exec.return_value = {
                "connection_status": "success",
                "message": "Connection established successfully",
                "server_version": "22.1.0",
                "available_streams": 15
            }

            # Act
            result = await meltano_wrapper.test_extractor_connection(extractor_config)

            # Assert
            assert result["connection_status"] == "success"
            assert result["available_streams"] == 15

            expected_cmd = ["test", "tap-oracle-wms"]
            mock_exec.assert_called_once_with(expected_cmd, extractor_config["settings"])

    @pytest.mark.asyncio
    async def test_get_pipeline_state(self, meltano_wrapper):
        """Test pipeline state retrieval."""
        # Arrange
        pipeline_id = "tap-oracle-wms-to-target-postgres"

        with patch.object(meltano_wrapper, '_read_state_file') as mock_read_state:
            mock_read_state.return_value = {
                "bookmarks": {
                    "items": {
                        "updated_at": "2025-06-19T09:00:00Z",
                        "version": 1
                    },
                    "orders": {
                        "updated_at": "2025-06-19T08:30:00Z",
                        "version": 1
                    }
                }
            }

            # Act
            state = await meltano_wrapper.get_pipeline_state(pipeline_id)

            # Assert
            assert "bookmarks" in state
            assert "items" in state["bookmarks"]
            assert "orders" in state["bookmarks"]
            assert state["bookmarks"]["items"]["updated_at"] == "2025-06-19T09:00:00Z"

class TestMeltanoCommandExecution:
    """Test Meltano command execution functionality."""

    @pytest.fixture
    def meltano_wrapper(self):
        """Meltano wrapper for command execution testing."""
        config = {
            "project_root": "/tmp/meltano_test",
            "environment": "test"
        }
        return MeltanoWrapper(config)

    @pytest.mark.asyncio
    async def test_execute_meltano_command_success(self, meltano_wrapper):
        """Test successful Meltano command execution."""
        # Arrange
        command = ["discover", "extractors"]

        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stdout = '{"extractors": [{"name": "tap-postgres"}]}'
            mock_subprocess.return_value.stderr = ""

            # Act
            result = await meltano_wrapper._execute_meltano_command(command)

            # Assert
            assert "extractors" in result
            assert len(result["extractors"]) == 1
            assert result["extractors"][0]["name"] == "tap-postgres"

    @pytest.mark.asyncio
    async def test_execute_meltano_command_failure(self, meltano_wrapper):
        """Test Meltano command execution failure handling."""
        # Arrange
        command = ["run", "invalid-tap", "invalid-target"]

        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.returncode = 1
            mock_subprocess.return_value.stdout = ""
            mock_subprocess.return_value.stderr = "Error: Extractor 'invalid-tap' not found"

            # Act & Assert
            with pytest.raises(MeltanoExecutionError) as exc_info:
                await meltano_wrapper._execute_meltano_command(command)

            assert "invalid-tap" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_command_with_timeout(self, meltano_wrapper):
        """Test command execution with timeout handling."""
        # Arrange
        command = ["run", "tap-slow", "target-slow"]

        with patch('subprocess.run') as mock_subprocess:
            import subprocess
            mock_subprocess.side_effect = subprocess.TimeoutExpired(command, timeout=30)

            # Act & Assert
            with pytest.raises(MeltanoExecutionError) as exc_info:
                await meltano_wrapper._execute_meltano_command(command, timeout=30)

            assert "timeout" in str(exc_info.value).lower()
```

#### **Event Bus Testing (test_event_bus.py)**

```python
"""Unit tests for event bus functionality."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from flx_meltano_enterprise.events.event_bus import EventBus
from flx_meltano_enterprise.events import (
    PipelineStartedEvent,
    PipelineCompletedEvent,
    PipelineFailedEvent,
    DataExtractionEvent,
    DataLoadingEvent
)

class TestEventBus:
    """Test event bus core functionality."""

    @pytest.fixture
    def event_bus(self):
        """Event bus instance for testing."""
        return EventBus()

    @pytest.fixture
    def mock_handler(self):
        """Mock event handler for testing."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_subscribe_and_publish_event(self, event_bus, mock_handler):
        """Test event subscription and publishing."""
        # Arrange
        event_bus.subscribe(PipelineStartedEvent, mock_handler)

        event = PipelineStartedEvent(
            pipeline_id="test-pipeline-001",
            extractor="tap-postgres",
            loader="target-jsonl",
            started_at="2025-06-19T10:00:00Z"
        )

        # Act
        await event_bus.publish(event)

        # Assert
        mock_handler.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_multiple_handlers_for_same_event(self, event_bus):
        """Test multiple handlers for the same event type."""
        # Arrange
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        handler3 = AsyncMock()

        event_bus.subscribe(PipelineCompletedEvent, handler1)
        event_bus.subscribe(PipelineCompletedEvent, handler2)
        event_bus.subscribe(PipelineCompletedEvent, handler3)

        event = PipelineCompletedEvent(
            pipeline_id="test-pipeline-002",
            status="success",
            records_processed=5000,
            execution_time=120.5,
            completed_at="2025-06-19T10:02:00Z"
        )

        # Act
        await event_bus.publish(event)

        # Assert
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)
        handler3.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_handler_exception_isolation(self, event_bus):
        """Test that handler exceptions don't affect other handlers."""
        # Arrange
        failing_handler = AsyncMock(side_effect=Exception("Handler failed"))
        working_handler = AsyncMock()

        event_bus.subscribe(DataExtractionEvent, failing_handler)
        event_bus.subscribe(DataExtractionEvent, working_handler)

        event = DataExtractionEvent(
            pipeline_id="test-pipeline-003",
            extractor="tap-mysql",
            stream="users",
            records_extracted=100,
            extracted_at="2025-06-19T10:05:00Z"
        )

        # Act
        await event_bus.publish(event)

        # Assert
        failing_handler.assert_called_once_with(event)
        working_handler.assert_called_once_with(event)
        # Both handlers should be called despite the first one failing

    @pytest.mark.asyncio
    async def test_unsubscribe_handler(self, event_bus, mock_handler):
        """Test event handler unsubscription."""
        # Arrange
        event_bus.subscribe(PipelineFailedEvent, mock_handler)
        event_bus.unsubscribe(PipelineFailedEvent, mock_handler)

        event = PipelineFailedEvent(
            pipeline_id="test-pipeline-004",
            error="Connection timeout",
            failed_at="2025-06-19T10:10:00Z"
        )

        # Act
        await event_bus.publish(event)

        # Assert
        mock_handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_event_filtering_by_type(self, event_bus):
        """Test that events are only sent to appropriate handlers."""
        # Arrange
        pipeline_handler = AsyncMock()
        data_handler = AsyncMock()

        event_bus.subscribe(PipelineStartedEvent, pipeline_handler)
        event_bus.subscribe(DataLoadingEvent, data_handler)

        pipeline_event = PipelineStartedEvent(
            pipeline_id="test-pipeline-005",
            extractor="tap-oracle-wms",
            loader="target-postgres",
            started_at="2025-06-19T10:15:00Z"
        )

        data_event = DataLoadingEvent(
            pipeline_id="test-pipeline-005",
            loader="target-postgres",
            stream="items",
            records_loaded=250,
            loaded_at="2025-06-19T10:16:00Z"
        )

        # Act
        await event_bus.publish(pipeline_event)
        await event_bus.publish(data_event)

        # Assert
        pipeline_handler.assert_called_once_with(pipeline_event)
        data_handler.assert_called_once_with(data_event)

        # Verify cross-contamination doesn't occur
        assert pipeline_handler.call_count == 1
        assert data_handler.call_count == 1
```

### **2. Integration Tests (integration/)**

#### **Pipeline Execution Testing (test_pipeline_execution.py)**

```python
"""Integration tests for complete pipeline execution."""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path

from flx_meltano_enterprise.engine.meltano_wrapper import MeltanoWrapper
from flx_meltano_enterprise.monitoring.metrics import MetricsCollector

@pytest.mark.integration
class TestPipelineExecution:
    """Test complete pipeline execution workflows."""

    @pytest.fixture
    async def meltano_test_project(self):
        """Create temporary Meltano test project."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"

            # Initialize Meltano project
            await self._initialize_meltano_project(project_path)

            yield project_path

    @pytest.fixture
    def meltano_wrapper(self, meltano_test_project):
        """Meltano wrapper with test project."""
        config = {
            "project_root": str(meltano_test_project),
            "environment": "test",
            "state_backend": "filesystem"
        }
        return MeltanoWrapper(config)

    @pytest.mark.asyncio
    async def test_simple_postgres_to_jsonl_pipeline(self, meltano_wrapper):
        """Test simple PostgreSQL to JSONL pipeline execution."""
        # Arrange
        pipeline_config = {
            "extractor": "tap-postgres",
            "loader": "target-jsonl",
            "select": ["users.*", "orders.*"],
            "settings": {
                "tap-postgres": {
                    "host": "localhost",
                    "port": 5432,
                    "user": "test_user",
                    "password": "test_password",
                    "database": "test_db"
                },
                "target-jsonl": {
                    "destination_path": "output"
                }
            }
        }

        # Act
        result = await meltano_wrapper.run_pipeline(pipeline_config)

        # Assert
        assert result["status"] == "success"
        assert result["records_extracted"] > 0
        assert result["records_loaded"] == result["records_extracted"]
        assert "state" in result

        # Verify output files were created
        output_path = meltano_wrapper.project_root / "output"
        assert output_path.exists()
        assert len(list(output_path.glob("*.jsonl"))) > 0

    @pytest.mark.asyncio
    async def test_oracle_wms_to_postgres_pipeline(self, meltano_wrapper):
        """Test Oracle WMS to PostgreSQL pipeline execution."""
        # Arrange
        pipeline_config = {
            "extractor": "tap-oracle-wms",
            "loader": "target-postgres",
            "select": ["items.*", "locations.*", "orders.*"],
            "settings": {
                "tap-oracle-wms": {
                    "wms_base_url": "https://test-wms.oracle.com",
                    "username": "wms_user",
                    "password": "wms_password",
                    "facility_id": "TEST_FACILITY"
                },
                "target-postgres": {
                    "host": "localhost",
                    "port": 5432,
                    "user": "postgres",
                    "password": "postgres",
                    "database": "warehouse_db"
                }
            }
        }

        # Act
        result = await meltano_wrapper.run_pipeline(pipeline_config)

        # Assert
        assert result["status"] == "success"
        assert result["records_extracted"] > 0
        assert "execution_time" in result
        assert result["execution_time"] < 300  # Should complete within 5 minutes

        # Verify state management
        assert "state" in result
        assert "bookmarks" in result["state"]

    @pytest.mark.asyncio
    async def test_pipeline_with_transformation(self, meltano_wrapper):
        """Test pipeline execution with data transformation."""
        # Arrange
        pipeline_config = {
            "extractor": "tap-csv",
            "transformer": "dbt-postgres",
            "loader": "target-postgres",
            "transform": "run",
            "settings": {
                "tap-csv": {
                    "files": [
                        {
                            "entity": "customers",
                            "path": "data/customers.csv",
                            "keys": ["customer_id"]
                        }
                    ]
                },
                "dbt-postgres": {
                    "host": "localhost",
                    "port": 5432,
                    "user": "postgres",
                    "password": "postgres",
                    "database": "analytics_db"
                }
            }
        }

        # Create test CSV file
        await self._create_test_csv_file(
            meltano_wrapper.project_root / "data" / "customers.csv"
        )

        # Act
        result = await meltano_wrapper.run_pipeline(pipeline_config)

        # Assert
        assert result["status"] == "success"
        assert "transformation_status" in result
        assert result["transformation_status"] == "success"

    @pytest.mark.asyncio
    async def test_pipeline_failure_handling(self, meltano_wrapper):
        """Test pipeline execution failure handling."""
        # Arrange - Invalid configuration to trigger failure
        pipeline_config = {
            "extractor": "tap-postgres",
            "loader": "target-postgres",
            "settings": {
                "tap-postgres": {
                    "host": "invalid-host",  # Invalid host to trigger failure
                    "port": 5432,
                    "user": "test_user",
                    "password": "test_password",
                    "database": "test_db"
                }
            }
        }

        # Act
        result = await meltano_wrapper.run_pipeline(pipeline_config)

        # Assert
        assert result["status"] == "failed"
        assert "error" in result
        assert "connection" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_incremental_pipeline_execution(self, meltano_wrapper):
        """Test incremental pipeline execution with state management."""
        # Arrange
        pipeline_config = {
            "extractor": "tap-postgres",
            "loader": "target-jsonl",
            "select": ["users.*"],
            "settings": {
                "tap-postgres": {
                    "host": "localhost",
                    "port": 5432,
                    "user": "test_user",
                    "password": "test_password",
                    "database": "test_db"
                }
            }
        }

        # Act - First run (full extract)
        result1 = await meltano_wrapper.run_pipeline(pipeline_config)

        # Act - Second run (incremental)
        pipeline_config["state"] = result1["state"]
        result2 = await meltano_wrapper.run_pipeline(pipeline_config)

        # Assert
        assert result1["status"] == "success"
        assert result2["status"] == "success"

        # Second run should extract fewer records (incremental)
        assert result2["records_extracted"] <= result1["records_extracted"]

    async def _initialize_meltano_project(self, project_path: Path) -> None:
        """Initialize Meltano test project."""
        import subprocess

        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)

        # Initialize Meltano project
        subprocess.run([
            "meltano", "init", str(project_path.name)
        ], cwd=project_path.parent, check=True)

        # Add required extractors and loaders
        extractors = ["tap-postgres", "tap-csv", "tap-oracle-wms"]
        loaders = ["target-jsonl", "target-postgres"]

        for extractor in extractors:
            subprocess.run([
                "meltano", "add", "extractor", extractor
            ], cwd=project_path, check=False)  # Some may not be available

        for loader in loaders:
            subprocess.run([
                "meltano", "add", "loader", loader
            ], cwd=project_path, check=False)  # Some may not be available

    async def _create_test_csv_file(self, file_path: Path) -> None:
        """Create test CSV file for pipeline testing."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        csv_content = """customer_id,name,email,created_at
1,John Doe,john@example.com,2025-01-01
2,Jane Smith,jane@example.com,2025-01-02
3,Bob Johnson,bob@example.com,2025-01-03
"""
        file_path.write_text(csv_content)
```

### **3. Performance Tests (performance/)**

#### **Data Throughput Testing (test_data_throughput.py)**

```python
"""Performance tests for data processing throughput."""

import pytest
import asyncio
import time
from statistics import mean, median

@pytest.mark.performance
class TestDataThroughput:
    """Test data processing throughput performance."""

    @pytest.mark.asyncio
    async def test_high_volume_data_processing(self, meltano_wrapper):
        """Test high-volume data processing performance."""
        # Arrange
        pipeline_config = {
            "extractor": "tap-csv",
            "loader": "target-jsonl",
            "settings": {
                "tap-csv": {
                    "files": [
                        {
                            "entity": "large_dataset",
                            "path": "data/large_dataset.csv",
                            "keys": ["id"]
                        }
                    ]
                }
            }
        }

        # Create large test dataset (100K records)
        await self._create_large_test_dataset(
            meltano_wrapper.project_root / "data" / "large_dataset.csv",
            record_count=100000
        )

        # Act
        start_time = time.time()
        result = await meltano_wrapper.run_pipeline(pipeline_config)
        end_time = time.time()

        # Assert performance metrics
        execution_time = end_time - start_time
        records_per_second = result["records_extracted"] / execution_time

        assert result["status"] == "success"
        assert result["records_extracted"] == 100000
        assert records_per_second >= 1000  # At least 1K records per second
        assert execution_time <= 120  # Complete within 2 minutes

    @pytest.mark.asyncio
    async def test_concurrent_pipeline_performance(self, meltano_wrapper):
        """Test performance with concurrent pipeline execution."""
        # Arrange
        pipeline_configs = []
        for i in range(5):  # 5 concurrent pipelines
            config = {
                "extractor": "tap-csv",
                "loader": "target-jsonl",
                "settings": {
                    "tap-csv": {
                        "files": [
                            {
                                "entity": f"dataset_{i}",
                                "path": f"data/dataset_{i}.csv",
                                "keys": ["id"]
                            }
                        ]
                    },
                    "target-jsonl": {
                        "destination_path": f"output_{i}"
                    }
                }
            }
            pipeline_configs.append(config)

            # Create test dataset for each pipeline
            await self._create_test_dataset(
                meltano_wrapper.project_root / "data" / f"dataset_{i}.csv",
                record_count=10000
            )

        # Act
        start_time = time.time()
        tasks = [
            meltano_wrapper.run_pipeline(config)
            for config in pipeline_configs
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        # Assert
        total_time = end_time - start_time
        successful_results = [r for r in results if not isinstance(r, Exception)]

        assert len(successful_results) >= 4  # At least 80% success rate
        assert total_time <= 180  # Complete within 3 minutes

        # Check individual pipeline performance
        for result in successful_results:
            assert result["status"] == "success"
            assert result["records_extracted"] == 10000

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, meltano_wrapper):
        """Test memory usage during high-load scenarios."""
        import psutil
        import os

        # Arrange
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create very large dataset
        large_dataset_path = meltano_wrapper.project_root / "data" / "memory_test.csv"
        await self._create_large_test_dataset(large_dataset_path, record_count=500000)

        pipeline_config = {
            "extractor": "tap-csv",
            "loader": "target-jsonl",
            "settings": {
                "tap-csv": {
                    "files": [
                        {
                            "entity": "memory_test",
                            "path": "data/memory_test.csv",
                            "keys": ["id"]
                        }
                    ]
                }
            }
        }

        # Act
        result = await meltano_wrapper.run_pipeline(pipeline_config)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Assert
        assert result["status"] == "success"
        assert result["records_extracted"] == 500000
        assert memory_increase <= 500  # Memory increase should be <= 500MB

        # Verify memory is released after processing
        import gc
        gc.collect()

        cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_released = final_memory - cleanup_memory

        assert memory_released >= memory_increase * 0.7  # At least 70% memory released

    async def _create_large_test_dataset(self, file_path: Path, record_count: int) -> None:
        """Create large test dataset for performance testing."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            # Write header
            f.write("id,name,email,value,created_at\n")

            # Write records in batches to manage memory
            batch_size = 10000
            for batch_start in range(0, record_count, batch_size):
                batch_end = min(batch_start + batch_size, record_count)
                batch_lines = []

                for i in range(batch_start, batch_end):
                    line = f"{i},User {i},user{i}@example.com,{i * 10.5},2025-01-{(i % 30) + 1:02d}\n"
                    batch_lines.append(line)

                f.writelines(batch_lines)
```

---

## 🔧 **Test Configuration**

### **Pytest Configuration (conftest.py)**

```python
"""Pytest configuration for Meltano Enterprise tests."""

import pytest
import asyncio
import os
import tempfile
from pathlib import Path

from flx_meltano_enterprise.engine.meltano_wrapper import MeltanoWrapper
from flx_meltano_enterprise.monitoring.metrics import MetricsCollector

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def meltano_test_config():
    """Meltano test configuration."""
    return {
        "project_root": os.getenv("MELTANO_TEST_PROJECT", "/tmp/meltano_test"),
        "environment": "test",
        "state_backend": "filesystem",
        "logging_level": "DEBUG"
    }

@pytest.fixture
async def meltano_wrapper(meltano_test_config):
    """Meltano wrapper with test configuration."""
    wrapper = MeltanoWrapper(meltano_test_config)
    yield wrapper
    await wrapper.cleanup()

@pytest.fixture
def metrics_collector():
    """Metrics collector for monitoring tests."""
    return MetricsCollector()

@pytest.fixture
async def clean_test_environment(meltano_test_config):
    """Clean test environment before and after tests."""
    # Cleanup before test
    await _cleanup_test_environment(meltano_test_config)

    yield

    # Cleanup after test
    await _cleanup_test_environment(meltano_test_config)

async def _cleanup_test_environment(config):
    """Clean up test environment."""
    project_path = Path(config["project_root"])

    if project_path.exists():
        import shutil
        shutil.rmtree(project_path, ignore_errors=True)
```

### **Test Configuration (pytest.ini)**

```ini
[tool:pytest]
minversion = 6.0
addopts =
    -ra
    --strict-markers
    --strict-config
    --cov=flx_meltano_enterprise
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests (requires Meltano environment)
    performance: Performance tests
    singer: Singer SDK compliance tests
    monitoring: Monitoring and observability tests
    security: Security and compliance tests
    slow: Slow running tests
asyncio_mode = auto
filterwarnings =
    ignore::DeprecationWarning
    ignore::meltano.core.utils.DeprecationWarning
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete FLX Meltano Enterprise documentation
- [Source Implementation](../src/README.md) - Source code structure and patterns
- [Examples](../examples/README.md) - Usage examples and patterns

### **Testing Documentation**

- [Meltano Testing Guide](../../docs/testing/meltano-testing.md) - Meltano-specific testing strategies
- [Pipeline Testing](../../docs/testing/pipeline-testing.md) - Data pipeline testing methodologies
- [Performance Testing](../../docs/testing/performance-testing.md) - Performance testing best practices

### **External References**

- [Meltano Documentation](https://docs.meltano.com/) - Official Meltano documentation
- [Singer SDK Documentation](https://sdk.meltano.com/) - Singer SDK testing patterns
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/) - Async testing framework

---

**📂 Module**: Test Suite | **🏠 Component**: [FLX Meltano Enterprise](../README.md) | **Framework**: PyTest 7.0+ | **Updated**: 2025-06-19
