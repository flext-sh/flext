#!/usr/bin/env python3
"""Script to refactor manual domain models to use FLEXT patterns.

This script identifies and refactors manual domain model implementations
to use standardized FLEXT domain patterns from flext-core.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


def find_domain_model_files() -> dict[str, list[str]]:
    """Find files containing domain models that need refactoring.

    Returns:
        Dict of model types to file lists.

    """
    patterns: dict[str, list[str]] = {
        "entities": [],
        "value_objects": [],
        "aggregates": [],
        "events": [],
    }

    # Find entity files
    cmd = [
        "find",
        ".",
        "-name",
        "*.py",
        "-type",
        "f",
        "-path",
        "*/domain/*",
        "-exec",
        "grep",
        "-l",
        "class.*Entity\\|entities\\.py",
        "{}",
        ";",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        patterns["entities"] = [
            f.strip() for f in result.stdout.split("\n") if f.strip()
        ]

    # Find value object files
    cmd = [
        "find",
        ".",
        "-name",
        "*.py",
        "-type",
        "f",
        "-path",
        "*/domain/*",
        "-exec",
        "grep",
        "-l",
        "value_objects\\.py\\|ValueObject",
        "{}",
        ";",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        patterns["value_objects"] = [
            f.strip() for f in result.stdout.split("\n") if f.strip()
        ]

    # Find aggregate files
    cmd = [
        "find",
        ".",
        "-name",
        "*.py",
        "-type",
        "f",
        "-path",
        "*/domain/*",
        "-exec",
        "grep",
        "-l",
        "aggregates\\.py\\|AggregateRoot",
        "{}",
        ";",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        patterns["aggregates"] = [
            f.strip() for f in result.stdout.split("\n") if f.strip()
        ]

    # Find event files
    cmd = [
        "find",
        ".",
        "-name",
        "*.py",
        "-type",
        "f",
        "-path",
        "*/domain/*",
        "-exec",
        "grep",
        "-l",
        "events\\.py\\|DomainEvent",
        "{}",
        ";",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        patterns["events"] = [f.strip() for f in result.stdout.split("\n") if f.strip()]

    return patterns


def refactor_entities_file(file_path: str) -> bool:
    """Refactor entity classes to use FlextEntity.

    Args:
        file_path: Path to file containing entity classes.

    Returns:
        True if changes were made, False otherwise.

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        changes_made = False

        # Add flext-core entity import if not present
        if "FlextEntity" not in content:
            # Find good insertion point after other flext_core imports
            if "from flext_core import" in content:
                pattern = r"(from flext_core import[^\n]*)"
                match = re.search(pattern, content)
                if match:
                    content = content.replace(
                        match.group(1),
                        f"{match.group(1)}\nFlextEntity",
                    )
                    changes_made = True
            else:
                # Add after other imports
                pattern = r"(from __future__ import annotations\n\n)"
                match = re.search(pattern, content)
                if match:
                    content = content.replace(
                        match.group(1),
                        f"{match.group(1)}FlextEntity\n",
                    )
                    changes_made = True

        # Find entity classes that don't inherit from FlextEntity
        entity_pattern = r"class\s+([A-Z][a-zA-Z0-9_]*)\s*\([^)]*\):"
        matches = re.finditer(entity_pattern, content)

        for match in matches:
            class_name = match.group(1)
            full_match = match.group(0)

            # Skip if already inherits from FlextEntity
            if "FlextEntity" in full_match:
                continue

            # Skip if it's a base class or not a domain entity
            if class_name in {"BaseModel", "BaseSettings", "Config"}:
                continue

            # Check if it inherits from BaseModel
            if "BaseModel" in full_match:
                # Replace BaseModel with FlextEntity
                new_class_def = full_match.replace("BaseModel", "FlextEntity")
                content = content.replace(full_match, new_class_def)
                changes_made = True

                # Add TODO comment above the class
                class_line_start = content.find(new_class_def)
                if class_line_start > 0:
                    # Find the start of the line
                    line_start = content.rfind("\n", 0, class_line_start) + 1
                    indent = ""
                    for char in content[line_start:class_line_start]:
                        if char in {" ", "\t"}:
                            indent += char
                        else:
                            break

                    todo_comment = (
                        f"{indent}# TODO: Refactored to use FlextEntity pattern\n"
                    )
                    content = content[:line_start] + todo_comment + content[line_start:]
                    changes_made = True

        # Add manual ID generation TODO comments
        uuid_pattern = r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*.*=.*uuid4\(\)"
        matches = re.finditer(uuid_pattern, content)

        for match in matches:
            indent = match.group(1)
            match.group(2)
            full_match = match.group(0)

            replacement = f"{indent}# TODO: Remove manual ID generation - FlextEntity provides automatic ID\n{full_match}"
            content = content.replace(full_match, replacement)
            changes_made = True

        if changes_made:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Refactored entities in: {file_path}")
            return True
        print(f"⏭️ No entity changes needed: {file_path}")
        return False

    except (OSError, ValueError, TypeError) as e:
        print(f"❌ Error refactoring entities in {file_path}: {e}")
        return False


