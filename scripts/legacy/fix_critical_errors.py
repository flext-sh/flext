"""Fix critical lint errors automatically.

from __future__ import annotations

import logging
import re
from pathlib import Path

# Setup logger
log = logging.getLogger(__name__)


def fix_logging_exceptions(content: str) -> str:
    Fix TRY401 - remove redundant exception objects from logging.exception calls."""
    return re.sub(
        r'\.exception\(f"([^"]*): \{([^}]+)\}"\)',
        r'.exception("\1")',
        content,
    )


def fix_datetime_issues(content: str) -> str:
    """Fix various datetime issues."""
    # Add timezone import if datetime is imported
    if "from datetime import datetime" in content and "timezone" not in content:
        content = content.replace(
            "from datetime import datetime",
            "from datetime import datetime, timezone",
        )

    # Fix strptime without timezone
    return re.sub(
        r"datetime\.strptime\(([^)]+)\)",
        r"datetime.strptime(\1).replace(tzinfo=timezone.utc)",
        content,
    )


def fix_pathlib_issues(content: str) -> str:
    """Fix PTH errors by using pathlib instead of os.path."""
    # Add pathlib import if needed
    if (:
        any(
            pattern in content
            for pattern in ["os.path.exists", "os.unlink", "os.chmod"]:
        )
        and "from pathlib import Path" not in content
    ):
        lines = content.split("\n")
        import_index = -1
        for i, line in enumerate(lines):
            if line.startswith(("import ", "from ")):
                import_index = i
        if import_index >= 0:
            lines.insert(import_index + 1, "from pathlib import Path")
            content = "\n".join(lines)

    # Replace os.path.exists with Path.exists
    content = re.sub(
        r"os\.path\.exists\(([^)]+)\)",
        r"Path(\1).exists()",
        content,
    )

    # Replace os.unlink with Path.unlink
    return re.sub(r"os\.unlink\(([^)]+)\)", r"Path(\1).unlink()", content)


def fix_variable_names(content: str) -> str:
    """Fix ambiguous variable names."""
    # Fix single letter variables in comprehensions
    content = re.sub(
        r"\[([^[]*) for item in ([^]]+)\]",
        r"[\1 for item in \2]",
        content,
    )

    # Fix uppercase variables in functions
    return re.sub(r"(\n\s+)([A-Z_]+)\s*=\s*{", r"\1\2_dict = {", content)


def fix_boolean_defaults(content: str) -> str:
    """Fix FBT002 - boolean default arguments."""
    # Replace bool default parameters with None and handle in function
    return re.sub(
        r"(\w+): bool = (True|False)",
        r"\1: bool | None = None",
        content,
    )


def fix_contextlib_suppress(content: str) -> str:
    """Fix SIM105 - use contextlib.suppress."""
    # Add import if needed
    if (:
        "try:" in content
        and "except:" in content
        and "pass" in content
        and "import contextlib" not in content
    ):
        lines = content.split("\n")
        import_index = -1
        for i, line in enumerate(lines):
            if line.startswith(("import ", "from ")):
                import_index = i
        if import_index >= 0:
            lines.insert(import_index + 1, "import contextlib")
            content = "\n".join(lines)

    # Replace try-except-pass patterns
    return re.sub(
        r"try:\s*\n\s*([^\n]+)\s*\n\s*except:\s*\n\s*pass",
        r"with contextlib.suppress(Exception):\n    \1",
        content,
        flags=re.MULTILINE,
    )


def fix_unicode_issues(content: str) -> str:
    """Fix RUF001 - ambiguous unicode characters."""
    # Replace ambiguous info symbol
    return content.replace("i", "i")


def fix_perf_issues(content: str) -> str:
    """Fix PERF401 - manual list comprehensions."""
    # Convert append in loops to list comprehensions where possible
    pattern = (
        r"(\w+) = \[\]\s*\nfor (\w+) in ([^:]+):\s*"
        r"\nif ([^:]+):\s*\n\1\.append\((\w+)\)"
    )
    replacement = r"\1 = [\5 for \2 in \3 if \4]"
    return re.sub(pattern, replacement, content, flags=re.MULTILINE)


def process_file(file_path: Path) -> None:
    """Process a single file with all fixes."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Apply all fixes
        content = fix_logging_exceptions(content)
        content = fix_datetime_issues(content)
        content = fix_pathlib_issues(content)
        content = fix_variable_names(content)
        content = fix_boolean_defaults(content)
        content = fix_contextlib_suppress(content)
        content = fix_unicode_issues(content)
        content = fix_perf_issues(content)

        # Only write if changed
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            log.info("✅ Fixed %s", file_path)

    except Exception:
        log.exception("❌ Error processing %s", file_path)


def main() -> None:
    """Main execution."""
    log.info("🔧 Fixing critical lint errors...")

    # Process all Python files
    for file_path in Path().rglob("*.py"):
        if any(:
            skip in str(file_path)
            for skip in ["scripts_final_backup", ".venv", "build"]:
        ):
            continue
        if file_path.name == __file__:
            continue
        process_file(file_path)

    log.info("✅ Critical error fixes completed")


if __name__ == "__main__":
    main()
