#!/usr/bin/env python3
"""Script to fix TOML errors in pyproject.toml files."""
import re
from pathlib import Path


def fix_toml_file(file_path: Path):
    """Fix common TOML issues in pyproject.toml files."""
    if not file_path.exists():
        return False

    try:
        content = file_path.read_text()
        original_content = content

        # Fix 1: Remove duplicate [tool.ruff.lint.pydocstyle] sections
        # Keep only the first occurrence
        sections = re.findall(r"\[tool\.ruff\.lint\.pydocstyle\].*?(?=\[|\Z)", content, re.DOTALL)
        if len(sections) > 1:
            # Replace all occurrences after the first
            for i in range(1, len(sections)):
                content = content.replace(sections[i], "")

        # Fix 2: Remove duplicate sections and keys
        content = re.sub(r"\n\[tool\.ruff\.lint\.pydocstyle\]\s*\n(?=.*\[tool\.ruff\.lint\.pydocstyle\])", "\n", content, flags=re.DOTALL)
        content = re.sub(r"\n\[tool\.ruff\.lint\.flake8-tidy-imports\]\s*\n(?=.*\[tool\.ruff\.lint\.flake8-tidy-imports\])", "\n", content, flags=re.DOTALL)
        content = re.sub(r"\n\[tool\.ruff\.lint\.flake8-type-checking\]\s*\n(?=.*\[tool\.ruff\.lint\.flake8-type-checking\])", "\n", content, flags=re.DOTALL)
        content = re.sub(r"\n\[tool\.ruff\.lint\.pycodestyle\]\s*\n(?=.*\[tool\.ruff\.lint\.pycodestyle\])", "\n", content, flags=re.DOTALL)
        content = re.sub(r"\n\[tool\.ruff\.lint\.pylint\]\s*\n(?=.*\[tool\.ruff\.lint\.pylint\])", "\n", content, flags=re.DOTALL)
        content = re.sub(r"\n\[tool\.vulture\]\s*\n(?=.*\[tool\.vulture\])", "\n", content, flags=re.DOTALL)
        content = re.sub(r"\n\[tool\.radon\]\s*\n(?=.*\[tool\.radon\])", "\n", content, flags=re.DOTALL)

        # Fix 3: Handle malformed arrays (common TOML issue)
        # Fix trailing commas in arrays
        content = re.sub(r"(\[.*?),\s*\]", r"\1]", content, flags=re.DOTALL)

        # Fix 4: Remove empty lines between duplicate sections
        content = re.sub(r'\n\n+\[tool\.ruff\.lint\.pydocstyle\]\s*convention = "google"\s*\n\[tool\.ruff\.lint\.flake8-tidy-imports\]', '\n\n[tool.ruff.lint.pydocstyle]\nconvention = "google"\n\n[tool.ruff.lint.flake8-tidy-imports]', content)

        # Fix 5: Ensure proper section ordering and no duplicates
        tool_sections = {
            "pydocstyle": 'convention = "google"',
            "flake8-tidy-imports": 'ban-relative-imports = "all"',
            "flake8-type-checking": "strict = true",
            "pycodestyle": "max-doc-length = 88",
            "pylint": """max-args = 10
max-branches = 15
max-returns = 8
max-statements = 60""",
            "vulture": """min_confidence = 100
paths = ["src"]
exclude = ["tests/"]
ignore_decorators = ["@app.route", "@router.get", "@router.post"]
ignore_names = ["_*"]
make_whitelist = true
sort_by_size = true""",
            "radon": '''exclude = ["tests/*", "*/tests/*"]
ignore = ["F401"]  # Unused imports
total_average = true
show_complexity = true
average = true
order = "SCORE"'''
        }

        # Remove all existing tool sections that might be duplicated
        for section_name in tool_sections:
            pattern = rf"\[tool\.ruff\.lint\.{re.escape(section_name)}\].*?(?=\[|\Z)"
            content = re.sub(pattern, "", content, flags=re.DOTALL)
            pattern = rf"\[tool\.{re.escape(section_name)}\].*?(?=\[|\Z)"
            content = re.sub(pattern, "", content, flags=re.DOTALL)

        # Add the sections at the end if not present
        if "[tool.ruff.lint.pydocstyle]" not in content:
            content += f'\n\n[tool.ruff.lint.pydocstyle]\n{tool_sections["pydocstyle"]}\n'
        if "[tool.ruff.lint.flake8-tidy-imports]" not in content:
            content += f'\n[tool.ruff.lint.flake8-tidy-imports]\n{tool_sections["flake8-tidy-imports"]}\n'
        if "[tool.ruff.lint.flake8-type-checking]" not in content:
            content += f'\n[tool.ruff.lint.flake8-type-checking]\n{tool_sections["flake8-type-checking"]}\n'
        if "[tool.ruff.lint.pycodestyle]" not in content:
            content += f'\n[tool.ruff.lint.pycodestyle]\n{tool_sections["pycodestyle"]}\n'
        if "[tool.ruff.lint.pylint]" not in content:
            content += f'\n[tool.ruff.lint.pylint]\n{tool_sections["pylint"]}\n'
        if "[tool.vulture]" not in content:
            content += f'\n[tool.vulture]\n{tool_sections["vulture"]}\n'
        if "[tool.radon]" not in content:
            content += f'\n[tool.radon]\n{tool_sections["radon"]}\n'

        # Fix 6: Clean up multiple newlines
        content = re.sub(r"\n{3,}", "\n\n", content)

        # Write back if changed
        if content != original_content:
            file_path.write_text(content)
            return True
        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Fix all pyproject.toml files in the workspace."""
    workspace_root = Path("/home/marlonsc/flext")

    # Find all pyproject.toml files except in .venv and site-packages
    toml_files = [toml_file for toml_file in workspace_root.rglob("pyproject.toml") if ".venv" not in str(toml_file) and "site-packages" not in str(toml_file)]

    print(f"Found {len(toml_files)} pyproject.toml files to fix")

    fixed_count = 0
    for toml_file in toml_files:
        print(f"Fixing {toml_file}...")
        if fix_toml_file(toml_file):
            fixed_count += 1
            print(f"✅ Fixed {toml_file}")
        else:
            print(f"↪️ No changes needed for {toml_file}")

    print(f"\n🎉 Fixed {fixed_count} out of {len(toml_files)} files")


if __name__ == "__main__":
    main()
