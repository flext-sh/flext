#!/usr/bin/env python3
"""Fix the remaining star separator issue in client.py.

This script specifically targets line 179 in client.py which has a syntax error
due to a star separator.

Usage:
    python fix_client_star_separator.py
"""

from pathlib import Path


def fix_client_file() -> bool:
    """Fix the star separator issue in client.py."""
    client_path = (
        Path(__file__).parent.parent /
        "dc-api-x" /
        "src" /
        "dc_api_x" /
        "client.py")

    if not client_path.exists():
        print(f"File not found: {client_path}")
        return False

    print(f"Processing {client_path}")
    content = client_path.read_text(encoding="utf-8")

    # Find the init method with the star separator issue
    init_start = content.find("def __init__(")
    if init_start == -1:
        print("Could not find __init__ method")
        return False

    # Find the problematic line with the star separator
    lines = content.split("\n")
    fixed_lines: list = []

    found_issue = False
    in_init = False
    star_found = False

    for line in lines:
        if "def __init__(" in line:
            in_init = True

        if in_init and "*," in line and "debug: bool" in line and not star_found:
            # Remove the star separator entirely since we already have one
            fixed_line = line.replace("*,", "")
            fixed_lines.append(fixed_line)
            found_issue = True
            star_found = True
            fixed_lines.append(line)

        if in_init and line.strip() == ")":
            in_init = False

    if found_issue:
        # Write fixed content back to file
        fixed_content = "\n".join(fixed_lines)
        client_path.write_text(fixed_content, encoding="utf-8")
        print(f"Fixed star separator in {client_path}")
        return True

    print("No star separator issue found")
    return False


def main() -> None:
    """Main entry point."""
    fix_client_file()


if __name__ == "__main__":
    main()
