#!/usr/bin/env python3
"""Deep analysis of mypy errors to understand patterns and fix systematically."""

import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def get_detailed_mypy_errors() -> list[dict[str, Any]]:
    """Run mypy and parse errors with full details."""
    cmd = [".venv/bin/python", "-m", "mypy", "flx/src/", "--show-error-codes", "--no-error-summary"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    errors = []
    for line in result.stdout.splitlines() + result.stderr.splitlines():
        if " error: " in line and "[" in line:
            match = re.match(r'(.+?):(\d+): error: (.+?) \[(.+?)\]', line)
            if match:
                errors.append({
                    'file': match.group(1),
                    'line': int(match.group(2)),
                    'message': match.group(3),
                    'code': match.group(4),
                })
    return errors


def analyze_call_arg_errors(errors: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Analyze call-arg errors to find patterns."""
    patterns = defaultdict(list)

    for error in errors:
        if error['code'] != 'call-arg':
            continue

        msg = error['message']

        # Missing named argument
        if "Missing named argument" in msg:
            match = re.search(r'Missing named argument "(.+?)" for "(.+?)"', msg)
            if match:
                arg_name = match.group(1)
                class_name = match.group(2)
                patterns['missing_args'].append(f"{class_name}.{arg_name}")

        # Too many arguments
        elif "Too many arguments" in msg:
            patterns['too_many_args'].append(f"{error['file']}:{error['line']}")

        # Unexpected keyword argument
        elif "Unexpected keyword argument" in msg:
            match = re.search(r'Unexpected keyword argument "(.+?)"', msg)
            if match:
                patterns['unexpected_kwargs'].append(match.group(1))

    return dict(patterns)


def analyze_attr_defined_errors(errors: list[dict[str, Any]]) -> dict[str, int]:
    """Analyze remaining attr-defined errors."""
    attr_patterns = defaultdict(int)

    for error in errors:
        if error['code'] != 'attr-defined':
            continue

        msg = error['message']

        # Extract the problematic attribute
        match = re.search(r'has no attribute "(.+?)"', msg)
        if match:
            attr_name = match.group(1)
            attr_patterns[attr_name] += 1

    return dict(attr_patterns)


def analyze_name_defined_errors(errors: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Analyze name-defined errors to find missing imports/definitions."""
    missing_names = defaultdict(list)

    for error in errors:
        if error['code'] != 'name-defined':
            continue

        msg = error['message']
        match = re.search(r'Name "(.+?)" is not defined', msg)
        if match:
            name = match.group(1)
            missing_names[name].append(f"{error['file']}:{error['line']}")

    return dict(missing_names)


def find_class_definitions() -> dict[str, str]:
    """Find where classes are defined in the codebase."""
    class_locations = {}

    for py_file in Path("flx/src").rglob("*.py"):
        try:
            content = py_file.read_text()
            # Find class definitions
            for match in re.finditer(r'^class\s+(\w+)', content, re.MULTILINE):
                class_name = match.group(1)
                class_locations[class_name] = str(py_file)
        except Exception:
            pass

    return class_locations


def generate_fix_suggestions(errors: list[dict[str, Any]]) -> None:
    """Generate specific fix suggestions based on error analysis."""

    # Get class locations
    class_locations = find_class_definitions()

    # Analyze errors
    call_arg_patterns = analyze_call_arg_errors(errors)
    attr_patterns = analyze_attr_defined_errors(errors)
    name_patterns = analyze_name_defined_errors(errors)

    print("\n=== CALL-ARG ERROR ANALYSIS ===")

    if 'missing_args' in call_arg_patterns:
        # Group by class
        missing_by_class = defaultdict(list)
        for item in call_arg_patterns['missing_args']:
            class_name, arg_name = item.split('.')
            missing_by_class[class_name].append(arg_name)

        print("\nClasses with missing constructor arguments:")
        for class_name, args in sorted(missing_by_class.items()):
            print(f"\n  {class_name}:")
            print(f"    Missing args: {', '.join(sorted(set(args)))}")
            if class_name in class_locations:
                print(f"    Defined in: {class_locations[class_name]}")

    print("\n=== ATTR-DEFINED ERROR ANALYSIS ===")
    print("\nMost common missing attributes:")
    for attr, count in sorted(attr_patterns.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {attr}: {count} occurrences")

    print("\n=== NAME-DEFINED ERROR ANALYSIS ===")
    print("\nMost common undefined names:")
    for name, locations in sorted(name_patterns.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
        print(f"\n  {name}: {len(locations)} occurrences")
        if name in class_locations:
            print(f"    Available in: {class_locations[name]}")
        # Show first few locations
        for loc in locations[:3]:
            print(f"    - {loc}")


def main():
    """Main analysis function."""
    print("Performing deep analysis of mypy errors...")

    errors = get_detailed_mypy_errors()
    print(f"\nTotal errors: {len(errors)}")

    # Group by error type
    by_type = defaultdict(list)
    for error in errors:
        by_type[error['code']].append(error)

    print("\nError distribution:")
    for code, errs in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {code}: {len(errs)}")

    # Generate detailed analysis and suggestions
    generate_fix_suggestions(errors)

    # Sample specific errors
    print("\n=== SAMPLE ERRORS ===")

    # Show some call-arg errors
    print("\nSample call-arg errors:")
    for err in by_type.get('call-arg', [])[:5]:
        print(f"  {err['file']}:{err['line']}")
        print(f"    {err['message']}")


if __name__ == "__main__":
    main()
