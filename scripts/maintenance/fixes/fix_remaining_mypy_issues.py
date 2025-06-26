#!/usr/bin/env python3
"""Fix remaining mypy issues systematically."""

import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def get_mypy_errors() -> dict[str, list[dict[str, Any]]]:
    """Get all mypy errors grouped by type."""
    cmd = [
        ".venv/bin/python",
        "-m",
        "mypy",
        "flx/src/",
        "--show-error-codes",
        "--no-error-summary",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    errors_by_type = defaultdict(list)

    for line in result.stdout.splitlines() + result.stderr.splitlines():
        if "error:" in line:
            match = re.match(r"(.+?):(\d+): error: (.+?) \[(.+?)\]", line)
            if match:
                error = {
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "message": match.group(3),
                    "type": match.group(4),
                }
                errors_by_type[error["type"]].append(error)

    return errors_by_type


def fix_import_attr_errors() -> None:
    """Fix import attribute errors."""
    errors = get_mypy_errors()
    attr_errors = errors.get("attr-defined", [])

    # Fix common patterns
    fixes = {
        # CLI command patterns
        "fix_create_cli": "flx_fix_create_cli",
        "register_cli_command_provider": "flx_register_cli_command_provider",
        "get_adapter_registry": "flx_get_adapter_registry",
        # Logger patterns
        "logger.warning": "logger.flx_warning",
        "logger.critical": "logger.flx_critical",
        "logger.exception": "logger.flx_exception",
        # Health check patterns
        "health_check()": "flx_health_check()",
    }

    files_to_fix: set = set()
    for error in attr_errors:
        files_to_fix.add(error["file"])

    for filepath in files_to_fix:
        try:
            path = Path(filepath)
            if not path.exists():
                continue

            content = path.read_text()
            modified = False

            for old, new in fixes.items():
                if old in content:
                    content = content.replace(old, new)
                    modified = True

            if modified:
                path.write_text(content)
                print(f"Fixed imports/attributes in {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def fix_missing_flx_prefix() -> None:
    """Fix missing flx_ prefix on methods."""
    files_to_check = list(Path("flx/src").rglob("*.py"))

    # Common method names that need flx_ prefix
    methods_to_fix = [
        "create_cli",
        "register_command",
        "get_adapter",
        "health_check",
        "execute_command",
        "initialize",
        "shutdown",
        "validate",
        "process",
        "handle",
        "dispatch",
        "publish",
        "subscribe",
        "connect",
        "disconnect",
        "send",
        "receive",
        "transform",
        "serialize",
        "deserialize",
        "encode",
        "decode",
    ]

    for filepath in files_to_check:
        try:
            content = filepath.read_text()
            modified = False

            for method in methods_to_fix:
                # Fix method calls
                pattern = rf"\.{method}\("
                replacement = f".flx_{method}("
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True

                # Fix method definitions
                pattern = rf"def {method}\("
                replacement = f"def flx_{method}("
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True

                # Fix async method definitions
                pattern = rf"async def {method}\("
                replacement = f"async def flx_{method}("
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True

            if modified:
                filepath.write_text(content)
                print(f"Fixed method names in {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def fix_constructor_args() -> None:
    """Fix constructor argument errors."""
    errors = get_mypy_errors()
    call_arg_errors = errors.get("call-arg", [])

    # Group by common patterns
    adapter_meta_errors: list = []
    adapter_result_errors: list = []
    other_errors: list = []

    for error in call_arg_errors:
        if "FlxAdapterMeta" in error["message"]:
            adapter_meta_errors.append(error)
        elif "FlxAdapterResult" in error["message"]:
            adapter_result_errors.append(error)
            other_errors.append(error)

    # Fix FlxAdapterMeta calls
    for error in adapter_meta_errors:
        filepath = Path(error["file"])
        if filepath.exists():
            try:
                content = filepath.read_text()
                content.splitlines()

                # Find FlxAdapterMeta calls missing version/dependencies
                pattern = (
                    r'FlxAdapterMeta\(\s*name="([^"]+)",\s*adapter_type=([^,\)]+)\s*\)'
                )
                replacement = r'FlxAdapterMeta(name="\1", adapter_type=\2, version="1.0.0", dependencies=[])'

                new_content = re.sub(pattern, replacement, content)

                if new_content != content:
                    filepath.write_text(new_content)
                    print(f"Fixed FlxAdapterMeta in {filepath}")

            except Exception as e:
                print(f"Error fixing {filepath}: {e}")

    # Fix FlxAdapterResult calls
    for error in adapter_result_errors:
        filepath = Path(error["file"])
        if filepath.exists():
            try:
                content = filepath.read_text()

                # Fix FlxAdapterResult calls missing required args
                pattern = r"FlxAdapterResult\(success=(True|False)\)"
                replacement = r'FlxAdapterResult(success=\1, data={}, message="", error=None, metadata={})'

                new_content = re.sub(pattern, replacement, content)

                # Fix partial FlxAdapterResult calls
                pattern = r'FlxAdapterResult\(success=(True|False),\s*error="([^"]+)"\)'
                replacement = r'FlxAdapterResult(success=\1, data={}, message="", error="\2", metadata={})'

                new_content = re.sub(pattern, replacement, new_content)

                if new_content != content:
                    filepath.write_text(new_content)
                    print(f"Fixed FlxAdapterResult in {filepath}")

            except Exception as e:
                print(f"Error fixing {filepath}: {e}")


def add_missing_type_imports() -> None:
    """Add missing type imports."""
    errors = get_mypy_errors()
    name_errors = errors.get("name-defined", [])

    # Group missing types by file
    missing_by_file = defaultdict(set)

    for error in name_errors:
        match = re.search(r'Name "(.+?)" is not defined', error["message"])
        if match:
            name = match.group(1)
            missing_by_file[error["file"]].add(name)

    # Common type imports
    type_imports = {
        "AsyncGenerator": "from collections.abc import AsyncGenerator",
        "AsyncIterator": "from collections.abc import AsyncIterator",
        "Awaitable": "from collections.abc import Awaitable",
        "Callable": "from collections.abc import Callable",
        "Iterator": "from collections.abc import Iterator",
        "Sequence": "from collections.abc import Sequence",
        "Mapping": "from collections.abc import Mapping",
        "MutableMapping": "from collections.abc import MutableMapping",
        "Generator": "from collections.abc import Generator",
        "Coroutine": "from collections.abc import Coroutine",
        "Hashable": "from collections.abc import Hashable",
        "Sized": "from collections.abc import Sized",
        "Container": "from collections.abc import Container",
        "Collection": "from collections.abc import Collection",
        "Set": "from collections.abc import Set",
        "MutableSet": "from collections.abc import MutableSet",
        "ByteString": "from collections.abc import ByteString",
        "MutableSequence": "from collections.abc import MutableSequence",
        "ItemsView": "from collections.abc import ItemsView",
        "KeysView": "from collections.abc import KeysView",
        "ValuesView": "from collections.abc import ValuesView",
        "AbstractSet": "from collections.abc import AbstractSet",
    }

    for filepath, missing_names in missing_by_file.items():
        try:
            path = Path(filepath)
            if not path.exists():
                continue

            content = path.read_text()
            lines = content.splitlines()

            # Find where to insert imports
            import_index = 0
            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    import_index = i + 1

            # Add missing imports
            added_imports: list = []
            for name in missing_names:
                if name in type_imports and type_imports[name] not in content:
                    added_imports.append(type_imports[name])

            if added_imports:
                for imp in sorted(set(added_imports)):
                    lines.insert(import_index, imp)
                    import_index += 1

                path.write_text("\n".join(lines))
                print(
                    f"Added imports to {filepath}: {
                        ', '.join(
                            name for name in missing_names if name in type_imports
                        )
                    }",
                )

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def main() -> None:
    """Main function."""
    print("Fixing remaining mypy issues...")

    print("\n1. Fixing import attribute errors...")
    fix_import_attr_errors()

    print("\n2. Fixing missing flx_ prefix...")
    fix_missing_flx_prefix()

    print("\n3. Fixing constructor arguments...")
    fix_constructor_args()

    print("\n4. Adding missing type imports...")
    add_missing_type_imports()

    print("\nDone! Run mypy again to check progress.")


if __name__ == "__main__":
    main()
