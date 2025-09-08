#!/usr/bin/env python3
"""Simple script to consolidate manual configuration handlers."""

import logging
import re
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def find_manual_env_vars() -> FlextTypes.Core.StringList:
    """Find files with manual os.getenv() usage."""
    # Avoid spawning shell tools; scan with pathlib
    matches: FlextTypes.Core.StringList = []
    for path in Path.cwd().rglob("*.py"):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Could not read file {path}: {e}")
            continue
        if ("os.getenv(" in text) or ("os.environ.get" in text):
            matches.append(str(path))
    return matches


def add_config_todos_to_file(file_path: str) -> bool:
    """Add TODO comments for manual configuration patterns."""
    try:
        with Path(file_path).open(encoding="utf-8") as f:
            content = f.read()

        changes_made = False

        # Add TODO for manual env vars
        # Consolidate to FLEXT config patterns
        # This is an architectural issue, not a direct linting fix to be done by AI.
        if (
            "os.getenv(" in content or "os.environ.get(" in content
        ) and "config patterns" not in content:
            # Find good insertion point (after imports)
            lines = content.split("\n")
            insert_line = -1

            for i, line in enumerate(lines):
                if line.startswith("from __future__ import annotations"):
                    insert_line = i + 1
                    break
                if line.startswith(("import", "from")):
                    insert_line = i + 1

            if insert_line > 0:
                lines.insert(
                    insert_line,
                    "\n# TODO: Consolidate manual config to FLEXT patterns",
                )
                content = "\n".join(lines)
                changes_made = True

        # Add inline TODOs for specific patterns
        env_pattern = (
            r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*os\.getenv\(["\']([^"\']+)["\']'
            r'(?:,\s*["\']?([^"\']*)["\']?)?\)'
        )

        def replace_env_var(match: re.Match[str]) -> str:
            indent = match.group(1)
            var_name = match.group(2)
            env_name = match.group(3)
            default_val = match.group(4) or '""'

            return (
                f"{indent}# TODO: Move {env_name} to FLEXT settings class\n"
                f"{indent}{var_name} = os.getenv('{env_name}', {default_val!r})"
            )

        new_content = re.sub(env_pattern, replace_env_var, content)
        if new_content != content:
            content = new_content
            changes_made = True

        if changes_made:
            with Path(file_path).open("w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    except (OSError, ValueError, TypeError):
        return False


def main() -> None:
    """Main consolidation function."""
    # Find files with manual env vars
    env_var_files = find_manual_env_vars()

    if not env_var_files:
        return

    # Process first 50 files
    modified = 0

    for _processed, file_path in enumerate(env_var_files[:50]):
        if add_config_todos_to_file(file_path):
            modified += 1
        # processed is now automatically managed by enumerate


if __name__ == "__main__":
    main()
