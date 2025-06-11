"""
Formatting utilities for the API client.

This module provides functions for formatting API response data in various formats,
including JSON, tables, CSV, and text.
"""

import csv
import io
import json
from collections.abc import Callable
from typing import Any, TextIO

from rich.console import Console
from rich.table import Table as RichTable


def format_json(
    data: dict[str, Any] | list[dict[str, Any]],
    indent: int = 2,
    sort_keys: bool = False,
    output_file: str | TextIO | None = None,
) -> str:
    """
    Format data as JSON.

    Args:
        data: Data to format
        indent: Indentation level (default: 2)
        sort_keys: Whether to sort keys (default: False)
        output_file: Output file path or file object (optional)

    Returns:
        str: Formatted JSON string
    """
    # Format as JSON
    json_str = json.dumps(data, indent=indent, sort_keys=sort_keys)

    # Write to file if requested
    if output_file is not None:
        if isinstance(output_file, str):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_str)
        else:
            output_file.write(json_str)

    return json_str


def format_table(
    data: list[dict[str, Any]],
    fields: list[str] | None = None,
    headers: dict[str, str] | None = None,
    title: str | None = None,
    console: Console | None = None,
    output_file: str | TextIO | None = None,
) -> str:
    """
    Format data as a table.

    Args:
        data: Data to format
        fields: Fields to include (optional)
        headers: Field header mapping (optional)
        title: Table title (optional)
        console: Rich console instance (optional)
        output_file: Output file path or file object (optional)

    Returns:
        str: Formatted table string
    """
    # Create console if not provided
    if console is None:
        console = Console(record=True)

    # Determine fields if not provided
    if fields is None and data:
        fields = list(data[0].keys())

    # Create header mapping if not provided
    if headers is None:
        headers = {field: field.replace("_", " ").title() for field in fields}

    # Create table
    table = RichTable(title=title)

    # Add columns
    for field in fields:
        header = headers.get(field, field)
        table.add_column(header)

    # Add rows
    for item in data:
        row = [str(item.get(field, "")) for field in fields]
        table.add_row(*row)

    # Output table
    console.print(table)

    # Get string representation
    table_str = console.export_text()

    # Write to file if requested
    if output_file is not None:
        if isinstance(output_file, str):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(table_str)
        else:
            output_file.write(table_str)

    return table_str


def format_csv(
    data: list[dict[str, Any]],
    fields: list[str] | None = None,
    headers: dict[str, str] | None = None,
    delimiter: str = ",",
    output_file: str | TextIO | None = None,
) -> str:
    """
    Format data as CSV.

    Args:
        data: Data to format
        fields: Fields to include (optional)
        headers: Field header mapping (optional)
        delimiter: CSV delimiter (default: ",")
        output_file: Output file path or file object (optional)

    Returns:
        str: Formatted CSV string
    """
    # Determine fields if not provided
    if fields is None and data:
        fields = list(data[0].keys())

    # Create header mapping if not provided
    if headers is None:
        headers = {field: field.replace("_", " ").title() for field in fields}

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output, delimiter=delimiter)

    # Write header row
    header_row = [headers.get(field, field) for field in fields]
    writer.writerow(header_row)

    # Write data rows
    for item in data:
        row = [item.get(field, "") for field in fields]
        writer.writerow(row)

    # Get string representation
    csv_str = output.getvalue()

    # Write to file if requested
    if output_file is not None:
        if isinstance(output_file, str):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(csv_str)
        else:
            output_file.write(csv_str)

    return csv_str


def format_text(
    data: list[dict[str, Any]],
    template: str,
    field_func: Callable[[str, Any], Any] | None = None,
    output_file: str | TextIO | None = None,
) -> str:
    """
    Format data using a text template.

    Args:
        data: Data to format
        template: Format template with field placeholders
        field_func: Function to transform field values (optional)
        output_file: Output file path or file object (optional)

    Returns:
        str: Formatted text string
    """
    # Default field transformation function
    if field_func is None:

        def field_func(name, value):
            return value

    # Format each item
    lines = []
    for item in data:
        # Create context with transformed field values
        context = {name: field_func(name, value) for name, value in item.items()}

        # Format template with context
        try:
            line = template.format(**context)
            lines.append(line)
        except KeyError:
            # Skip items that don't have all template fields
            pass

    # Join lines
    text = "\n".join(lines)

    # Write to file if requested
    if output_file is not None:
        if isinstance(output_file, str):
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            output_file.write(text)

    return text