def refactor_value_objects_file(file_path: str) -> bool:
    """Refactor value object classes to use FlextValueObject.

    Args:
        file_path: Path to file containing value object classes.

    Returns:
        True if changes were made, False otherwise.

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        changes_made = False

        # Add flext-core value object import if not present
        if "FlextValueObject" not in content:
            # Find good insertion point
            if "from flext_core import" in content:
                pattern = r"(from flext_core import[^\n]*)"
                match = re.search(pattern, content)
                if match:
                    content = content.replace(
                        match.group(1),
                        f"{match.group(1)}\nFlextValueObject",
                    )
                    changes_made = True
            else:
                # Add after other imports
                pattern = r"(from __future__ import annotations\n\n)"
                match = re.search(pattern, content)
                if match:
                    content = content.replace(
                        match.group(1),
                        f"{match.group(1)}FlextValueObject\n",
                    )
                    changes_made = True

        # Find value object classes that don't inherit from FlextValueObject
        vo_pattern = r"class\s+([A-Z][a-zA-Z0-9_]*)\s*\([^)]*\):"
        matches = re.finditer(vo_pattern, content)

        for match in matches:
            class_name = match.group(1)
            full_match = match.group(0)

            # Skip if already inherits from FlextValueObject
            if "FlextValueObject" in full_match:
                continue

            # Skip if it's a base class
            if class_name in {"BaseModel", "BaseSettings"}:
                continue

            # Check if it inherits from BaseModel
            if "BaseModel" in full_match:
                # Replace BaseModel with FlextValueObject
                new_class_def = full_match.replace("BaseModel", "FlextValueObject")
                content = content.replace(full_match, new_class_def)
                changes_made = True

                # Add TODO comment above the class
                class_line_start = content.find(new_class_def)
                if class_line_start > 0:
                    line_start = content.rfind("\n", 0, class_line_start) + 1
                    indent = ""
                    for char in content[line_start:class_line_start]:
                        if char in {" ", "\t"}:
                            indent += char
                        else:
                            break

                    todo_comment = (
                        f"{indent}# TODO: Refactored to use FlextValueObject pattern\n"
                    )
                    content = content[:line_start] + todo_comment + content[line_start:]
                    changes_made = True

        # Add TODO comments for custom validation methods
        validation_pattern = r"(\s+)def\s+validate_[a-zA-Z_][a-zA-Z0-9_]*\s*\("
        matches = re.finditer(validation_pattern, content)

        for match in matches:
            indent = match.group(1)
            full_match = match.group(0)

            replacement = f"{indent}# TODO: Consider using FlextValueObject validation patterns\n{full_match}"
            content = content.replace(full_match, replacement)
            changes_made = True

        if changes_made:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Refactored value objects in: {file_path}")
            return True
        print(f"⏭️ No value object changes needed: {file_path}")
        return False

    except (OSError, ValueError, TypeError) as e:
        print(f"❌ Error refactoring value objects in {file_path}: {e}")
        return False


def analyze_domain_patterns(file_path: str) -> dict[str, int]:
    """Analyze domain patterns in a file.

    Args:
        file_path: Path to file to analyze.

    Returns:
        Dict with pattern counts.

    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        patterns = {
            "manual_entities": 0,
            "manual_value_objects": 0,
            "manual_id_generation": 0,
            "custom_validation": 0,
            "non_flext_result": 0,
        }

        # Count manual entities (classes inheriting from BaseModel but not FlextEntity)
        entity_matches = re.findall(
            r"class\s+[A-Z][a-zA-Z0-9_]*\s*\(.*BaseModel.*\):",
            content,
        )
        if entity_matches and "FlextEntity" not in content:
            patterns["manual_entities"] = len(entity_matches)

        # Count manual ID generation
        patterns["manual_id_generation"] = len(re.findall(r"uuid4\(\)", content))

        # Count custom validation methods
        patterns["custom_validation"] = len(
            re.findall(r"def\s+validate_[a-zA-Z_]", content),
        )

        # Count non-FlextResult return types in domain methods
        method_matches = re.findall(
            r"def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*->\s*([^:]+):",
            content,
        )
        for return_type in method_matches:
            if "FlextResult" not in return_type and return_type.strip() not in {
                "None",
                "bool",
                "str",
                "int",
            }:
                patterns["non_flext_result"] += 1

        return patterns

    except (OSError, ValueError, TypeError) as e:
        print(f"❌ Error analyzing patterns in {file_path}: {e}")
        return {}


