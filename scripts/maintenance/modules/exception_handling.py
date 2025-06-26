"""Exception handling fix module.

Fixes common exception handling anti-patterns:
- Bare except clauses
- Too broad exception catching
- Missing 'from' in exception chaining
- Empty except blocks
- Using assert for error handling
"""

import ast
import re
from pathlib import Path

from .base import CustomFixModule, Issue


class ExceptionHandlingFixModule(CustomFixModule):
    """Fix exception handling anti-patterns."""

    @property
    def name(self) -> str:
        return "Exception Handling Fixer"

    @property
    def description(self) -> str:
        return "Fix bare except, add exception chaining, and improve error handling"

    @property
    def category(self) -> str:
        return "error_handling"

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze file for exception handling issues."""
        issues: list = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues

        # Use AST visitor for complex analysis
        visitor = ExceptionVisitor()
        visitor.visit(tree)

        lines = content.split("\n")

        # Convert AST findings to issues
        for finding in visitor.findings:
            issue = self._create_issue_from_finding(finding, lines)
            if issue:
                issues.append(issue)

        # Also check with regex for patterns AST might miss
        issues.extend(self._check_regex_patterns(lines))

        return issues

    def _create_issue_from_finding(
        self, finding: dict, lines: list[str],
    ) -> Issue | None:
        """Create an Issue from an AST finding."""
        line_num = finding["line"]
        issue_type = finding["type"]

        if line_num > len(lines):
            return None

        original_line = lines[line_num - 1]

        if issue_type == "bare_except":
            return Issue(
                line=line_num,
                message="Bare except clause - catch specific exceptions",
                severity="error",
                fix_description="Replace with 'except Exception:'",
                original_line=original_line,
                fixed_line=original_line.replace("except:", "except Exception:"),
            )

        if issue_type == "broad_except":
            return Issue(
                line=line_num,
                message="Catching Exception is too broad",
                severity="warning",
                fix_description="Consider catching more specific exceptions",
                original_line=original_line,
            )

        if issue_type == "empty_except":
            return Issue(
                line=line_num,
                message="Empty except block - add proper error handling",
                severity="error",
                fix_description="Add logging or error handling",
                original_line=original_line,
            )

        if issue_type == "missing_from":
            # Check if we're in an except block and raising
            return Issue(
                line=line_num,
                message="Exception chaining missing 'from'",
                severity="warning",
                fix_description="Add 'from e' to preserve traceback",
                original_line=original_line,
                fixed_line=self._add_from_clause(original_line),
            )

        return None

    def _check_regex_patterns(self, lines: list[str]) -> list[Issue]:
        """Check for patterns using regex."""
        issues: list = []

        # Pattern 1: assert used for validation (should be proper exception)
        assert_pattern = re.compile(r'^\s*assert\s+([^,]+),\s*["\']([^"\']+)["\']')

        # Pattern 2: raise without message
        bare_raise_pattern = re.compile(r"^\s*raise\s+(\w+)\s*\(\s*\)")

        # Pattern 3: except with multiple exceptions not in tuple
        multi_except_pattern = re.compile(r"^\s*except\s+(\w+)\s*,\s*(\w+)")

        in_except_block = False
        except_var = None

        for i, line in enumerate(lines, 1):
            # Track if we're in an except block
            if re.match(r"^\s*except\s+.*as\s+(\w+)", line):
                match = re.match(r"^\s*except\s+.*as\s+(\w+)", line)
                in_except_block = True
                except_var = match.group(1) if match else "e"
            elif re.match(r"^\s*except", line):
                in_except_block = True
                except_var = "e"
            elif not line.strip().startswith(" ") and line.strip():
                in_except_block = False
                except_var = None

            # Check assert pattern
            match = assert_pattern.match(line)
            if match:
                condition, message = match.groups()
                indent = len(line) - len(line.lstrip())
                fixed_line = f"{' ' * indent}if not {condition}:\n{
                    ' ' * (indent + 4)
                }raise ValueError('{message}')"

                issues.append(
                    Issue(
                        line=i,
                        message="assert used for validation - use proper exception",
                        severity="warning",
                        fix_description="Replace with if/raise pattern",
                        original_line=line,
                        fixed_line=fixed_line.split("\n")[0],  # Just show first line
                    ),
                )

            # Check bare raise
            match = bare_raise_pattern.match(line)
            if match:
                exception_type = match.group(1)
                issues.append(
                    Issue(
                        line=i,
                        message=f"Raise {exception_type} without message",
                        severity="warning",
                        fix_description="Add descriptive error message",
                        original_line=line,
                    ),
                )

            # Check multiple exceptions
            match = multi_except_pattern.match(line)
            if match:
                exc1, exc2 = match.groups()
                fixed_line = line.replace(f"{exc1}, {exc2}", f"({exc1}, {exc2})")

                issues.append(
                    Issue(
                        line=i,
                        message="Multiple exceptions should be in parentheses",
                        severity="error",
                        fix_description="Add parentheses around exception tuple",
                        original_line=line,
                        fixed_line=fixed_line,
                    ),
                )

            # Check for raise in except without from
            if (
                in_except_block
                and re.match(r"^\s*raise\s+\w+\(", line)
                and " from " not in line
            ):
                fixed_line = line.rstrip()
                if except_var:
                    fixed_line += f" from {except_var}"
                    fixed_line += " from e"

                issues.append(
                    Issue(
                        line=i,
                        message="Exception chaining missing 'from'",
                        severity="warning",
                        fix_description="Add 'from' clause for better tracebacks",
                        original_line=line,
                        fixed_line=fixed_line,
                    ),
                )

        return issues

    def _add_from_clause(self, line: str) -> str:
        """Add 'from e' to a raise statement."""
        if " from " in line:
            return line

        # Find the end of the raise statement
        if line.rstrip().endswith(")"):
            return line.rstrip() + " from e"
        return line

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply exception handling fixes."""
        lines = content.split("\n")

        # Sort issues by line number in reverse order
        sorted_issues = sorted(issues, key=lambda x: x.line, reverse=True)

        # Track multi-line fixes
        multi_line_fixes: list = []

        for issue in sorted_issues:
            if issue.fixed_line and 0 < issue.line <= len(lines):
                # Handle multi-line fixes (like assert replacement)
                if "\n" in issue.fixed_line:
                    multi_line_fixes.append((issue.line, issue.fixed_line))
                    lines[issue.line - 1] = issue.fixed_line

        # Apply multi-line fixes
        for line_num, fixed_content in multi_line_fixes:
            if "assert" in lines[line_num - 1]:
                # Replace assert with if/raise
                new_lines = fixed_content.split("\n")
                lines[line_num - 1 : line_num] = new_lines

        return "\n".join(lines)

    def validate_fixes(self, original: str, fixed: str) -> bool:
        """Validate exception handling fixes."""
        if not super().validate_fixes(original, fixed):
            return False

        try:
            # Parse to ensure valid Python
            ast.parse(fixed)

            # Additional validation
            # Ensure no bare excepts remain
            if re.search(r"^\s*except\s*:", fixed, re.MULTILINE):
                return False

            return True
        except SyntaxError:
            return False


