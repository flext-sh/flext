#!/usr/bin/env python3
"""Script to systematically fix all mypy errors in the FLX project."""

import re
import subprocess


def run_mypy() -> str:
    """Run mypy and return the output."""
    try:
        result = subprocess.run(
            ["mypy", "flx/", "--config-file", "mypy.ini"],
            capture_output=True,
            text=True,
            cwd="/home/marlonsc/pyauto", check=False,
        )
        return result.stdout
    except Exception as e:
        print(f"Error running mypy: {e}")
        return ""


def parse_mypy_errors(output: str) -> list[dict[str, str]]:
    """Parse mypy output into structured errors."""
    errors = []
    lines = output.split('\n')

    for line in lines:
        if ': error:' in line:
            # Parse the error line
            match = re.match(r'^([^:]+):(\d+): error: (.+) \[([^\]]+)\]', line)
            if match:
                file_path, line_no, message, error_code = match.groups()
                errors.append({
                    'file': file_path,
                    'line': int(line_no),
                    'message': message,
                    'code': error_code,
                })

    return errors


def fix_logging_imports(file_path: str) -> bool:
    """Fix logging import issues in a file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # If file uses logging but doesn't import it
        if 'logging.' in content and 'import logging' not in content:
            # Add import at the top after existing imports
            lines = content.split('\n')
            import_index = 0

            # Find where to insert the import
            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    import_index = i + 1
                elif line.strip() == '' and import_index > 0:
                    break

            lines.insert(import_index, 'import logging')

            with open(file_path, 'w', encoding="utf-8") as f:
                f.write('\n'.join(lines))
            return True

    except Exception as e:
        print(f"Error fixing logging imports in {file_path}: {e}")

    return False


def fix_type_annotations(file_path: str, line_no: int, message: str) -> bool:
    """Fix type annotation issues."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        if line_no <= len(lines):
            line = lines[line_no - 1]

            # Fix missing return type annotations
            if "Function is missing a return type annotation" in message:
                # Add -> None if function doesn't return value
                if "Use \"-> None\" if function does not return a value" in message:
                    # Find the function definition
                    if 'def ' in line and ')' in line and ':' in line:
                        line = line.replace('):', ') -> None:')
                        lines[line_no - 1] = line

                        with open(file_path, 'w', encoding="utf-8") as f:
                            f.writelines(lines)
                        return True

            # Fix variable annotations
            elif "Need type annotation for" in message:
                var_match = re.search(r'Need type annotation for "([^"]+)"', message)
                if var_match:
                    var_name = var_match.group(1)
                    # Add type annotation based on context
                    if f'{var_name} = []' in line:
                        line = line.replace(f'{var_name} = []', f'{var_name}: list[Any] = []')
                    elif f'{var_name} = {{}}' in line:
                        line = line.replace(f'{var_name} = {{}}', f'{var_name}: dict[str, Any] = {{}}')
                    else:
                        # Generic annotation
                        line = line.replace(f'{var_name} = ', f'{var_name}: Any = ')

                    lines[line_no - 1] = line

                    with open(file_path, 'w', encoding="utf-8") as f:
                        f.writelines(lines)
                    return True

    except Exception as e:
        print(f"Error fixing type annotations in {file_path}:{line_no}: {e}")

    return False


def fix_attribute_errors(file_path: str, line_no: int, message: str) -> bool:
    """Fix attribute errors."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        if line_no <= len(lines):
            lines[line_no - 1]

            # Fix logging attribute errors
            if 'Module has no attribute "getLogger"' in message:
                # Ensure logging is imported
                if 'import logging' not in '\n'.join(lines[:10]):
                    # Add import at the top
                    for i, line in enumerate(lines):
                        if line.startswith('from __future__'):
                            continue
                        if line.startswith(("import ", "from ")):
                            if 'import logging' not in line:
                                lines.insert(i, 'import logging\n')
                                break
                        elif line.strip() == '':
                            lines.insert(i, 'import logging\n')
                            break

                    with open(file_path, 'w', encoding="utf-8") as f:
                        f.writelines(lines)
                    return True

    except Exception as e:
        print(f"Error fixing attribute errors in {file_path}:{line_no}: {e}")

    return False


def fix_file_errors(file_path: str, errors: list[dict[str, str]]) -> int:
    """Fix all errors in a specific file."""
    fixed_count = 0

    # Group errors by type
    logging_errors = [e for e in errors if 'logging' in e['message'].lower()]
    type_errors = [e for e in errors if e['code'] in {'no-untyped-def', 'var-annotated'}]
    attr_errors = [e for e in errors if e['code'] == 'attr-defined']

    # Fix logging imports first
    if logging_errors and fix_logging_imports(file_path):
        fixed_count += len(logging_errors)

    # Fix type annotations
    for error in type_errors:
        if fix_type_annotations(file_path, error['line'], error['message']):
            fixed_count += 1

    # Fix attribute errors
    for error in attr_errors:
        if fix_attribute_errors(file_path, error['line'], error['message']):
            fixed_count += 1

    return fixed_count


def main():
    """Main function to fix all mypy errors."""
    print("Running mypy to identify errors...")
    output = run_mypy()

    if not output:
        print("No mypy output received")
        return

    errors = parse_mypy_errors(output)
    print(f"Found {len(errors)} mypy errors")

    # Group errors by file
    errors_by_file: dict[str, list[dict[str, str]]] = {}
    for error in errors:
        file_path = error['file']
        if file_path not in errors_by_file:
            errors_by_file[file_path] = []
        errors_by_file[file_path].append(error)

    total_fixed = 0

    # Fix errors file by file
    for file_path, file_errors in errors_by_file.items():
        print(f"\nProcessing {file_path} ({len(file_errors)} errors)...")
        fixed = fix_file_errors(file_path, file_errors)
        total_fixed += fixed
        print(f"Fixed {fixed}/{len(file_errors)} errors in {file_path}")

    print(f"\nTotal errors fixed: {total_fixed}/{len(errors)}")

    # Run mypy again to check progress
    print("\nRunning mypy again to check progress...")
    new_output = run_mypy()
    new_errors = parse_mypy_errors(new_output)
    print(f"Remaining errors: {len(new_errors)}")


if __name__ == "__main__":
    main()
