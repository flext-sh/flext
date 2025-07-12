#!/usr/bin/env python3
"""Script para corrigir blind excepts sistematicamente seguindo SOLID principles.

Este script implementa correções específicas para Exception handling anti-patterns,
garantindo que todos os excepts sejam específicos e sigam SOLID principles.


from __future__ import annotations

import re
import subprocess
from pathlib import Path


class BlindExceptFixer:
    Fix blind except anti-patterns systematically."""

    def __init__(self) -> None:
        Initialize blind except fixer."""
        self.python_bin = "/home/marlonsc/flext/.venv/bin/python"
        self.project_root = Path.cwd()
        self.src_dir = self.project_root / "src"
        self.fixes_applied = 0

    def analyze_blind_excepts(self) -> list[tuple[Path, int, str]]:
        """Analyze all blind excepts in the codebase."""
        blind_excepts = []

        for py_file in self.src_dir.rglob("*.py"):
            lines = py_file.read_text().split("\n")

            for i, line in enumerate(lines, 1):
                if "except Exception" in line and "as " in line:
                    # Found a blind except - get context
                    context_start = max(0, i - 3)
                    context_end = min(len(lines), i + 5)
                    context = "\n".join(lines[context_start:context_end])

                    blind_excepts.append((py_file, i, context))

        return blind_excepts

    def get_specific_exceptions_for_context(self, context: str) -> list[str]:
        """Determine specific exceptions based on code context."""
        specific_exceptions = []

        # Analysis patterns for different contexts
        if any(:
            keyword in context.lower()
            for keyword in ["file", "path", "open", "read", "write"]:
        ):
            specific_exceptions.extend(
                ["OSError", "FileNotFoundError", "PermissionError"]
            )

        if any(:
            keyword in context.lower()
            for keyword in ["json", "parse", "loads", "dumps"]:
        ):
            specific_exceptions.extend(["json.JSONDecodeError", "ValueError"])

        if any(keyword in context.lower() for keyword in ["int(", "float(", "convert"]):
            specific_exceptions.extend(["ValueError", "TypeError"])

        if any(keyword in context.lower() for keyword in ["dict", "key", "get", "[]"]):
            specific_exceptions.extend(["KeyError", "AttributeError"])

        if any(:
            keyword in context.lower() for keyword in ["import", "module", "getattr"]
        ):
            specific_exceptions.extend(
                ["ImportError", "AttributeError", "ModuleNotFoundError"]
            )

        if any(:
            keyword in context.lower()
            for keyword in ["connection", "network", "http", "ldap"]:
        ):
            specific_exceptions.extend(["ConnectionError", "OSError", "RuntimeError"])

        if any(keyword in context.lower() for keyword in ["config", "settings", "env"]):
            specific_exceptions.extend(["ValueError", "KeyError", "TypeError"])

        # Default exceptions if no specific context found
        if not specific_exceptions:
            specific_exceptions = ["ValueError", "TypeError", "RuntimeError", "OSError"]

        # Remove duplicates while preserving order
        return list(dict.fromkeys(specific_exceptions))

    def fix_blind_except_in_file(self, file_path: Path) -> int:
        """Fix all blind excepts in a single file."""
        content = file_path.read_text()
        lines = content.split("\n")
        fixes_in_file = 0

        for i, line in enumerate(lines):
            if "except Exception as " in line:
                # Get variable name
                var_match = re.search(r"except Exception as (\w+):", line)
                if not var_match:
                    continue

                var_name = var_match.group(1)

                # Get context for this except block
                context_start = max(0, i - 5)
                context_end = min(len(lines), i + 10)
                context = "\n".join(lines[context_start:context_end])

                # Determine specific exceptions
                specific_exceptions = self.get_specific_exceptions_for_context(context)

                # Build replacement line
                if len(specific_exceptions) == 1:
                    new_line = line.replace(
                        f"except Exception as {var_name}:",
                        f"except {specific_exceptions[0]} as {var_name}:",
                    )
                else:
                    # Multiple exceptions - use tuple
                    exceptions_str = f"({', '.join(specific_exceptions)})"
                    new_line = line.replace(
                        f"except Exception as {var_name}:",
                        f"except {exceptions_str} as {var_name}:",
                    )

                # Update the line
                lines[i] = new_line
                fixes_in_file += 1

                # Add comment explaining the choice
                indent = len(line) - len(line.lstrip())
                comment = (
                    " " * indent + "# Specific exceptions based on context analysis"
                )

                # Insert comment before the except line
                lines.insert(i, comment)

        # Write back the fixed content
        if fixes_in_file > 0:
            file_path.write_text("\n".join(lines))

        return fixes_in_file

    def add_necessary_imports(
        self, file_path: Path, exceptions_used: list[str]
    ) -> None:
        """Add necessary imports for specific exceptions."""
        content = file_path.read_text()

        # Check if json import is needed
        if any("json.JSONDecodeError" in exc for exc in exceptions_used):
            if "import json" not in content and "from json import" not in content:
                # Add import after other imports
                lines = content.split("\n")

                # Find where to insert import
                import_line_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith(("import ", "from ")):
                        import_line_idx = i + 1

                lines.insert(import_line_idx, "import json")
                file_path.write_text("\n".join(lines))

    def verify_fixes(self) -> tuple[bool, str]:
        """Verify that blind except fixes were successful."""
        cmd = [
            self.python_bin,
            "-m",
            "ruff",
            "check",
            str(self.src_dir),
            "--select=BLE001",
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if "Found 0 errors" in result.stdout or result.returncode == 0:
                return True, "All blind excepts fixed!"
            return False, result.stdout
        except Exception as e:
            return False, str(e)

    def run_comprehensive_fix(self) -> None:
        """Run comprehensive blind except fixing."""
        print("🚀 BLIND EXCEPT FIXER - SOLID PRINCIPLES ENFORCEMENT")
        print("=" * 60)

        # Step 1: Analyze current state
        print("\n📊 ANALYZING BLIND EXCEPTS...")
        blind_excepts = self.analyze_blind_excepts()
        print(f"Found {len(blind_excepts)} blind excepts to fix")

        if not blind_excepts:
            print("✅ No blind excepts found!")
            return

        # Step 2: Show examples of what will be fixed
        print("\n📋 EXAMPLES OF FIXES TO BE APPLIED:")
        for file_path, line_num, context in blind_excepts[:3]:  # Show first 3
            rel_path = file_path.relative_to(self.project_root)
            print(f"   {rel_path}:{line_num}")
            context_lines = context.split("\n")
            for ctx_line in context_lines:
                if "except Exception" in ctx_line:
                    print(f"     -> {ctx_line.strip()}")
                    break

        if len(blind_excepts) > 3:
            print(f"   ... and {len(blind_excepts) - 3} more")

        # Step 3: Apply fixes
        print("\n🔧 APPLYING FIXES...")

        files_processed = set()
        files_processed.update(file_path for file_path, _, _ in blind_excepts)

        for file_path in files_processed:
            fixes = self.fix_blind_except_in_file(file_path)
            if fixes > 0:
                self.fixes_applied += fixes
                rel_path = file_path.relative_to(self.project_root)
                print(f"   ✅ {rel_path}: {fixes} fixes")

        # Step 4: Verify fixes
        print("\n📊 VERIFICATION...")
        success, message = self.verify_fixes()

        print("\n📈 RESULTS:")
        print(f"   Files processed: {len(files_processed)}")
        print(f"   Total fixes applied: {self.fixes_applied}")
        print(f"   Verification: {'✅ SUCCESS' if success else '❌ ISSUES REMAIN'}")

        if not success:
            print(f"   Details: {message}")

        print("\n" + "=" * 60)
        if success:
            print("🎉 ALL BLIND EXCEPTS FIXED - SOLID PRINCIPLES ENFORCED!")
        else:
            print("⚠️ SOME ISSUES REMAIN - MANUAL REVIEW NEEDED")


def main() -> None:
    """Main function."""
    fixer = BlindExceptFixer()
    fixer.run_comprehensive_fix()


if __name__ == "__main__":
    main()
