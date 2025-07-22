#!/usr/bin/env python3
"""Fix remaining import syntax errors."""

import re
import subprocess
from pathlib import Path

# Find files with the malformed import
result = subprocess.run(["grep", "-r", "-l", "import ServiceResult", "/home/marlonsc/flext", "--include=*.py"],
                       check=False, capture_output=True, text=True)

if result.returncode == 0:
    files = result.stdout.strip().split("\n")
    for file_path in files:
        if file_path:
            path = Path(file_path)
            try:
                content = path.read_text()
                # Fix the specific pattern
                fixed_content = re.sub(
                    r"from flext_core\.domain\.shared_types import import ServiceResult",
                    "from flext_core.domain.shared_types import ServiceResult",
                    content
                )
                if fixed_content != content:
                    path.write_text(fixed_content)
            except Exception:
                pass
else:
    pass
