# Owner-Skill: .claude/skills/scripts-architecture/SKILL.md
import pathlib
import sys

FILES = [
    "flext-core/examples/04_config_basics.py",
    "flext-core/examples/05_utilities_advanced.py",
    "flext-core/examples/06_decorators_complete.py",
    "flext-core/examples/09_context_management.py",
    "flext-core/examples/12_utilities_comprehensive.py",
]

BAD_LINE = "from flext_core.models import m"


def fix(filepath) -> None:
    if not pathlib.Path(filepath).exists():
        return
    with pathlib.Path(filepath).open("r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    import_added = False

    # Check if we have the bad line inside a block
    # Logic: If we see 'from flext_core import (', we insert BEFORE it.
    # And we skip the BAD_LINE if encountered later.

    for line in lines:
        if line.strip() == BAD_LINE.strip():
            continue  # Skip the bad insertion

        if "from flext_core import (" in line and not import_added:
            new_lines.append(BAD_LINE + "\n")
            import_added = True

        new_lines.append(line)

    with pathlib.Path(filepath).open("w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"Fixed {filepath}")


def main() -> int:
    for f in FILES:
        fix(f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