class ExceptionVisitor(ast.NodeVisitor):
    """AST visitor to find exception handling issues."""

    def __init__(self):
        self.findings = []
        self.in_except = False
        self.except_var = None

    def visit_except_handler(self, node) -> None:
        """Visit except handlers."""
        old_in_except = self.in_except
        old_except_var = self.except_var

        self.in_except = True
        self.except_var = node.name if node.name else "e"

        # Check for bare except
        if node.type is None:
            self.findings.append({"type": "bare_except", "line": node.lineno})

        # Check for broad except
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            self.findings.append({"type": "broad_except", "line": node.lineno})

        # Check for empty except body
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.findings.append({"type": "empty_except", "line": node.lineno})

        self.generic_visit(node)

        self.in_except = old_in_except
        self.except_var = old_except_var

    def visit_raise(self, node) -> None:
        """Visit raise statements."""
        if self.in_except and node.exc and not node.cause:
            # Raising new exception in except without 'from'
            self.findings.append({"type": "missing_from", "line": node.lineno})

        self.generic_visit(node)


# Testing
if __name__ == "__main__":
    test_content = """
def risky_operation(data):
    try:
        # Bare except
        result = process(data)
    except:
        print("Error occurred")

    try:
        # Too broad
        validate(data)
    except Exception:
        pass  # Empty except

    try:
        # Multiple exceptions wrong syntax
        parse(data)
    except ValueError, TypeError:
        print("Parse error")

    try:
        # Missing from clause
        dangerous_op()
    except IOError as e:
        raise RuntimeError("Operation failed")

    # Assert for validation
    assert len(data) > 0, "Data cannot be empty"

    # Bare raise
    if not data:
        raise ValueError()
"""

    fixer = ExceptionHandlingFixModule(dry_run=True, verbose=True)

    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_content)
        temp_path = Path(f.name)

    result = fixer.process_file(temp_path)

    print(f"\nResult: {result}")
    if result.diff:
        print("\nDiff:")
        print(result.diff)

    temp_path.unlink()
