import sys
import os

FILES = [
    "flext-core/src/flext_core/_decorators/__init__.py",
    "flext-core/src/flext_core/_dispatcher/__init__.py",
    "flext-core/src/flext_core/_dispatcher/reliability.py",
    "flext-core/src/flext_core/_dispatcher/timeout.py",
    "flext-core/src/flext_core/_utilities/cast.py",
    "flext-core/src/flext_core/_utilities/checker.py",
    "flext-core/src/flext_core/_utilities/collection.py",
    "flext-core/src/flext_core/_utilities/conversion.py",
    "flext-core/src/flext_core/_utilities/_deprecation_helpers.py",
    "flext-core/src/flext_core/_utilities/deprecation.py",
    "flext-core/src/flext_core/_utilities/domain.py",
    "flext-core/src/flext_core/_utilities/guards.py",
    "flext-core/src/flext_core/_utilities/__init__.py",
    "flext-core/src/flext_core/_utilities/pagination.py",
    "flext-core/src/flext_core/_utilities/pattern.py",
    "flext-core/src/flext_core/_utilities/reliability.py",
    "flext-core/src/flext_core/_utilities/text.py",
    "flext-core/src/flext_core/_utilities/generators.py",  # Added generators.py
]

IMPORT_LINE = "from flext_core.models import m"


def fix_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, "r") as f:
        lines = f.readlines()

    if any(IMPORT_LINE in line for line in lines):
        return

    # Insert after last import
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i

    lines.insert(last_import_idx + 1, IMPORT_LINE + "\n")

    with open(filepath, "w") as f:
        f.writelines(lines)
    print(f"Fixed: {filepath}")


for f in FILES:
    fix_file(f)
