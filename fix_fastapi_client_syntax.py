#!/usr/bin/env python3
"""Fix syntax errors in fastapi_client_demo.py file."""

import re
from pathlib import Path


def fix_syntax_errors():
    """Fix all syntax errors in the fastapi client demo file."""
    file_path = Path("legacy/flx/examples/adapters/fastapi_client_demo.py")

    if not file_path.exists():
        return

    content = file_path.read_text()

    # Fix malformed logging statements like:
    # logger.info("Log message")
    #     "actual message",
    #     extra={...}
    # )

    # Pattern to match malformed logger calls
    pattern = r'logger\.info\("Log message"\)\s*\n\s*"([^"]+)"[,)]?\s*\n(\s*extra=\{[^}]*\}\s*\n\s*\))?'

    def fix_logger_call(match):
        message = match.group(1)
        extra_part = match.group(2) if match.group(2) else ""

        if extra_part:
            # Extract the extra dict content
            extra_content = re.search(r"extra=(\{[^}]*\})", extra_part)
            if extra_content:
                extra_dict = extra_content.group(1)
                return f'logger.info(\n    "{message}",\n    extra={extra_dict}\n)'

        return f'logger.info("{message}")'

    # Apply the fix
    fixed_content = re.sub(pattern, fix_logger_call, content, flags=re.MULTILINE | re.DOTALL)

    # Fix function call formatting issues
    # Pattern like: func(\n    param)\n    another_param\n)
    func_pattern = r"(\w+\.[\w_]+\(\s*\n\s*[^)]+)\)\s*\n\s*([^)]+\n\s*\))"

    def fix_func_call(match):
        func_part = match.group(1)
        param_part = match.group(2)

        # Add comma between parameters
        return func_part + ",\n    " + param_part

    fixed_content = re.sub(func_pattern, fix_func_call, fixed_content, flags=re.MULTILINE)

    # Fix standalone closing parentheses that should be part of function calls
    standalone_paren_pattern = r"(\s+)([^)]+)\s*\n\s*\)\s*\n\s*\)"
    fixed_content = re.sub(standalone_paren_pattern, r"\1\2\n)", fixed_content, flags=re.MULTILINE)

    if fixed_content != content:
        file_path.write_text(fixed_content)
    else:
        pass


if __name__ == "__main__":
    fix_syntax_errors()
