"""Type annotation fix module.

Adds missing type annotations to functions, variables, and class attributes.
"""

import ast
import re
from pathlib import Path

from .base import CustomFixModule, Issue


class TypeAnnotationFixModule(CustomFixModule):
    """Fix missing type annotations."""

    @property
    def name(self) -> str:
        return "Type Annotation Fixer"

    @property
    def description(self) -> str:
        return "Add missing type annotations to functions, variables, and classes"

    @property
    def category(self) -> str:
        return "type_safety"

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze file for missing type annotations."""
        issues: list = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues

        # Analyze AST
        for node in ast.walk(tree):
            # Check function definitions
            if isinstance(node, ast.FunctionDef):
                issues.extend(self._check_function(node, content))

            # Check variable assignments
            elif isinstance(node, ast.AnnAssign):
                issues.extend(self._check_variable(node, content))

        # Also check with regex for patterns AST might miss
        issues.extend(self._check_patterns(content))

        return issues

    def _check_function(self, node: ast.FunctionDef, content: str) -> list[Issue]:
        """Check function for missing annotations."""
        issues: list = []
        lines = content.split("\n")

        # Check return annotation
        if node.returns is None and node.name != "__init__":
            if node.lineno <= len(lines):
                issues.append(
                    Issue(
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Function '{node.name}' missing return type annotation",
                        severity="warning",
                        fix_description="Add return type annotation",
                        original_line=lines[node.lineno - 1],
                        fixed_line=self._add_return_type(
                            lines[node.lineno - 1],
                            node.name,
                        ),
                    ),
                )

        # Check parameter annotations
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != "self" and arg.arg != "cls":
                issues.append(
                    Issue(
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Parameter '{arg.arg}' missing type annotation",
                        severity="warning",
                        fix_description="Add parameter type annotation",
                    ),
                )

        return issues

    def _check_variable(self, node: ast.AnnAssign, content: str) -> list[Issue]:
        """Check variable assignments."""
        return []

        # AnnAssign already has annotation, so we look for regular assignments
        # This would be done in _check_patterns

    def _check_patterns(self, content: str) -> list[Issue]:
        """Check for patterns that need type annotations."""
        issues: list = []
        lines = content.split("\n")

        # Pattern: variable = []  (should be: variable: list = [])
        list_pattern = re.compile(r"^(\s*)(\w+)\s*=\s*\[\]")

        # Pattern: variable = {}  (should be: variable: dict = {})
        dict_pattern = re.compile(r"^(\s*)(\w+)\s*=\s*\{\}")

        # Pattern: variable = set()  (should be: variable: set = set())
        set_pattern = re.compile(r"^(\s*)(\w+)\s*=\s*set\(\)")

        for i, line in enumerate(lines, 1):
            # Check list pattern
            match = list_pattern.match(line)
            if match:
                indent, var_name = match.groups()
                issues.append(
                    Issue(
                        line=i,
                        message=f"Variable '{var_name}' should have type annotation",
                        severity="warning",
                        fix_description="Add list type annotation",
                        original_line=line,
                        fixed_line=f"{indent}{var_name}: list = []",
                    ),
                )

            # Check dict pattern
            match = dict_pattern.match(line)
            if match:
                indent, var_name = match.groups()
                issues.append(
                    Issue(
                        line=i,
                        message=f"Variable '{var_name}' should have type annotation",
                        severity="warning",
                        fix_description="Add dict type annotation",
                        original_line=line,
                        fixed_line=f"{indent}{var_name}: dict = {{}}",
                    ),
                )

            # Check set pattern
            match = set_pattern.match(line)
            if match:
                indent, var_name = match.groups()
                issues.append(
                    Issue(
                        line=i,
                        message=f"Variable '{var_name}' should have type annotation",
                        severity="warning",
                        fix_description="Add set type annotation",
                        original_line=line,
                        fixed_line=f"{indent}{var_name}: set = set()",
                    ),
                )

        return issues

    def _add_return_type(self, line: str, func_name: str) -> str:
        """Add return type to function definition."""
        # Simple heuristic - add -> None before the colon
        if " -> " not in line:
            # Find the closing parenthesis and colon
            match = re.search(r"\)\s*:", line)
            if match:
                return line[: match.start()] + ") -> None:" + line[match.end() :]
        return line

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply type annotation fixes."""
        lines = content.split("\n")

        # Sort issues by line number in reverse order to avoid offset issues
        sorted_issues = sorted(issues, key=lambda x: x.line, reverse=True)

        for issue in sorted_issues:
            if issue.fixed_line and 0 < issue.line <= len(lines):
                lines[issue.line - 1] = issue.fixed_line

        return "\n".join(lines)

    def validate_fixes(self, original: str, fixed: str) -> bool:
        """Validate that fixes maintain valid Python syntax."""
        if not super().validate_fixes(original, fixed):
            return False

        try:
            # Try to parse the fixed content
            ast.parse(fixed)
            return True
        except SyntaxError:
            return False


# Example usage and testing
if __name__ == "__main__":
    # Test code
    test_content = """
def calculate_total(items, tax_rate):
    total = 0
    for item in items:
        total += item.price
    return total * (1 + tax_rate)

class ShoppingCart:
    def __init__(self):
        self.items = []
        self.discounts = {}

    def add_item(self, item):
        self.items.append(item)

    def get_total(self):
        return sum(item.price for item in self.items)

empty_list: list = []
empty_dict: dict = {}
empty_set: set = set()
"""

    # Run fixer in dry-run mode
    fixer = TypeAnnotationFixModule(dry_run=True, verbose=True)

    # Create temporary file
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_content)
        temp_path = Path(f.name)

    # Process file
    result = fixer.process_file(temp_path)

    print(f"\nResult: {result}")
    if result.diff:
        print("\nDiff:")
        print(result.diff)

    # Cleanup
    temp_path.unlink()
