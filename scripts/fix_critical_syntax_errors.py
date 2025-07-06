#!/usr/bin/env python3
"""
🚨 EMERGENCY SYNTAX ERROR FIXER - CRÍTICO
Script para corrigir os 1515 syntax errors imediatamente

PRIORIDADE MÁXIMA: Syntax errors impedem funcionamento
"""

import re
import subprocess
from pathlib import Path


class EmergencySyntaxFixer:
    """Corretor de syntax errors críticos."""

    def __init__(self, project_dir: str = "/home/marlonsc/flext/algar-oud-mig") -> None:
        self.project_dir = Path(project_dir)
        self.src_dir = self.project_dir / "src"
        self.fixes_applied = []

    def fix_all_critical_syntax_errors(self) -> None:
        """Aplicar correções urgentes de syntax error."""
        print("🚨 EMERGENCY: FIXING CRITICAL SYNTAX ERRORS")
        print(f"📁 Project: {self.project_dir}")

        # Phase 1: Fix missing newlines at end of files
        self._fix_missing_newlines()

        # Phase 2: Fix function signature errors
        self._fix_function_signature_errors()

        # Phase 3: Fix missing colons
        self._fix_missing_colons()

        # Phase 4: Fix unclosed parentheses/brackets
        self._fix_unclosed_constructs()

        # Phase 5: Fix invalid indentation
        self._fix_indentation_errors()

        # Phase 6: Fix specific syntax patterns
        self._fix_specific_syntax_patterns()

        # Report and verify
        self._verify_syntax_fixes()

    def _fix_missing_newlines(self) -> None:
        """Fix missing newlines at end of files."""
        print("\n🔧 FIXING MISSING NEWLINES")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")

            if not content.endswith("\n"):
                py_file.write_text(content + "\n", encoding="utf-8")
                self.fixes_applied.append(f"Added newline: {py_file.name}")
                print(f"✅ Added newline to {py_file.name}")

    def _fix_function_signature_errors(self) -> None:
        """Fix broken function signatures."""
        print("\n🔧 FIXING FUNCTION SIGNATURE ERRORS")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Fix broken function definitions
            patterns = [
                # Pattern: _normalize_entry_attributes(\n        self,
                (r"(\w+)\(\s*\n\s+self,", r"\1(self,"),
                # Pattern: def function(\n        args
                (r"def\s+(\w+)\(\s*\n\s+", r"def \1("),
                # Pattern: function(\n        args) -> type:
                (r"(\w+)\(\s*\n\s+([^)]+)\)", r"\1(\2)"),
                # Pattern: broken line continuations in function calls
                (r"\(\s*\n\s+([^)]+)\s*\n\s*\)", r"(\1)"),
            ]

            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    content = new_content
                    self.fixes_applied.append(
                        f"Fixed function signature: {py_file.name}"
                    )

            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                print(f"✅ Fixed function signatures in {py_file.name}")

    def _fix_missing_colons(self) -> None:
        """Fix missing colons in control structures."""
        print("\n🔧 FIXING MISSING COLONS")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Patterns for missing colons
            patterns = [
                # if/elif/else without colon
                (r"\b(if|elif|else)\s+([^:\n]+)\s*\n", r"\1 \2:\n"),
                # for/while without colon
                (r"\b(for|while)\s+([^:\n]+)\s*\n", r"\1 \2:\n"),
                # try/except/finally without colon
                (r"\b(try|except|finally)\s*([^:\n]*)\s*\n", r"\1\2:\n"),
                # function def without colon
                (r"\bdef\s+\w+\([^)]*\)\s*(->\s*[^:\n]+)?\s*\n", r"\g<0>:"),
                # class without colon
                (r"\bclass\s+\w+[^:\n]*\s*\n", r"\g<0>:"),
            ]

            for pattern, replacement in patterns:
                # Be careful not to add double colons
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    content = new_content
                    self.fixes_applied.append(f"Fixed missing colon: {py_file.name}")

            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                print(f"✅ Fixed missing colons in {py_file.name}")

    def _fix_unclosed_constructs(self) -> None:
        """Fix unclosed parentheses, brackets, etc."""
        print("\n🔧 FIXING UNCLOSED CONSTRUCTS")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Balance parentheses, brackets, braces
            content = self._balance_constructs(content)

            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                self.fixes_applied.append(f"Balanced constructs: {py_file.name}")
                print(f"✅ Balanced constructs in {py_file.name}")

    def _balance_constructs(self, content: str) -> str:
        """Balance parentheses, brackets, and braces."""
        lines = content.split("\n")
        balanced_lines = []

        for line in lines:
            # Count unbalanced constructs
            paren_balance = line.count("(") - line.count(")")
            bracket_balance = line.count("[") - line.count("]")
            brace_balance = line.count("{") - line.count("}")

            balanced_line = line

            # Add missing closing constructs at end of line if needed
            if paren_balance > 0:
                balanced_line += ")" * paren_balance
            elif paren_balance < 0:
                balanced_line = "(" * abs(paren_balance) + balanced_line

            if bracket_balance > 0:
                balanced_line += "]" * bracket_balance
            elif bracket_balance < 0:
                balanced_line = "[" * abs(bracket_balance) + balanced_line

            if brace_balance > 0:
                balanced_line += "}" * brace_balance
            elif brace_balance < 0:
                balanced_line = "{" * abs(brace_balance) + balanced_line

            balanced_lines.append(balanced_line)

        return "\n".join(balanced_lines)

    def _fix_indentation_errors(self) -> None:
        """Fix obvious indentation errors."""
        print("\n🔧 FIXING INDENTATION ERRORS")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            lines = content.split("\n")
            fixed_lines = []

            for i, line in enumerate(lines):
                # Fix obvious indentation issues
                if (
                    line.strip()
                    and not line.startswith(" ")
                    and not line.startswith("\t")
                ):
                    # Check if this should be indented (follows colon)
                    if i > 0 and lines[i - 1].rstrip().endswith(":"):
                        if line.strip():  # Not empty line
                            line = "    " + line  # Add 4-space indent

                fixed_lines.append(line)

            content = "\n".join(fixed_lines)

            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                self.fixes_applied.append(f"Fixed indentation: {py_file.name}")
                print(f"✅ Fixed indentation in {py_file.name}")

    def _fix_specific_syntax_patterns(self) -> None:
        """Fix specific syntax patterns found in the codebase."""
        print("\n🔧 FIXING SPECIFIC SYNTAX PATTERNS")

        for py_file in self.src_dir.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8")
            original_content = content

            # Specific fixes based on common patterns
            fixes = [
                # Fix "def _normalize_entry_attributes(\n        self," pattern
                (r"def\s+(\w+)\(\s*\n\s+self,", r"def \1(self,"),
                # Fix broken return type annotations
                (r"\)\s*->\s*\n\s+([^:\n]+):", r") -> \1:"),
                # Fix broken assignments
                (r"(\w+)\s*=\s*\n\s+", r"\1 = "),
                # Fix broken imports
                (r"from\s+(\w+)\s+import\s*\n\s+", r"from \1 import "),
                # Fix broken function calls
                (r"(\w+)\(\s*\n\s+([^)]+)\s*\n\s*\)", r"\1(\2)"),
                # Fix method chaining breaks
                (r"\.\s*\n\s+(\w+)", r".\1"),
            ]

            for pattern, replacement in fixes:
                new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                if new_content != content:
                    content = new_content
                    self.fixes_applied.append(f"Fixed syntax pattern: {py_file.name}")

            if content != original_content:
                py_file.write_text(content, encoding="utf-8")
                print(f"✅ Fixed syntax patterns in {py_file.name}")

    def _verify_syntax_fixes(self) -> None:
        """Verify syntax fixes by running Python syntax check."""
        print("\n🔍 VERIFYING SYNTAX FIXES")

        syntax_errors = []

        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    compile(f.read(), py_file, "exec")
            except SyntaxError as e:
                syntax_errors.append(f"{py_file.name}:{e.lineno}: {e.msg}")

        if syntax_errors:
            print(f"⚠️  REMAINING SYNTAX ERRORS: {len(syntax_errors)}")
            for error in syntax_errors[:10]:  # Show first 10
                print(f"   {error}")
            if len(syntax_errors) > 10:
                print(f"   ... and {len(syntax_errors) - 10} more")
        else:
            print("✅ NO SYNTAX ERRORS FOUND!")

        # Run ruff check to see current status
        print("\n📊 FINAL RUFF STATUS:")
        result = subprocess.run(
            [
                "ruff",
                "check",
                str(self.src_dir),
                "--select=E9,F9",  # Only syntax errors
                "--statistics",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=self.project_dir,
        )

        if result.stdout:
            print(result.stdout)
        else:
            print("✅ No critical syntax errors reported by ruff!")

        print(f"\n🎯 FIXES APPLIED: {len(self.fixes_applied)}")

        # Group fixes by type
        fix_types = {}
        for fix in self.fixes_applied:
            fix_type = fix.split(":")[0]
            fix_types[fix_type] = fix_types.get(fix_type, 0) + 1

        for fix_type, count in sorted(fix_types.items()):
            print(f"   - {fix_type}: {count} fixes")


def main() -> None:
    """Execute emergency syntax error fixing."""
    fixer = EmergencySyntaxFixer()
    fixer.fix_all_critical_syntax_errors()


if __name__ == "__main__":
    main()
