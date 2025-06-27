"""Asyncio pattern fix module.

Fixes common asyncio anti-patterns:
- asyncio.run() in loops or async contexts
- time.sleep() in async functions
- Blocking I/O in async functions
- Missing await keywords
- Synchronous context managers in async code
"""

import ast
import re
from pathlib import Path

from .base import CustomFixModule, Issue


class AsyncioPatternFixModule(CustomFixModule):
    """Fix asyncio anti-patterns."""

    @property
    def name(self) -> str:
        return "Asyncio Pattern Fixer"

    @property
    def description(self) -> str:
        return "Fix asyncio anti-patterns like asyncio.run() in loops and blocking calls in async"

    @property
    def category(self) -> str:
        return "async_patterns"

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze file for asyncio issues."""
        issues: list = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return issues

        # Use AST visitor
        visitor = AsyncVisitor()
        visitor.visit(tree)

        lines = content.split("\n")

        # Convert findings to issues
        for finding in visitor.findings:
            issue = self._create_issue_from_finding(finding, lines)
            if issue:
                issues.append(issue)

        # Additional regex checks
        issues.extend(self._check_regex_patterns(lines))

        return issues

    def _create_issue_from_finding(
        self,
        finding: dict,
        lines: list[str],
    ) -> Issue | None:
        """Create Issue from AST finding."""
        line_num = finding["line"]
        issue_type = finding["type"]

        if line_num > len(lines):
            return None

        original_line = lines[line_num - 1]

        if issue_type == "asyncio_run_in_loop":
            return Issue(
                line=line_num,
                message="asyncio.run() called inside loop - creates new event loop each time",
                severity="error",
                fix_description="Move asyncio.run() outside loop or use await",
                original_line=original_line,
            )

        if issue_type == "time_sleep_in_async":
            fixed_line = original_line.replace("time.sleep(", "await asyncio.sleep(")
            return Issue(
                line=line_num,
                message="time.sleep() blocks the event loop in async function",
                severity="error",
                fix_description="Use await asyncio.sleep() instead",
                original_line=original_line,
                fixed_line=fixed_line,
            )

        if issue_type == "sync_open_in_async":
            # Extract file operation
            len(original_line) - len(original_line.lstrip())
            if "open(" in original_line:
                return Issue(
                    line=line_num,
                    message="Synchronous file I/O in async function",
                    severity="warning",
                    fix_description="Use aiofiles for async file operations",
                    original_line=original_line,
                )

        elif issue_type == "missing_await":
            # Add await to coroutine call
            fixed_line = re.sub(r"(\s*)([a-zA-Z_]\w*\()", r"\1await \2", original_line)
            return Issue(
                line=line_num,
                message=f"Coroutine '{
                    finding.get('name', 'unknown')
                }' called without await",
                severity="error",
                fix_description="Add await keyword",
                original_line=original_line,
                fixed_line=fixed_line,
            )

        elif issue_type == "blocking_io":
            return Issue(
                line=line_num,
                message="Potentially blocking I/O operation in async function",
                severity="warning",
                fix_description="Use async version or run_in_executor",
                original_line=original_line,
            )

        return None

    def _check_regex_patterns(self, lines: list[str]) -> list[Issue]:
        """Check patterns with regex."""
        issues: list = []

        # Track if we're in an async function
        in_async_func = False
        func_indent = 0

        # Pattern for asyncio.create_task without await
        task_pattern = re.compile(r"^\s*asyncio\.create_task\(")

        # Pattern for synchronous requests in async
        requests_pattern = re.compile(r"requests\.(get|post|put|delete|patch)")

        # Pattern for threading in async
        threading_pattern = re.compile(r"threading\.(Thread|Lock|Event)")

        for i, line in enumerate(lines, 1):
            # Track async function context
            if re.match(r"^(\s*)async\s+def\s+", line):
                in_async_func = True
                func_indent = len(line) - len(line.lstrip())
            elif (
                in_async_func
                and line.strip()
                and len(line) - len(line.lstrip()) <= func_indent
            ):
                if not line.lstrip().startswith((" ", "\t")):
                    in_async_func = False

            # Check for create_task without assignment
            if task_pattern.match(line) and "=" not in line:
                issues.append(
                    Issue(
                        line=i,
                        message="asyncio.create_task() result not stored - task may be garbage collected",
                        severity="warning",
                        fix_description="Store task reference: task = asyncio.create_task(...)",
                        original_line=line,
                    ),
                )

            # Check for synchronous requests in async
            if in_async_func and requests_pattern.search(line):
                issues.append(
                    Issue(
                        line=i,
                        message="Synchronous requests library used in async function",
                        severity="error",
                        fix_description="Use aiohttp or httpx for async HTTP requests",
                        original_line=line,
                    ),
                )

            # Check for threading in async
            if in_async_func and threading_pattern.search(line):
                issues.append(
                    Issue(
                        line=i,
                        message="Threading used in async function - use asyncio primitives",
                        severity="warning",
                        fix_description="Use asyncio.Lock, asyncio.Event, etc.",
                        original_line=line,
                    ),
                )

            # Check for loop.run_until_complete in async
            if in_async_func and "run_until_complete" in line:
                issues.append(
                    Issue(
                        line=i,
                        message="run_until_complete() in async function - use await instead",
                        severity="error",
                        fix_description="Replace with await",
                        original_line=line,
                    ),
                )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply asyncio fixes."""
        lines = content.split("\n")

        # Check if we need asyncio import
        needs_asyncio = any(
            "asyncio.sleep" in issue.fixed_line for issue in issues if issue.fixed_line
        )

        # Sort issues by line number in reverse
        sorted_issues = sorted(issues, key=lambda x: x.line, reverse=True)

        for issue in sorted_issues:
            if issue.fixed_line and 0 < issue.line <= len(lines):
                lines[issue.line - 1] = issue.fixed_line

        # Add asyncio import if needed
        if needs_asyncio and "import asyncio" not in "\n".join(lines):
            # Find appropriate place for import
            import_added = False
            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    # Add after last import
                    continue
                if import_added:
                    break
                lines.insert(i, "import asyncio")
                import_added = True
                break

            if not import_added:
                lines.insert(0, "import asyncio")

        return "\n".join(lines)

    def validate_fixes(self, original: str, fixed: str) -> bool:
        """Validate asyncio fixes."""
        if not super().validate_fixes(original, fixed):
            return False

        try:
            # Parse to ensure valid syntax
            ast.parse(fixed)

            # Check for common issues
            # No asyncio.run in loops
            lines = fixed.split("\n")
            for i, line in enumerate(lines):
                if "asyncio.run(" in line:
                    # Check if in a loop (simple heuristic)
                    for j in range(max(0, i - 5), i):
                        if re.match(r"^\s*(for|while)\s+", lines[j]):
                            return False

            return True
        except SyntaxError:
            return False


