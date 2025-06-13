"""Tests for the module.py module."""

import pytest
from src.module import example_function, process_items


def test_example_function() -> None:
    """Test the example_function with default parameters."""
    result = example_function("test")
    assert result["param1"] == "test"
    assert result["param2"] is None
    assert result["param3"] is False
    assert result["result"] == "Processed: test"


def test_example_function_with_params() -> None:
    """Test the example_function with custom parameters."""
    result = example_function("test", 42, True)
    assert result["param1"] == "test"
    assert result["param2"] == 42
    assert result["param3"] is True
    assert result["result"] == "Processed: test"


def test_example_function_raises_error() -> None:
    """Test that example_function raises ValueError for empty param1."""
    with pytest.raises(ValueError):
        example_function("")


def test_process_items() -> None:
    """Test the process_items function."""
    items = ["apple", 42, "banana"]
    result = process_items(items)
    assert result == ["Item: apple", "Item: 42", "Item: banana"]
    assert len(result) == len(items)
