#!/usr/bin/env python3
"""Simple script to consolidate manual configuration handlers."""

import re
import subprocess
from typing import Any

print("🔍 Starting manual configuration consolidation...")


def find_manual_env_vars() -> list[str]:
    """Find files with manual os.getenv() usage."""
    cmd = [
        "find", ".", "-name", "*.py", "-type", "f",
        "-exec", "grep", "-l", "os\\.getenv\\|os\\.environ\\.get", "{}", ";",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return [f.strip() for f in result.stdout.split("\n") if f.strip()]
    return []


def add_config_todos_to_file(file_path: str) -> bool:
    """Add TODO comments for manual configuration patterns."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        changes_made = False

        # Add TODO for manual env vars
        if "os.getenv(" in content or "os.environ.get(" in content:
            if "# TODO: Consolidate to FLEXT config patterns" not in content:
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
                    lines.insert(insert_line, "\n# TODO: Consolidate manual config to FLEXT patterns")
                    content = "\n".join(lines)
                    changes_made = True

        # Add inline TODOs for specific patterns
        env_pattern = r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*os\.getenv\(["\']([^"\']+)["\'](?:,\s*["\']?([^"\']*)["\']?)?\)'

        def replace_env_var(match: Any) -> str:
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
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Added FLEXT config TODOs to: {file_path}")
            return True
        print(f"⏭️ No changes needed: {file_path}")
        return False

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def main() -> None:
    """Main consolidation function."""
    # Find files with manual env vars
    print("🔍 Finding files with manual environment variables...")
    env_var_files = find_manual_env_vars()

    if not env_var_files:
        print("✅ No manual environment variable usage found!")
        return

    print(f"📄 Found {len(env_var_files)} files with manual env vars")

    # Process first 50 files
    processed = 0
    modified = 0

    for file_path in env_var_files[:50]:
        if add_config_todos_to_file(file_path):
            modified += 1
        processed += 1

    print("\n✅ Configuration consolidation completed!")
    print(f"📊 Processed {processed} files, modified {modified}")
    print("📋 Next steps:")
    print("  1. Review TODO comments added to files")
    print("  2. Create FLEXT config classes for each project")
    print("  3. Replace manual patterns with centralized config")
    print("  4. Remove manual os.getenv() calls")


if __name__ == "__main__":
    main()
