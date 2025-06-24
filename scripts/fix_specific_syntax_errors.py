#!/usr/bin/env python
"""
Fix specific critical syntax errors preventing FLX imports.

Per CLAUDE.md RULE 4: Complete delivery with zero tolerance for violations.
"""

import re
from pathlib import Path


def fix_protocols_py():
    """Fix broken docstring in protocols.py."""
    file_path = Path("/home/marlonsc/pyauto/flx/src/flx/core/protocols.py")
    content = file_path.read_text()

    # Fix incomplete docstring - find the missing closing """
    if '"""' in content and content.count('"""') % 2 != 0:
        # Find the last line before 'from __future__' or 'import'
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if (
                line.strip().startswith("from __future__")
                or line.strip().startswith("import ")
                or line.strip().startswith("from typing")
            ):
                # Insert closing """ before this line
                lines.insert(i, '"""')
                break

        content = "\n".join(lines)
        file_path.write_text(content)


def fix_incomplete_docstrings():
    """Fix incomplete docstrings in various files."""
    base_path = Path("/home/marlonsc/pyauto/flx")

    # Files with known incomplete docstring issues
    files_to_fix = [
        "src/flx/core/protocols.py",
        "src/flx/adapters/inbound/__init__.py",
        "src/flx/core/ultra_base.py",
        "src/flx/adapters/outbound/configuration.py",
        "src/flx/adapters/observability/prometheus_metrics.py",
        "src/flx/adapters/mixins/behavioral/error_handling.py",
        "src/flx/infra/output/output_factory_impl.py",
        "src/flx/infra/cache/strategy_factory.py",
        "src/flx/infra/cache/cache_strategy_factory_impl.py",
        "src/flx/infra/database/session.py",
        "src/flx/infra/runtime/manager.py",
        "src/flx/infra/adapters/metrics_adapter.py",
        "src/flx/application/commands/app_handlers.py",
        "src/flx/application/commands/__init__.py",
        "src/flx/daemon/__main__.py",
        "tests/unit/core/test_base.py",
        "tests/unit/application/test_services.py",
        "tests/hexagonal/test_port_contracts.py",
        "scripts/utilities/utils/pdf_converter_advanced.py",
        "scripts/utilities/test_basic.py",
        "scripts/utilities/test_all_functionality.py",
        "scripts/quality_loop.py",
    ]

    fixed_files = []

    for file_rel_path in files_to_fix:
        file_path = base_path / file_rel_path
        if not file_path.exists():
            continue

        try:
            content = file_path.read_text()
            original_content = content

            # Fix 1: Incomplete docstrings (odd number of """)
            if '"""' in content and content.count('"""') % 2 != 0:
                lines = content.split("\n")

                # Find where to close the docstring
                in_docstring = False
                for i, line in enumerate(lines):
                    if '"""' in line:
                        in_docstring = not in_docstring
                    elif in_docstring and (
                        line.strip().startswith("from ")
                        or line.strip().startswith("import ")
                        or line.strip() == ""
                    ):
                        # Close docstring before this line
                        lines.insert(i, '"""')
                        break

                content = "\n".join(lines)

            # Fix 2: Remove duplicate typing imports
            content = re.sub(
                r"(from typing import [^\n]+)\n(from typing import [^\n]+)",
                r"\1",
                content,
            )

            # Fix 3: Remove isolated import sys
            lines = content.split("\n")
            filtered_lines = []
            for i, line in enumerate(lines):
                if (
                    line.strip() == "import sys"
                    and i > 0
                    and i < len(lines) - 1
                    and not lines[i - 1].strip().startswith("import")
                    and not lines[i - 1].strip().startswith("from")
                    and not lines[i + 1].strip().startswith("import")
                    and not lines[i + 1].strip().startswith("from")
                ):
                    continue  # Skip isolated import sys
                filtered_lines.append(line)

            content = "\n".join(filtered_lines)

            # Fix 4: Remove lines that are just broken fragments
            content = re.sub(
                r"^from typing import [^,\n]+(?:, [^,\n]+)*\nfrom typing import.*$",
                "from typing import Any, Dict, List, Optional",
                content,
                flags=re.MULTILINE,
            )

            if content != original_content:
                file_path.write_text(content)
                fixed_files.append(file_rel_path)

        except Exception:
            pass

    return fixed_files


def test_syntax():
    """Test basic FLX imports."""
    import subprocess

    try:
        result = subprocess.run(
            [
                "python",
                "-c",
                "import sys; sys.path.insert(0, '/home/marlonsc/pyauto/flx/src'); import flx; print('✅ FLX imports successfully')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return True
        return False
    except Exception:
        return False


if __name__ == "__main__":
    # Fix specific files
    fixed_files = fix_incomplete_docstrings()

    # Test if fixes worked
    success = test_syntax()

    # Log to token
    with open("/home/marlonsc/pyauto/.token", "a") as f:
        status = "SUCCESS" if success else "FAILED"
        f.write(
            f"FLX-SYNTAX-FIX-002 {status}: Fixed {len(fixed_files)} files, import test {status}\n"
        )
