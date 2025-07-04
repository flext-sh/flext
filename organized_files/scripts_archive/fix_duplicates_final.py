#!/usr/bin/env python3
"""Fix duplicate keys in pyproject.toml files."""

import glob
import re
from pathlib import Path


def clean_toml_duplicates(file_path):
    """Remove duplicate configurations in TOML files."""
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Track seen configurations to remove duplicates
    lines = content.split("\n")
    cleaned_lines = []

    # Configuration tracking
    mypy_configs = set()
    seen_sections = set()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Handle mypy duplicates
        if line in {"warn_unused_ignores = true", "warn_return_any = true", "warn_unreachable = true"} and line in mypy_configs:
            # Skip duplicate mypy config
            i += 1
            continue
        if line in {"warn_unused_ignores = true", "warn_return_any = true", "warn_unreachable = true"}:
            mypy_configs.add(line)

        # Handle duplicate tool sections
        if line.startswith("[tool."):
            section_name = line
            if section_name in seen_sections:
                # Skip entire duplicate section
                i += 1
                while i < len(lines) and not lines[i].startswith("["):
                    i += 1
                continue
            seen_sections.add(section_name)

        cleaned_lines.append(lines[i])
        i += 1

    # Remove empty lines at the end
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_lines) + "\n")


def main():
    # Core FLEXT modules
    modules = [
        "flext-core", "flext-api", "flext-auth", "flext-grpc",
        "flext-web", "flext-cli", "flext-meltano", "flext-observability", "flext-plugin"
    ]

    for module in modules:
        toml_file = f"{module}/pyproject.toml"
        if Path(toml_file).exists():
            print(f"Cleaning {toml_file}...")
            clean_toml_duplicates(toml_file)

    print("✅ Duplicate cleanup completed!")


if __name__ == "__main__":
    main()
