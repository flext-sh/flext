#!/usr/bin/env python3
"""Fix call-arg errors systematically."""

import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def get_call_arg_errors() -> dict[str, list[dict[str, Any]]]:
    """Get all call-arg errors grouped by pattern."""
    cmd = [".venv/bin/python", "-m", "mypy", "flx/src/", "--show-error-codes", "--no-error-summary"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    errors_by_pattern = defaultdict(list)

    for line in result.stdout.splitlines() + result.stderr.splitlines():
        if " error: " in line and "[call-arg]" in line:
            match = re.match(r"(.+?):(\d+): error: (.+?) \[call-arg\]", line)
            if match:
                error_info = {
                    "file": match.group(1),
                    "line": int(match.group(2)),
                    "message": match.group(3),
                }

                # Categorize by error pattern
                msg = error_info["message"]
                if "Missing named argument" in msg:
                    errors_by_pattern["missing_named"].append(error_info)
                elif "Too many arguments" in msg:
                    errors_by_pattern["too_many"].append(error_info)
                elif "Unexpected keyword argument" in msg:
                    errors_by_pattern["unexpected_kwarg"].append(error_info)
                elif "takes no arguments" in msg:
                    errors_by_pattern["takes_no_args"].append(error_info)
                else:
                    errors_by_pattern["other"].append(error_info)

    return dict(errors_by_pattern)


def analyze_missing_arguments() -> dict[str, set[str]]:
    """Analyze which functions/classes are missing which arguments."""
    errors = get_call_arg_errors()
    missing_args_by_func = defaultdict(set)

    for error in errors.get("missing_named", []):
        # Extract function/class name and missing argument
        match = re.search(r'Missing named argument "(.+?)" for "(.+?)"', error["message"])
        if match:
            arg_name = match.group(1)
            func_name = match.group(2)
            missing_args_by_func[func_name].add(arg_name)

    return dict(missing_args_by_func)


def fix_specific_call_patterns() -> None:
    """Fix specific known call patterns."""
    # Fix FlxError calls with wrong arguments
    files_to_check = list(Path("flx/src").rglob("*.py"))

    for filepath in files_to_check:
        try:
            content = filepath.read_text()
            modified = False

            # Fix FlxError calls with positional args after message
            # Pattern: FlxError("message", "code", details={})
            # Should be: FlxError("message", error_code="code", details={})
            pattern = r'FlxError\(([^,]+),\s*"([^"]+)",\s*details=({[^}]*})\)'
            replacement = r'FlxError(\1, error_code="\2", details=\3)'
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True

            # Fix logger.add_detail calls
            # Pattern: logger.add_detail("key", value)
            # Should be: logger.flx_add_detail("key", value)
            if ".add_detail(" in content:
                content = content.replace(".add_detail(", ".flx_add_detail(")
                modified = True

            # Fix Path().exists calls
            # Pattern: path.exists
            # Should be: path.exists()
            pattern = r"(\w+)\.exists(?!\s*\()"
            if re.search(pattern, content):
                content = re.sub(pattern, r"\1.exists()", content)
                modified = True

            if modified:
                filepath.write_text(content)
                print(f"Fixed call patterns in {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def fix_constructor_defaults() -> None:
    """Add default values to constructors that are missing arguments."""
    # Classes that commonly have missing arguments
    classes_to_fix = {
        "FlxAdapterMeta": {
            "file": "flx/src/flx/core/models.py",
            "defaults": {
                "version": '"1.0.0"',
                "dependencies": "[]",
            },
        },
        "FlxAdapterResult": {
            "file": "flx/src/flx/core/models.py",
            "defaults": {
                "message": '""',
                "error": "None",
                "metadata": "{}",
            },
        },
    }

    for class_name, info in classes_to_fix.items():
        filepath = Path(info["file"])
        if not filepath.exists():
            # Try alternative locations
            alt_paths = [
                Path("flx/src/flx/adapters/models.py"),
                Path("flx/src/flx/core/adapters.py"),
            ]
            for alt_path in alt_paths:
                if alt_path.exists():
                    filepath = alt_path
                    break

        if filepath.exists():
            try:
                content = filepath.read_text()

                # Find the class definition
                class_pattern = rf"class {class_name}.*?:\n((?:    .*\n)*)"
                match = re.search(class_pattern, content, re.MULTILINE)

                if match:
                    class_body = match.group(0)

                    # Check if __init__ exists
                    if "def __init__" in class_body:
                        # Update __init__ to add defaults
                        for param, default in info["defaults"].items():
                            # Check if parameter exists without default
                            param_pattern = rf"{param}:\s*[^,\)]+(?![\s=])"
                            if re.search(param_pattern, class_body):
                                # Add default value
                                new_pattern = rf"({param}:\s*[^,\)]+)"
                                replacement = rf"\1 = {default}"
                                class_body = re.sub(new_pattern, replacement, class_body)

                    # Replace in content
                    content = content.replace(match.group(0), class_body)
                    filepath.write_text(content)
                    print(f"Fixed defaults in {class_name} at {filepath}")

            except Exception as e:
                print(f"Error fixing {class_name}: {e}")


def fix_method_signatures() -> None:
    """Fix method signatures that have changed."""
    # Common signature mismatches
    signature_fixes = [
        {
            "pattern": r"\.flx_log\(([^,]+),\s*([^,]+),\s*([^)]+)\)",
            "replacement": r".flx_log(\1, level=\2, message=\3)",
            "description": "Fix flx_log calls",
        },
        {
            "pattern": r"\.flx_create_logger\(([^)]+)\)",
            "replacement": r".flx_register_logger(\1)",
            "description": "Fix logger creation",
        },
    ]

    files_to_check = list(Path("flx/src").rglob("*.py"))

    for filepath in files_to_check:
        try:
            content = filepath.read_text()
            modified = False

            for fix in signature_fixes:
                if re.search(fix["pattern"], content):
                    content = re.sub(fix["pattern"], fix["replacement"], content)
                    modified = True
                    print(f"{fix['description']} in {filepath}")

            if modified:
                filepath.write_text(content)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def add_missing_type_imports() -> None:
    """Add missing imports for types used in signatures."""
    files_to_check = list(Path("flx/src").rglob("*.py"))

    for filepath in files_to_check:
        try:
            content = filepath.read_text()
            lines = content.splitlines()
            imports_to_add = set()

            # Check for Dict usage without import
            if re.search(r":\s*Dict\[", content) and "from typing import" in content:
                if "Dict" not in content.split("from typing import")[1].split("\n")[0]:
                    imports_to_add.add("Dict")

            # Check for Any usage without import
            if re.search(r":\s*Any\b", content) and "from typing import" in content:
                if "Any" not in content.split("from typing import")[1].split("\n")[0]:
                    imports_to_add.add("Any")

            # Check for field usage without import
            if "field(" in content and "from dataclasses import" in content:
                if "field" not in content:
                    imports_to_add.add("field")

            if imports_to_add:
                # Update typing imports
                for i, line in enumerate(lines):
                    if line.startswith("from typing import"):
                        imports = line.split("import")[1].strip()
                        current_imports = [imp.strip() for imp in imports.split(",")]
                        for imp in imports_to_add:
                            if imp not in current_imports:
                                current_imports.append(imp)
                        lines[i] = f"from typing import {', '.join(sorted(current_imports))}"
                        break

                filepath.write_text("\n".join(lines))
                print(f"Updated imports in {filepath}")

        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def main() -> None:
    """Main function to fix call-arg errors."""
    print("Analyzing call-arg errors...")

    errors = get_call_arg_errors()

    print("\nCall-arg error distribution:")
    for pattern, errs in errors.items():
        print(f"  {pattern}: {len(errs)} errors")

    # Analyze missing arguments
    missing_args = analyze_missing_arguments()
    print("\nFunctions/classes with missing arguments:")
    for func, args in sorted(missing_args.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"  {func}: {', '.join(sorted(args))}")

    print("\n1. Fixing specific call patterns...")
    fix_specific_call_patterns()

    print("\n2. Fixing constructor defaults...")
    fix_constructor_defaults()

    print("\n3. Fixing method signatures...")
    fix_method_signatures()

    print("\n4. Adding missing type imports...")
    add_missing_type_imports()

    print("\nDone! Run mypy again to check progress.")


if __name__ == "__main__":
    main()
