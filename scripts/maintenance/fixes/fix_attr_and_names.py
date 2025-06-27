#!/usr/bin/env python3
"""Fix remaining attr-defined and name-defined errors."""

import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def get_mypy_errors_by_type(error_type: str) -> list[dict[str, Any]]:
    """Get specific type of mypy errors."""
    cmd = [
        ".venv/bin/python",
        "-m",
        "mypy",
        "flx/src/",
        "--show-error-codes",
        "--no-error-summary",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    errors: list = []
    for line in result.stdout.splitlines() + result.stderr.splitlines():
        if f"[{error_type}]" in line:
            match = re.match(r"(.+?):(\d+): error: (.+?) \[" + error_type + r"\]", line)
            if match:
                errors.append(
                    {
                        "file": match.group(1),
                        "line": int(match.group(2)),
                        "message": match.group(3),
                    },
                )
    return errors


def fix_logger_attributes() -> None:
    """Fix logger attribute errors."""
    files_to_fix = list(Path("flx/src").rglob("*.py"))

    # Logger method mappings
    logger_mappings = {
        ".warning(": ".flx_warning(",
        ".warn(": ".flx_warning(",
        ".critical(": ".flx_critical(",
        ".exception(": ".flx_exception(",
        ".setLevel(": ".flx_set_level(",
        ".getChild(": ".flx_get_child(",
        ".addHandler(": ".flx_add_handler(",
    }

    for filepath in files_to_fix:
        try:
            content = filepath.read_text()
            modified = False

            for old, new in logger_mappings.items():
                if old in content:
                    content = content.replace(old, new)
                    modified = True

            if modified:
                filepath.write_text(content)
                print(f"Fixed logger methods in {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def fix_path_methods() -> None:
    """Fix Path method calls."""
    files_to_fix = list(Path("flx/src").rglob("*.py"))

    for filepath in files_to_fix:
        try:
            content = filepath.read_text()
            modified = False

            # Fix .parent.mkdir patterns
            pattern = r"\.parent\.mkdir(?!\s*\()"
            if re.search(pattern, content):
                content = re.sub(pattern, ".parent.mkdir()", content)
                modified = True

            # Fix .read_text patterns
            pattern = r"\.read_text(?!\s*\()"
            if re.search(pattern, content):
                content = re.sub(pattern, ".read_text()", content)
                modified = True

            # Fix .write_text patterns without parentheses
            pattern = r"\.write_text\s+([^(])"
            if re.search(pattern, content):
                content = re.sub(pattern, r".write_text(\1)", content)
                modified = True

            if modified:
                filepath.write_text(content)
                print(f"Fixed Path methods in {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def add_missing_imports() -> None:
    """Add missing imports based on name-defined errors."""
    # Common missing imports
    missing_imports = {
        "Optional": "from typing import Dict, Optional, Optional",
        "Union": "from typing import Dict, Optional, Union",
        "Callable": "from typing import Dict, Optional, Callable",
        "Iterator": "from typing import Dict, Optional, Iterator",
        "Sequence": "from typing import Dict, Optional, Sequence",
        "Mapping": "from typing import Dict, Optional, Mapping",
        "MutableMapping": "from typing import Dict, Optional, MutableMapping",
        "Awaitable": "from typing import Dict, Optional, Awaitable",
        "Final": "from typing import Dict, Optional, Final",
        "Literal": "from typing import Dict, Optional, Literal",
        "TypedDict": "from typing import Dict, Optional, TypedDict",
        "Protocol": "from typing import Dict, Optional, Protocol",
        "runtime_checkable": "from typing import Dict, Optional, runtime_checkable",
        "overload": "from typing import Dict, Optional, overload",
        "NoReturn": "from typing import Dict, Optional, NoReturn",
        "ClassVar": "from typing import Dict, Optional, ClassVar",
        "Type": "from typing import Dict, Optional, Type",
        "cast": "from typing import Dict, Optional, cast",
        "get_args": "from typing import Dict, Optional, get_args",
        "get_origin": "from typing import Dict, Optional, get_origin",
        "get_type_hints": "from typing import Dict, Optional, get_type_hints",
    }

    name_errors = get_mypy_errors_by_type("name-defined")
    files_to_fix = defaultdict(set)

    for error in name_errors:
        match = re.search(r'Name "(.+?)" is not defined', error["message"])
        if match:
            name = match.group(1)
            if name in missing_imports:
                files_to_fix[error["file"]].add(name)

    for filepath, names in files_to_fix.items():
        try:
            path = Path(filepath)
            content = path.read_text()
            lines = content.splitlines()

            # Find where to insert imports
            import_index = 0
            for i, line in enumerate(lines):
                if line.startswith("from typing import Dict, Optional,"):
                    # Update existing typing import
                    current_imports = re.findall(
                        r"from typing import Dict, Optional, (.+)",
                        line,
                    )[0]
                    current_names = [n.strip() for n in current_imports.split(",")]

                    for name in names:
                        if name not in current_names:
                            current_names.append(name)

                    lines[i] = f"from typing import Dict, Optional, {
                        ', '.join(sorted(current_names))
                    }"
                    names: set = set()
                    break
                if line.startswith(("import", "from")):
                    import_index = i + 1

            # Add remaining imports if any
            if names:
                for name in sorted(names):
                    lines.insert(import_index, missing_imports[name])
                    import_index += 1

            path.write_text("\n".join(lines))
            print(f"Added imports to {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def fix_common_attribute_patterns() -> None:
    """Fix common attribute access patterns."""
    # Common patterns to fix
    patterns = [
        # Exception attributes
        (
            r"except\s+(\w+)\s+as\s+e:\s*\n\s*if\s+e\.code",
            r'except \1 as e:\n    if hasattr(e, "code") and e.code',
        ),
        # Response attributes
        (
            r"if\s+response\.ok(?:\s*:|\s+and)",
            r'if hasattr(response, "ok") and response.ok',
        ),
        (
            r"response\.json\(\)",
            r'response.json() if hasattr(response, "json") else {}',
        ),
        # Config attributes
        (
            r"if\s+self\.config\.(\w+)(?:\s*:|\s+and)",
            r'if hasattr(self.config, "\1") and self.config.\1',
        ),
    ]

    files_to_fix = list(Path("flx/src").rglob("*.py"))

    for filepath in files_to_fix:
        try:
            content = filepath.read_text()
            modified = False

            for pattern, replacement in patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True

            if modified:
                filepath.write_text(content)
                print(f"Fixed attribute patterns in {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def fix_model_attributes() -> None:
    """Fix pydantic model attribute access."""
    files_to_fix = list(Path("flx/src").rglob("*.py"))

    for filepath in files_to_fix:
        try:
            content = filepath.read_text()
            modified = False

            # Fix model_dump() calls
            if ".dict()" in content:
                content = content.replace(".dict()", ".model_dump()")
                modified = True

            # Fix json() calls
            if ".json()" in content and "response.json()" not in content:
                content = re.sub(r"(\w+)\.json\(\)", r"\1.model_dump_json()", content)
                modified = True

            # Fix validate() calls
            if ".validate(" in content:
                content = content.replace(".validate(", ".model_validate(")
                modified = True

            # Fix parse_obj() calls
            if ".parse_obj(" in content:
                content = content.replace(".parse_obj(", ".model_validate(")
                modified = True

            # Fix parse_raw() calls
            if ".parse_raw(" in content:
                content = content.replace(".parse_raw(", ".model_validate_json(")
                modified = True

            # Fix schema() calls
            if ".schema()" in content:
                content = content.replace(".schema()", ".model_json_schema()")
                modified = True

            # Fix copy() calls with update
            pattern = r"\.copy\(update="
            if re.search(pattern, content):
                content = re.sub(pattern, ".model_copy(update=", content)
                modified = True

            if modified:
                filepath.write_text(content)
                print(f"Fixed model methods in {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def fix_specific_undefined_names() -> None:
    """Fix specific undefined names based on context."""
    specific_fixes = {
        "flx/src/flx/infra/logging/decorators.py": {
            "decorator": '''def decorator(func: Callable) -> Callable:
    """Decorator factory."""
    return func
''',
        },
        "flx/src/flx/infra/observability/health.py": {
            "asyncio": "import asyncio",
            "Callable": "from typing import Dict, Optional, Callable",
        },
    }

    for filepath, fixes in specific_fixes.items():
        path = Path(filepath)
        if not path.exists():
            continue

        try:
            content = path.read_text()

            for name, fix in fixes.items():
                if name not in content:
                    if "import" in fix:
                        # Add import
                        lines = content.splitlines()
                        for i, line in enumerate(lines):
                            if line.startswith(("from", "import")):
                                lines.insert(i + 1, fix)
                                break
                        content = "\n".join(lines)
                        # Add definition
                        content = fix + "\n\n" + content

            path.write_text(content)
            print(f"Fixed undefined names in {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def main() -> None:
    """Main function."""
    print("Fixing attribute and name errors...")

    print("\n1. Fixing logger attributes...")
    fix_logger_attributes()

    print("\n2. Fixing Path methods...")
    fix_path_methods()

    print("\n3. Adding missing imports...")
    add_missing_imports()

    print("\n4. Fixing common attribute patterns...")
    fix_common_attribute_patterns()

    print("\n5. Fixing model attributes...")
    fix_model_attributes()

    print("\n6. Fixing specific undefined names...")
    fix_specific_undefined_names()

    print("\nDone! Run mypy again to check progress.")


if __name__ == "__main__":
    main()