class AsyncVisitor(ast.NodeVisitor):
    """AST visitor for asyncio pattern detection."""

    def __init__(self):
        self.findings = []
        self.in_async_func = False
        self.in_loop = False
        self.async_funcs = set()

    def visit_AsyncFunctionDef(self, node) -> None:
        """Visit async function definitions."""
        old_in_async = self.in_async_func
        self.in_async_func = True
        self.async_funcs.add(node.name)

        self.generic_visit(node)

        self.in_async_func = old_in_async

    def visit_For(self, node) -> None:
        """Visit for loops."""
        old_in_loop = self.in_loop
        self.in_loop = True

        self.generic_visit(node)

        self.in_loop = old_in_loop

    def visit_While(self, node) -> None:
        """Visit while loops."""
        old_in_loop = self.in_loop
        self.in_loop = True

        self.generic_visit(node)

        self.in_loop = old_in_loop

    def visit_Call(self, node) -> None:
        """Visit function calls."""
        # Check for asyncio.run in loops
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "asyncio"
            and node.func.attr == "run"
            and self.in_loop
        ):
            self.findings.append({"type": "asyncio_run_in_loop", "line": node.lineno})

        # Check for time.sleep in async
        if (
            self.in_async_func
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "time"
            and node.func.attr == "sleep"
        ):
            self.findings.append({"type": "time_sleep_in_async", "line": node.lineno})

        # Check for sync open() in async
        if (
            self.in_async_func
            and isinstance(node.func, ast.Name)
            and node.func.id == "open"
        ):
            self.findings.append({"type": "sync_open_in_async", "line": node.lineno})

        # Check for missing await on coroutines
        if (
            self.in_async_func
            and isinstance(node.func, ast.Name)
            and node.func.id in self.async_funcs
        ):
            # Check if this call is already awaited
            # This is simplified - real implementation would check parent
            self.findings.append(
                {"type": "missing_await", "line": node.lineno, "name": node.func.id},
            )

        # Check for blocking operations
        blocking_funcs = {"input", "sleep", "subprocess.run", "os.system"}
        if (
            self.in_async_func
            and isinstance(node.func, ast.Name)
            and node.func.id in blocking_funcs
        ):
            self.findings.append({"type": "blocking_io", "line": node.lineno})

        self.generic_visit(node)


# Testing
if __name__ == "__main__":
    test_content = """
import time
import asyncio
import requests

async def process_items(items):
    # asyncio.run in loop
    for item in items:
        result = asyncio.run(fetch_data(item))
        print(result)

    # time.sleep in async
    print("Waiting...")
    time.sleep(5)

    # Sync I/O in async
    with open('data.txt') as f:
        data = f.read()

    # Missing await
    process_item(data)

    # Sync requests in async
    response = requests.get('https://api.example.com')

    # Create task without storing
    asyncio.create_task(background_job())

async def fetch_data(item):
    return f"Data for {item}"

async def process_item(data):
    await asyncio.sleep(1)
    return data

async def background_job():
    while True:
        await asyncio.sleep(60)
"""

    fixer = AsyncioPatternFixModule(dry_run=True, verbose=True)

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
