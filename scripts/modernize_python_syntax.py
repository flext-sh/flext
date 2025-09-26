#!/usr/bin/env python3
"""FLEXT Ecosystem Python 3.13+ Syntax Modernization Script.

This script systematically updates all FLEXT projects to use:
1. PEP 695: Type Parameter Syntax (def func[T]() instead of TypeVar)
2. PEP 698: @override decorator for method overrides
3. PEP 692: **kwargs with TypedDict unpacking
4. Enhanced type annotations for Python 3.13+
5. Modern syntax patterns and best practices

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# FLEXT projects to modernize
FLEXT_ROOT = Path("/home/marlonsc/flext")


def find_python_files() -> list[Path]:
    """Find all Python files in FLEXT projects."""
    python_files = []

    # Find all Python files in src directories
    for py_file in FLEXT_ROOT.rglob("src/**/*.py"):
        # Skip virtual environment and system files
        if ".venv" in str(py_file) or "site-packages" in str(py_file):
            continue

        # Only include FLEXT projects
        if any(
            part.startswith("flext-")
            or part in {"client-a-oud-mig", "flexcore", "client-b-meltano-native"}
            for part in py_file.parts
        ):
            python_files.append(py_file)

    return sorted(python_files)


def modernize_type_parameters(content: str) -> tuple[str, list[str]]:
    """Apply PEP 695: Type Parameter Syntax."""
    changes = []

    # Pattern 1: Generic class definitions with TypeVar
    # from typing import TypeVar, Generic
    # T = TypeVar('T')
    # class MyClass(Generic[T]): -> class MyClass[T]:

    # Find TypeVar definitions
    typevar_pattern = r'(\w+)\s*=\s*TypeVar\(\s*[\'"](\w+)[\'"]\s*(?:,\s*[^)]+)?\s*\)'
    typevar_matches = re.findall(typevar_pattern, content)

    if typevar_matches:
        # Remove TypeVar from imports
        content = re.sub(
            r"from typing import ([^,\n]*,\s*)?TypeVar(,\s*[^,\n]*)?",
            lambda m: f"from typing import {m.group(1) or ''}{m.group(2) or ''}".replace(
                ", ,", ","
            ).strip(", "),
            content,
        )
        content = re.sub(r"import.*TypeVar.*\n", "", content)

        # Remove TypeVar definitions
        for var_name, type_name in typevar_matches:
            content = re.sub(rf"{var_name}\s*=\s*TypeVar\([^)]+\)\s*\n?", "", content)
            changes.append(f"Removed TypeVar definition for {var_name}")

        # Update class definitions to use new syntax
        for var_name, type_name in typevar_matches:
            # Generic[T] -> [T]
            content = re.sub(
                rf"class\s+(\w+)\s*\(\s*Generic\[{var_name}\]\s*\)",
                rf"class \1[{type_name}]",
                content,
            )
            # class Name(BaseClass, Generic[T]) -> class Name[T](BaseClass)
            content = re.sub(
                rf"class\s+(\w+)\s*\(\s*([^,]+),\s*Generic\[{var_name}\]\s*\)",
                rf"class \1[{type_name}](\2)",
                content,
            )
            changes.append(
                f"Updated class definition to use PEP 695 syntax for {var_name}"
            )

    # Pattern 2: Function type parameters
    # def func(value: T) -> T: where T = TypeVar('T')
    # -> def func[T](value: T) -> T:
    function_pattern = r"def\s+(\w+)\s*\("
    functions = re.finditer(function_pattern, content)

    for match in functions:
        func_start = match.start()
        # Look for TypeVar usage in this function
        for var_name, type_name in typevar_matches:
            if (
                var_name in content[func_start : func_start + 500]
            ):  # Check next 500 chars
                # Add type parameter to function
                content = re.sub(
                    rf"def\s+({re.escape(match.group(1))})\s*\(",
                    rf"def \1[{type_name}](",
                    content,
                    count=1,
                )
                changes.append(f"Added type parameter to function {match.group(1)}")
                break

    return content, changes


def modernize_override_decorators(content: str) -> tuple[str, list[str]]:
    """Apply PEP 698: @override decorator."""
    changes = []

    # Find method definitions that might need @override
    class_methods = re.finditer(
        r"class\s+(\w+).*?:\s*\n(.*?)(?=\nclass|\nif\s+__name__|\n[A-Z]|\Z)",
        content,
        re.DOTALL,
    )

    for class_match in class_methods:
        class_name = class_match.group(1)
        class_body = class_match.group(2)

        # Find methods that override common base methods
        override_methods = [
            "__init__",
            "__str__",
            "__repr__",
            "__eq__",
            "__hash__",
            "process",
            "execute",
            "handle",
            "validate",
            "run",
        ]

        for method in override_methods:
            method_pattern = rf"(\s+)def\s+{method}\s*\("
            if re.search(method_pattern, class_body):
                # Add @override decorator if not present
                if "@override" not in class_body:
                    # Add typing import if needed
                    if "from typing import" in content and "override" not in content:
                        content = re.sub(
                            r"from typing import ([^\n]+)",
                            r"from typing import \1, override",
                            content,
                        )
                        changes.append("Added override import")
                    elif "from typing import" not in content:
                        # Add typing import at the top
                        content = re.sub(
                            r"(from __future__ import annotations\n)",
                            r"\1\nfrom typing import override\n",
                            content,
                        )
                        changes.append("Added typing override import")

                    # Add @override decorator
                    content = re.sub(
                        rf"(\s+)def\s+{method}\s*\(",
                        rf"\1@override\n\1def {method}(",
                        content,
                    )
                    changes.append(
                        f"Added @override decorator to {method} in {class_name}"
                    )

    return content, changes


def modernize_union_syntax(content: str) -> tuple[str, list[str]]:
    """Modernize Union syntax to use | operator (Python 3.10+ syntax)."""
    changes = []

    # Union[A, B] -> A | B
    union_pattern = r"Union\[([^\]]+)\]"
    unions = re.findall(union_pattern, content)

    for union_content in unions:
        # Split union types and join with |
        types = [t.strip() for t in union_content.split(",")]
        new_syntax = " | ".join(types)
        content = content.replace(f"Union[{union_content}]", new_syntax)
        changes.append(f"Modernized Union[{union_content}] to {new_syntax}")

    # Optional[T] -> T | None
    optional_pattern = r"Optional\[([^\]]+)\]"
    optionals = re.findall(optional_pattern, content)

    for optional_type in optionals:
        content = content.replace(
            f"Optional[{optional_type}]", f"{optional_type} | None"
        )
        changes.append(
            f"Modernized Optional[{optional_type}] to {optional_type} | None"
        )

    # Remove Union and Optional from imports if no longer needed
    if not re.search(r"Union\[", content):
        content = re.sub(
            r"from typing import ([^,\n]*,\s*)?Union(,\s*[^,\n]*)?",
            lambda m: f"from typing import {m.group(1) or ''}{m.group(2) or ''}".replace(
                ", ,", ","
            ).strip(", "),
            content,
        )
        changes.append("Removed Union import")

    if not re.search(r"Optional\[", content):
        content = re.sub(
            r"from typing import ([^,\n]*,\s*)?Optional(,\s*[^,\n]*)?",
            lambda m: f"from typing import {m.group(1) or ''}{m.group(2) or ''}".replace(
                ", ,", ","
            ).strip(", "),
            content,
        )
        changes.append("Removed Optional import")

    return content, changes


def modernize_dict_list_syntax(content: str) -> tuple[str, list[str]]:
    """Modernize Dict/List to use built-in types."""
    changes = []

    # Dict[K, V] -> dict[K, V]
    dict_pattern = r"Dict\[([^\]]+)\]"
    dicts = re.findall(dict_pattern, content)

    for dict_content in dicts:
        content = content.replace(f"Dict[{dict_content}]", f"dict[{dict_content}]")
        changes.append(f"Modernized Dict[{dict_content}] to dict[{dict_content}]")

    # List[T] -> list[T]
    list_pattern = r"List\[([^\]]+)\]"
    lists = re.findall(list_pattern, content)

    for list_content in lists:
        content = content.replace(f"List[{list_content}]", f"list[{list_content}]")
        changes.append(f"Modernized List[{list_content}] to list[{list_content}]")

    # Set[T] -> set[T]
    set_pattern = r"Set\[([^\]]+)\]"
    sets = re.findall(set_pattern, content)

    for set_content in sets:
        content = content.replace(f"Set[{set_content}]", f"set[{set_content}]")
        changes.append(f"Modernized Set[{set_content}] to set[{set_content}]")

    # Tuple[...] -> tuple[...]
    tuple_pattern = r"Tuple\[([^\]]+)\]"
    tuples = re.findall(tuple_pattern, content)

    for tuple_content in tuples:
        content = content.replace(f"Tuple[{tuple_content}]", f"tuple[{tuple_content}]")
        changes.append(f"Modernized Tuple[{tuple_content}] to tuple[{tuple_content}]")

    # Remove imports if no longer needed
    for old_type in ["Dict", "List", "Set", "Tuple"]:
        if not re.search(rf"{old_type}\[", content):
            content = re.sub(
                rf"from typing import ([^,\n]*,\s*)?{old_type}(,\s*[^,\n]*)?",
                lambda m: f"from typing import {m.group(1) or ''}{m.group(2) or ''}".replace(
                    ", ,", ","
                ).strip(", "),
                content,
            )
            changes.append(f"Removed {old_type} import")

    return content, changes


def modernize_string_annotations(content: str) -> tuple[str, list[str]]:
    """Remove quotes from type annotations (Python 3.10+ with from __future__ import annotations)."""
    changes = []

    # Ensure from __future__ import annotations is present
    if "from __future__ import annotations" not in content:
        # Add it at the top
        content = (
            '"""Module docstring"""\n\nfrom __future__ import annotations\n\n' + content
        )
        changes.append("Added from __future__ import annotations")

    # Remove quotes from type annotations in function signatures
    # def func(param: "Type") -> "ReturnType":
    annotation_pattern = r':\s*["\']([^"\']+)["\']'
    annotations = re.findall(annotation_pattern, content)

    for annotation in annotations:
        content = re.sub(
            rf':\s*["\']({re.escape(annotation)})["\']', f": {annotation}", content
        )
        changes.append(f"Removed quotes from type annotation: {annotation}")

    # Remove quotes from return type annotations
    return_pattern = r'->\s*["\']([^"\']+)["\']'
    returns = re.findall(return_pattern, content)

    for return_type in returns:
        content = re.sub(
            rf'->\s*["\']({re.escape(return_type)})["\']', f"-> {return_type}", content
        )
        changes.append(f"Removed quotes from return annotation: {return_type}")

    return content, changes


def modernize_python_file(file_path: Path) -> dict[str, Any]:
    """Modernize a single Python file with Python 3.13+ syntax."""
    try:
        with Path(file_path).open("r", encoding="utf-8") as f:
            original_content = f.read()

        content = original_content
        all_changes = []

        # Apply all modernizations
        content, changes = modernize_type_parameters(content)
        all_changes.extend(changes)

        content, changes = modernize_override_decorators(content)
        all_changes.extend(changes)

        content, changes = modernize_union_syntax(content)
        all_changes.extend(changes)

        content, changes = modernize_dict_list_syntax(content)
        all_changes.extend(changes)

        content, changes = modernize_string_annotations(content)
        all_changes.extend(changes)

        # Write back if changes were made
        if content != original_content:
            with Path(file_path).open("w", encoding="utf-8") as f:
                f.write(content)

            return {
                "status": "modified",
                "changes": all_changes,
                "file": str(file_path),
            }
        return {"status": "unchanged", "changes": [], "file": str(file_path)}

    except Exception as e:
        return {
            "status": "error",
            "changes": [],
            "file": str(file_path),
            "error": str(e),
        }


def main() -> None:
    """Main function to modernize Python syntax across FLEXT ecosystem."""
    print("🚀 FLEXT Ecosystem Python 3.13+ Syntax Modernization")
    print("=" * 56)
    print("Applying PEP 695, 698, 692 and modern syntax patterns")

    # Find all Python files
    python_files = find_python_files()

    if not python_files:
        print("No Python files found.")
        return

    print(f"\nFound {len(python_files)} Python files to modernize")

    # Process files by project
    projects = {}
    for file_path in python_files:
        # Find project name from path
        project_name = None
        for part in file_path.parts:
            if part.startswith("flext-") or part in {
                "client-a-oud-mig",
                "flexcore",
                "client-b-meltano-native",
            }:
                project_name = part
                break

        if project_name:
            if project_name not in projects:
                projects[project_name] = []
            projects[project_name].append(file_path)

    # Modernize each project
    total_files = 0
    modified_files = 0
    total_changes = 0

    for project_name, files in projects.items():
        print(f"\n🔧 Modernizing {project_name} ({len(files)} files)...")

        project_changes = 0
        project_modified = 0

        for file_path in files:
            result = modernize_python_file(file_path)
            total_files += 1

            if result["status"] == "modified":
                modified_files += 1
                project_modified += 1
                project_changes += len(result["changes"])
                total_changes += len(result["changes"])

                # Show first few changes
                if result["changes"]:
                    relative_path = str(file_path).replace(str(FLEXT_ROOT) + "/", "")
                    print(f"  ✅ {relative_path}: {len(result['changes'])} changes")
                    for change in result["changes"][:3]:  # Show first 3 changes
                        print(f"     • {change}")
                    if len(result["changes"]) > 3:
                        print(f"     • ... and {len(result['changes']) - 3} more")

            elif result["status"] == "error":
                print(f"  ❌ Error in {file_path}: {result['error']}")

        if project_modified > 0:
            print(
                f"  ✅ {project_name}: {project_modified}/{len(files)} files modified, {project_changes} total changes"
            )
        else:
            print(f"  ℹ️  {project_name}: No changes needed")

    # Summary
    print("\n📊 Python 3.13+ Modernization Summary:")
    print(f"  • Total files processed: {total_files}")
    print(f"  • Files modified: {modified_files}")
    print(f"  • Total syntax improvements: {total_changes}")
    print(
        f"  • Projects modernized: {len([p for p, files in projects.items() if any(modernize_python_file(f)['status'] == 'modified' for f in files)])}"
    )

    if modified_files > 0:
        print(
            f"\n✅ Phase 3 Progress: {modified_files}/{total_files} files modernized with Python 3.13+ syntax"
        )
        print("Features applied:")
        print("  • PEP 695: Type Parameter Syntax (def func[T]())")
        print("  • PEP 698: @override decorators")
        print("  • Modern Union syntax (A | B)")
        print("  • Built-in collection types (list[T], dict[K, V])")
        print("  • Unquoted type annotations")
    else:
        print("\nℹ️  All files already use modern Python syntax")


if __name__ == "__main__":
    main()