def main() -> None:
    """Main function to refactor domain models."""
    print("🚀 Starting domain model refactoring...")

    # Find domain model files
    domain_files = find_domain_model_files()

    print("📄 Found domain files:")
    print(f"  - Entities: {len(domain_files['entities'])}")
    print(f"  - Value Objects: {len(domain_files['value_objects'])}")
    print(f"  - Aggregates: {len(domain_files['aggregates'])}")
    print(f"  - Events: {len(domain_files['events'])}")

    # Process high priority files first
    priority_files = [
        # flext-auth (highest priority)
        "./flext-auth/src/flext_auth/domain/entities.py",
        "./flext-auth/src/flext_auth/domain/value_objects.py",
        # flext-meltano (high priority)
        "./flext-meltano/src/flext_meltano/domain/entities.py",
        # flext-web (medium priority)
        "./flext-web/src/flext_web/domain/entities.py",
    ]

    refactored_count = 0

    # Refactor entity files
    print("\n🔧 Refactoring entity files...")
    for file_path in priority_files:
        if (
            "entities.py" in file_path
            and Path(file_path).exists()
            and refactor_entities_file(file_path)
        ):
            refactored_count += 1

    # Refactor value object files
    print("\n🔧 Refactoring value object files...")
    for file_path in priority_files:
        if (
            "value_objects.py" in file_path
            and Path(file_path).exists()
            and refactor_value_objects_file(file_path)
        ):
            refactored_count += 1

    # Analyze remaining files
    print("\n📊 Analyzing remaining domain files...")
    total_patterns = {
        "manual_entities": 0,
        "manual_value_objects": 0,
        "manual_id_generation": 0,
        "custom_validation": 0,
        "non_flext_result": 0,
    }

    analyzed_files = 0
    for file_list in domain_files.values():
        for file_path in file_list[:10]:  # Analyze first 10 files from each category
            patterns = analyze_domain_patterns(file_path)
            if patterns:
                analyzed_files += 1
                for key, count in patterns.items():
                    total_patterns[key] += count

    print(f"\n📈 Domain Pattern Analysis ({analyzed_files} files):")
    print(
        f"  - Manual entities needing refactoring: {total_patterns['manual_entities']}",
    )
    print(
        f"  - Manual ID generation instances: {total_patterns['manual_id_generation']}",
    )
    print(f"  - Custom validation methods: {total_patterns['custom_validation']}")
    print(f"  - Non-FlextResult return types: {total_patterns['non_flext_result']}")

    print("\n✅ Domain model refactoring completed!")
    print(f"📊 Successfully refactored {refactored_count} files")

    print("\n📋 Next Steps:")
    print("1. Review refactored domain model files")
    print("2. Update imports in dependent modules")
    print("3. Run tests to ensure compatibility")
    print("4. Update remaining domain files using established patterns")
    print("5. Implement FlextResult return types for domain methods")


if __name__ == "__main__":
    main()
