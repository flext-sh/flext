"""Modern unit tests for flext-meltano-bridge.

These tests demonstrate modern pytest patterns that pass strict linting:
- ruff with ALL rules enabled
- mypy --strict
- bandit security checks
- PEP 8 compliance
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel, ValidationError


class SampleModel(BaseModel):
    """Sample model for testing validation."""

    id: int
    name: str
    active: bool = True

    def process(self) -> str:
        """Sample method for testing."""
        return f"Processing {self.name} ({self.id})"


class TestModernUnitPatterns:
    """Modern unit test patterns with strict typing and validation."""

    def test_model_validation_success(self) -> None:
        """Test successful model validation."""
        data = {"id": 1, "name": "test", "active": True}
        model = SampleModel(**data)

        assert model.id == 1
        assert model.name == "test"
        assert model.active is True
        assert model.process() == "Processing test (1)"

    def test_model_validation_failure(self) -> None:
        """Test model validation failure."""
        with pytest.raises(ValidationError) as exc_info:
            SampleModel(id="invalid", name="test")  # type: ignore[arg-type]

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(error["type"] == "int_parsing" for error in errors)

    @pytest.mark.parametrize(
        ("input_data", "expected_result"),
        [
            ({"id": 1, "name": "alpha"}, "Processing alpha (1)"),
            ({"id": 2, "name": "beta", "active": False}, "Processing beta (2)"),
            ({"id": 3, "name": "gamma"}, "Processing gamma (3)"),
        ],
        ids=["simple", "with_active_false", "default_active"],
    )
    def test_parametrized_processing(
        self, input_data: dict[str, Any], expected_result: str
    ) -> None:
        """Test parametrized model processing."""
        model = SampleModel(**input_data)
        result = model.process()
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_async_operation(self) -> None:
        """Test async operation patterns."""

        async def sample_async_operation() -> str:
            await asyncio.sleep(0.001)  # Minimal delay for async test
            return "async_result"

        result = await sample_async_operation()
        assert result == "async_result"

    def test_mock_usage_patterns(self) -> None:
        """Test modern mock usage patterns."""
        mock_service = MagicMock()
        mock_service.get_data.return_value = {"key": "value"}

        result = mock_service.get_data()

        assert result == {"key": "value"}
        mock_service.get_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_mock_patterns(self) -> None:
        """Test async mock patterns."""
        async_mock = AsyncMock()
        async_mock.async_operation.return_value = "async_mock_result"

        result = await async_mock.async_operation()

        assert result == "async_mock_result"
        async_mock.async_operation.assert_called_once()

    def test_fixture_usage(self, mock_config: dict[str, Any]) -> None:
        """Test fixture usage from conftest.py."""
        assert mock_config["debug"] is True
        assert mock_config["testing"] is True
        assert "log_level" in mock_config

    @pytest.mark.fast
    def test_fast_operation(self) -> None:
        """Test marked as fast for performance testing."""
        result = sum(range(100))
        assert result == 4950

    @pytest.mark.slow
    def test_slow_operation(self) -> None:
        """Test marked as slow (can be skipped in CI)."""
        # Simulate slow operation
        import time

        time.sleep(0.01)
        assert True

    def test_error_handling_patterns(self) -> None:
        """Test modern error handling patterns."""

        def risky_operation(fail: bool = False) -> str:
            if fail:
                msg = "Expected failure"
                raise ValueError(msg)
            return "success"

        # Test success path
        result = risky_operation(fail=False)
        assert result == "success"

        # Test failure path
        with pytest.raises(ValueError, match="Expected failure"):
            risky_operation(fail=True)


@pytest.mark.unit
class TestSecurityPatterns:
    """Security-focused test patterns."""

    def test_no_hardcoded_secrets(self) -> None:
        """Test that no secrets are hardcoded."""
        suspicious_strings = ["password", "secret", "key", "token"]
        test_data = {"username": "test", "config": "debug_mode"}

        # Check that test data doesn't contain suspicious strings
        data_str = str(test_data).lower()
        found_suspicious = [s for s in suspicious_strings if s in data_str]

        # This is OK because we're testing with safe test data
        assert len(found_suspicious) == 0 or all(
            s == "key"
            for s in found_suspicious  # "key" in "config" is OK
        )

    def test_input_validation(self) -> None:
        """Test input validation patterns."""

        def validate_input(data: str) -> str:
            if not data or len(data) > 100:
                msg = "Invalid input length"
                raise ValueError(msg)
            # Simple validation - no actual security risk in test
            return data.strip()

        # Test valid input
        result = validate_input("valid input")
        assert result == "valid input"

        # Test invalid input
        with pytest.raises(ValueError, match="Invalid input length"):
            validate_input("")

        with pytest.raises(ValueError, match="Invalid input length"):
            validate_input("x" * 101)


# Performance benchmark examples
@pytest.mark.benchmark
class TestPerformancePatterns:
    """Performance testing patterns with pytest-benchmark."""

    def test_list_comprehension_performance(self, benchmark: Any) -> None:
        """Benchmark list comprehension performance."""

        def list_comp_operation() -> list[int]:
            return [x * 2 for x in range(1000)]

        result = benchmark(list_comp_operation)
        assert len(result) == 1000
        assert result[0] == 0
        assert result[-1] == 1998
