"""
Sample module with example function.

This module provides a simple example function.
"""

from typing import Any


def example_function(
    param1: str,
    param2: int | None = None,
    param3: bool = False,
) -> dict[str, Any]:
    """
    An example function to demonstrate function signature and docstring.

    Args:
        param1: A string parameter.
        param2: Optional integer parameter.
        param3: Boolean parameter.

    Returns:
        A dictionary containing the parameters and result.

    Raises:
        ValueError: If param1 is empty.
    """
    if not param1:
        raise ValueError("param1 cannot be empty")

    return {
        "param1": param1,
        "param2": param2,
        "param3": param3,
        "result": f"Processed: {param1}",
    }


def process_items(items: list[str | int]) -> list[str]:
    """
    Process a list of items and convert them to strings.

    Args:
        items: A list of strings or integers.

    Returns:
        A list of processed strings.
    """
    return [f"Item: {item}" for item in items]
