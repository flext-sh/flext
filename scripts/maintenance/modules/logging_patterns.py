"""
Logging pattern fix module.

Fixes common logging anti-patterns:
- f-strings in logging calls
- print() statements that should be logger calls
- Incorrect log level usage
- Missing logger initialization
"""

import ast
import re
from pathlib import Path

from .base import CustomFixModule, Issue


class LoggingPatternFixModule(CustomFixModule):
    """Fix logging anti-patterns."""

    @property
    def name(self) -> str:
        return "Logging Pattern Fixer"

    @property
    def description(self) -> str:
        return "Fix f-strings in logging, replace print statements, and improve logging patterns"

    @property
    def category(self) -> str:
        return "logging"

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze file for logging issues."""
        issues: list = []
        lines = content.split("\n")

        # Check for logger presence
        has_logger = self._has_logger(content)

        # Pattern 1: f-strings in logging
        issues.extend(self._check_fstring_logging(lines))

        # Pattern 2: print statements
        issues.extend(self._check_print_statements(lines, has_logger))

        # Pattern 3: % formatting in logging (should use lazy formatting)
        issues.extend(self._check_percent_formatting(lines))

        # Pattern 4: .format() in logging
        issues.extend(self._check_format_logging(lines))

        # Pattern 5: Wrong log levels
        issues.extend(self._check_log_levels(lines))

        return issues

    def _has_logger(self, content: str) -> bool:
        """Check if file has logger defined."""
        patterns = [
            r"logger\s*=\s*logging\.getLogger",
            r"from\s+.*\s+import\s+.*logger",
            r"import\s+logging",
        ]
        return any(re.search(pattern, content) for pattern in patterns)

    def _check_fstring_logging(self, lines: list[str]) -> list[Issue]:
        """Check for f-strings in logging calls."""
        issues: list = []

        # Pattern: logger.method(f"...") or logger.method(f'...')
        fstring_pattern = re.compile(
            r'(logger|logging|log)\.(debug|info|warning|error|critical)\s*\(\s*f["\']([^"\']*)["\']([^)]*)\)'
        )

        for i, line in enumerate(lines, 1):
            match = fstring_pattern.search(line)
            if match:
                logger_obj, level, message, rest = match.groups()

                # Extract variables from f-string
                variables = re.findall(r"\{([^}]+)\}", message)

                # Create fixed version with lazy formatting
                fixed_message = re.sub(r"\{[^}]+\}", "%s", message)
                if variables:
                    var_args = ", ".join(variables)
                    fixed_line = line.replace(
                        match.group(0),
                        f'{logger_obj}.{level}("{fixed_message}", {var_args}{rest})',
                    )
                    fixed_line = line.replace('f"', '"').replace("f'", "'")

                issues.append(
                    Issue(
                        line=i,
                        message=f"F-string used in {level} logging call",
                        severity="warning",
                        fix_description="Use lazy formatting instead",
                        original_line=line,
                        fixed_line=fixed_line,
                    )
                )

        return issues

    def _check_print_statements(
        self, lines: list[str], has_logger: bool
    ) -> list[Issue]:
        """Check for print statements that should be logger calls."""
        issues: list = []

        print_pattern = re.compile(r"^\s*print\s*\((.+)\)\s*$")

        for i, line in enumerate(lines, 1):
            match = print_pattern.match(line)
            if match:
                content = match.group(1)

                # Determine appropriate log level based on content
                log_level = self._determine_log_level(content)

                # Create fixed version
                if has_logger:
                    indent = len(line) - len(line.lstrip())
                    fixed_line = f"{' ' * indent}logger.{log_level}({content})"
                    # Skip if no logger available
                    continue

                issues.append(
                    Issue(
                        line=i,
                        message=f"print() should be logger.{log_level}()",
                        severity="warning",
                        fix_description=f"Replace with logger.{log_level}",
                        original_line=line,
                        fixed_line=fixed_line,
                    )
                )

        return issues

    def _check_percent_formatting(self, lines: list[str]) -> list[Issue]:
        """Check for % formatting in logging (should be lazy)."""
        issues: list = []

        # Pattern: logger.method("... %s ..." % variable)
        percent_pattern = re.compile(
            r'(logger|logging)\.(debug|info|warning|error|critical)\s*\(\s*["\']([^"\']*%[sdfr][^"\']*)["\']'
            r"\s*%\s*([^)]+)\)"
        )

        for i, line in enumerate(lines, 1):
            match = percent_pattern.search(line)
            if match:
                logger_obj, level, message, variables = match.groups()

                # Create fixed version with lazy formatting
                fixed_line = line.replace(
                    match.group(0), f'{logger_obj}.{level}("{message}", {variables})'
                )

                issues.append(
                    Issue(
                        line=i,
                        message="Use lazy % formatting in logging",
                        severity="warning",
                        fix_description="Move % formatting to logger arguments",
                        original_line=line,
                        fixed_line=fixed_line,
                    )
                )

        return issues

    def _check_format_logging(self, lines: list[str]) -> list[Issue]:
        """Check for .format() in logging calls."""
        issues: list = []

        # Pattern: logger.method("...{}...".format(...))
        format_pattern = re.compile(
            r'(logger|logging)\.(debug|info|warning|error|critical)\s*\(\s*["\']([^"\']*\{[^"\']*\}[^"\']*)["\']'
            r"\.format\s*\(([^)]+)\)\s*\)"
        )

        for i, line in enumerate(lines, 1):
            match = format_pattern.search(line)
            if match:
                logger_obj, level, message, args = match.groups()

                # Convert {} to %s for lazy formatting
                fixed_message = re.sub(r"\{\}", "%s", message)
                fixed_message = re.sub(r"\{[^}]+\}", "%s", fixed_message)

                fixed_line = line.replace(
                    match.group(0), f'{logger_obj}.{level}("{fixed_message}", {args})'
                )

                issues.append(
                    Issue(
                        line=i,
                        message=".format() used in logging call",
                        severity="warning",
                        fix_description="Use lazy formatting instead",
                        original_line=line,
                        fixed_line=fixed_line,
                    )
                )

        return issues

    def _check_log_levels(self, lines: list[str]) -> list[Issue]:
        """Check for incorrect log level usage."""
        issues: list = []

        # Common patterns that indicate wrong log level
        error_keywords = ["error", "exception", "fail", "critical"]

        for i, line in enumerate(lines, 1):
            # Check if info/debug used for errors
            if "logger.info" in line or "logger.debug" in line:
                message_lower = line.lower()
                if any(keyword in message_lower for keyword in error_keywords):
                    issues.append(
                        Issue(
                            line=i,
                            message="Error/exception logged at info/debug level",
                            severity="warning",
                            fix_description="Use logger.error() for errors",
                            original_line=line,
                        )
                    )

        return issues

    def _determine_log_level(self, content: str) -> str:
        """Determine appropriate log level based on content."""
        content_lower = content.lower()

        if any(word in content_lower for word in ["error", "exception", "fail"]):
            return "error"
        if any(word in content_lower for word in ["warning", "warn", "deprecated"]):
            return "warning"
        if any(word in content_lower for word in ["debug", "trace", "verbose"]):
            return "debug"
        return "info"

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply logging fixes."""
        lines = content.split("\n")

        # Sort issues by line number in reverse order
        sorted_issues = sorted(issues, key=lambda x: x.line, reverse=True)

        for issue in sorted_issues:
            if issue.fixed_line and 0 < issue.line <= len(lines):
                lines[issue.line - 1] = issue.fixed_line

        # Add logger import if needed and not present
        fixed_content = "\n".join(lines)
        if "logger." in fixed_content and "import logging" not in fixed_content:
            # Add import at the top after other imports
            import_added = False
            new_lines: list = []
            for line in lines:
                new_lines.append(line)
                if (
                    line.startswith("import ")
                    or line.startswith("from ")
                    and not import_added
                ):
                    new_lines.append("import logging")
                    new_lines.append("logger = logging.getLogger(__name__)")
                    import_added = True

            if not import_added:
                # No imports found, add at the beginning
                new_lines = [
                    "import logging",
                    "logger = logging.getLogger(__name__)",
                    "",
                ] + new_lines

            fixed_content = "\n".join(new_lines)

        return fixed_content

    def validate_fixes(self, original: str, fixed: str) -> bool:
        """Validate logging fixes."""
        if not super().validate_fixes(original, fixed):
            return False

        try:
            # Parse to ensure valid Python
            ast.parse(fixed)

            # Check that we didn't break any logging calls
            if "logger." in fixed:
                # Ensure no malformed logging calls
                malformed_patterns = [
                    r"logger\.\w+\(\s*\)",  # Empty logging calls
                    r"logger\.\w+\([^)]*\)\)",  # Double closing parenthesis
                ]
                for pattern in malformed_patterns:
                    if re.search(pattern, fixed):
                        return False

            return True
        except SyntaxError:
            return False


# Testing
if __name__ == "__main__":
    test_content = """
import os

def process_data(data):
    print("Processing data...")

    for item in data:
        logger.info(f"Processing item: {item.id} with value {item.value}")

        if item.value < 0:
            print(f"Error: Invalid value {item.value}")
            logger.debug("Found error in processing")

        result = calculate(item)
        logger.info("Result: %s" % result)

        logger.warning("Item {} needs review".format(item.id))

    print("Processing complete!")
"""

    fixer = LoggingPatternFixModule(dry_run=True, verbose=True)

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
