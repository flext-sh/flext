#!/usr/bin/env python3
"""Script Documentation Generator.

This script generates or improves documentation for Python scripts in the
pyauto workspace. It scans Python files, analyzes their content, and adds
or enhances docstrings based on the script's purpose.

Features:
1. Adds missing module-level docstrings
2. Enhances existing docstrings with more information
3. Generates documentation for important functions
4. Creates a summary of all scripts

Usage:
    python document_scripts.py [--check] [--update] [--verbose]
"""

import argparse
import ast
import re
import sys
from pathlib import Path

# Absolute paths
WORKSPACE_ROOT = Path("/home/marlonsc/pyauto")
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"

# Exclude patterns
DEFAULT_EXCLUDE_PATTERNS = [
    ".venv/",
    "reference/",
    "__pycache__/",
    "dist/",
]

# Colors for terminal output
COLORS = {
    "GREEN": "\033[0;32m",
    "YELLOW": "\033[0;33m",
    "RED": "\033[0;31m",
    "CYAN": "\033[0;36m",
    "BLUE": "\033[0;34m",
    "NC": "\033[0m",  # No Color
}


def colorize(text: str, color: str) -> str:
    """Add color to terminal output."""
    return f"{COLORS.get(color, '')}{text}{COLORS['NC']}"


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Document Python scripts in the workspace",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check for missing or incomplete documentation",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update existing documentation",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output",
    )
    parser.add_argument(
        "--exclude",
        default=",".join(DEFAULT_EXCLUDE_PATTERNS),
        help="Comma-separated list of patterns to exclude",
    )
    return parser.parse_args()


def get_python_files(scripts_dir: Path, exclude_patterns: list[str]) -> list[Path]:
    """Get all Python files in the scripts directory."""
    python_files = []

    # Check if the path exists
    if not scripts_dir.exists():
        print(f"Error: Directory {scripts_dir} does not exist")
        return []

    # Get all Python files
    for file_path in scripts_dir.glob("**/*.py"):
        # Check if file should be excluded
        exclude = False
        for pattern in exclude_patterns:
            if pattern in str(file_path):
                exclude = True
                break

        if not exclude:
            python_files.append(file_path)

    return python_files


class ScriptDocumenter:
    """Class to document Python scripts."""

    def __init__(self, script_path: Path, verbose: bool = False) -> None:
        self.script_path = script_path
        self.verbose = verbose
        self.script_content = self._read_script()
        self.ast_tree = self._parse_script()
        self.functions = self._get_functions()

    def _read_script(self) -> str:
        """Read script content."""
        try:
            with open(self.script_path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {self.script_path}: {e}")
            return ""

    def _parse_script(self) -> ast.Module | None:
        """Parse script AST."""
        try:
            return ast.parse(self.script_content)
        except SyntaxError as e:
            print(f"Syntax error in {self.script_path}: {e}")
            return None

    def _get_functions(self) -> list[ast.FunctionDef]:
        """Get all function definitions in the script."""
        if not self.ast_tree:
            return []

        return [
            node
            for node in ast.walk(self.ast_tree)
            if isinstance(node, ast.FunctionDef)
        ]

    def has_module_docstring(self) -> bool:
        """Check if script has module-level docstring."""
        if not self.ast_tree:
            return False

        return (
            len(self.ast_tree.body) > 0
            and isinstance(self.ast_tree.body[0], ast.Expr)
            and isinstance(self.ast_tree.body[0].value, ast.Str)
        )

    def get_module_docstring(self) -> str:
        """Get module-level docstring."""
        if not self.has_module_docstring():
            return ""

        return ast.get_docstring(self.ast_tree) or ""

    def suggest_module_docstring(self) -> str:
        """Suggest a module-level docstring based on script content."""
        # Get script name without extension
        script_name = self.script_path.stem

        # Generate title from script name
        title = " ".join(
            word.capitalize() for word in script_name.replace("_", " ").split()
        )

        # Try to infer purpose from function names and content
        purpose = []
        keywords = set()

        for func in self.functions:
            func_name = func.name.lower()

            # Add function name words to keywords
            for word in re.findall(r"[a-z]+", func_name):
                if len(word) > 3:  # Skip short words
                    keywords.add(word)

        # Add keywords from script name
        for word in re.findall(r"[a-z]+", script_name.lower()):
            if len(word) > 3:  # Skip short words
                keywords.add(word)

        # Construct purpose based on keywords
        if "manage" in keywords:
            purpose.append(
                "Manages and coordinates operations related to the workspace",
            )
        if "update" in keywords:
            purpose.append("Updates configuration or dependencies")
        if "fix" in keywords:
            purpose.append("Fixes issues or applies corrections")
        if "lint" in keywords or "pep8" in keywords:
            purpose.append("Ensures code quality and style compliance")
        if "scaffold" in keywords:
            purpose.append("Handles flx_project templates and scaffolding")
        if "git" in keywords:
            purpose.append("Provides Git operations for the workspace")

        # If no specific purpose found, use a generic one
        if not purpose:
            purpose = ["Utility script for the pyauto workspace"]

        # Construct docstring
        docstring = f"{title}\n\n"
        docstring += "\n".join(purpose) + "\n"
        docstring += "\nThis script is part of the pyauto workspace management tools.\n"

        return docstring

    def function_needs_docstring(self, func: ast.FunctionDef) -> bool:
        """Check if function needs a docstring."""
        # Skip private functions
        if func.name.startswith("_") and func.name != "__main__":
            return False

        # Check if function has a docstring
        return not ast.get_docstring(func)

    def suggest_function_docstring(self, func: ast.FunctionDef) -> str:
        """Suggest a docstring for a function."""
        func_name = func.name

        # Generate title from function name
        title = " ".join(
            word.capitalize() for word in func_name.replace("_", " ").split()
        )

        # Get parameters
        params = []
        for arg in func.args.args:
            if arg.arg != "self":
                params.append(arg.arg)

        # Generate docstring
        docstring = f"{title}."

        if params:
            docstring += "\n\nArgs:\n"
            for param in params:
                docstring += f"    {param}: Description of {param}.\n"

        # Add Returns section if the function seems to return something
        returns_value = False
        for node in ast.walk(func):
            if isinstance(node, ast.Return) and node.value is not None:
                returns_value = True
                break

        if returns_value:
            docstring += "\nReturns:\n    Description of return value.\n"

        return docstring

    def check_documentation(self) -> dict[str, list[str]]:
        """Check script documentation and return issues."""
        issues = {
            "module": [],
            "functions": [],
        }

        # Check module docstring
        if not self.has_module_docstring():
            issues["module"].append("Missing module docstring")
        elif len(self.get_module_docstring().split("\n")) < 3:
            issues["module"].append("Module docstring is too short")

        # Check function docstrings
        for func in self.functions:
            if self.function_needs_docstring(func):
                issues["functions"].append(
                    f"Function '{func.name}' is missing a docstring",
                )

        return issues

    def generate_documentation_report(self) -> str:
        """Generate a report of documentation status."""
        issues = self.check_documentation()

        report = f"Documentation report for {self.script_path.name}:\n"

        if not issues["module"] and not issues["functions"]:
            report += "  ✓ Documentation is complete\n"
            return report

        if issues["module"]:
            report += "  Module issues:\n"
            for issue in issues["module"]:
                report += f"    - {issue}\n"

        if issues["functions"]:
            report += "  Function issues:\n"
            for issue in issues["functions"]:
                report += f"    - {issue}\n"

        return report

    def update_documentation(self) -> tuple[bool, str]:
        """Update script documentation and return updated content."""
        modified = False
        updated_content = self.script_content

        # Handle module docstring
        if not self.has_module_docstring():
            docstring = self.suggest_module_docstring()

            # Add to the beginning of the file, after any shebang
            lines = updated_content.split("\n")
            insert_pos = 0

            # Check for shebang
            if lines and lines[0].startswith("#!"):
                insert_pos = 1

            # Insert the docstring
            formatted_docstring = f'"""\n{docstring}\n"""'
            lines.insert(insert_pos, formatted_docstring)

            # If there's no blank line after the docstring, add one
            if insert_pos + 1 < len(lines) and lines[insert_pos + 1].strip():
                lines.insert(insert_pos + 1, "")

            updated_content = "\n".join(lines)
            modified = True

        # We don't automatically update function docstrings as it's more complex
        # and might require manual intervention

        return modified, updated_content

    def write_updated_content(self, content: str) -> bool:
        """Write updated content to file."""
        try:
            with open(self.script_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing to {self.script_path}: {e}")
            return False


def generate_scripts_summary(python_files: list[Path]) -> str:
    """Generate a summary of all scripts."""
    summary = "# pyauto Scripts Summary\n\n"
    summary += (
        "This document provides an overview of scripts in the pyauto workspace.\n\n"
    )

    # Group scripts by directory
    scripts_by_dir = {}
    for file_path in sorted(python_files):
        dir_name = file_path.parent.name
        if dir_name not in scripts_by_dir:
            scripts_by_dir[dir_name] = []
        scripts_by_dir[dir_name].append(file_path)

    # Add each script to the summary
    for dir_name, scripts in scripts_by_dir.items():
        if dir_name == "scripts":
            summary += "## Main Scripts\n\n"
        else:
            summary += f"## Scripts in {dir_name}\n\n"

        for script_path in sorted(scripts):
            # Get script name and basic info
            script_name = script_path.name

            # Try to get docstring
            try:
                with open(script_path, encoding="utf-8") as f:
                    content = f.read()

                # Parse and get docstring
                tree = ast.parse(content)
                docstring = ast.get_docstring(tree)

                if docstring:
                    # Extract the first line as title
                    title = docstring.split("\n")[0].strip()

                    # Extract a brief description (next paragraph)
                    description = ""
                    paragraphs = [p.strip() for p in docstring.split("\n\n")]
                    if len(paragraphs) > 1:
                        description = paragraphs[1].replace("\n", " ")

                    summary += f"### {script_name}\n\n"
                    summary += f"**{title}**\n\n"

                    if description:
                        summary += f"{description}\n\n"

                    # Add a separator
                    summary += "---\n\n"
                else:
                    summary += f"### {script_name}\n\n"
                    summary += "*No documentation available*\n\n"
                    summary += "---\n\n"

            except Exception as e:
                summary += f"### {script_name}\n\n"
                summary += f"*Error parsing script: {e}*\n\n"
                summary += "---\n\n"

    return summary


def main() -> int:
    """Main function."""
    args = parse_arguments()

    # Convert exclude patterns to list
    exclude_patterns = (
        args.exclude.split(",") if args.exclude else DEFAULT_EXCLUDE_PATTERNS
    )

    # Get Python files
    python_files = get_python_files(SCRIPTS_DIR, exclude_patterns)

    if not python_files:
        print(colorize("No Python files found in scripts directory", "YELLOW"))
        return 1

    print(f"Found {len(python_files)} Python files")

    # Checking mode
    if args.check:
        print(colorize("Checking documentation status...", "CYAN"))

        issues_found = False
        for script_path in python_files:
            documenter = ScriptDocumenter(script_path, args.verbose)
            issues = documenter.check_documentation()

            if issues["module"] or issues["functions"]:
                issues_found = True
                print(colorize(documenter.generate_documentation_report(), "YELLOW"))
            elif args.verbose:
                print(
                    colorize(
                        f"✓ {script_path.name} documentation is complete",
                        "GREEN",
                    ),
                )

        if not issues_found:
            print(colorize("All scripts are properly documented!", "GREEN"))

    # Update mode
    elif args.update:
        print(colorize("Updating documentation...", "CYAN"))

        updated_count = 0
        for script_path in python_files:
            documenter = ScriptDocumenter(script_path, args.verbose)
            modified, updated_content = documenter.update_documentation()

            if modified:
                if documenter.write_updated_content(updated_content):
                    updated_count += 1
                    print(
                        colorize(
                            f"Updated documentation for {script_path.name}",
                            "GREEN",
                        ),
                    )
                else:
                    print(colorize(f"Failed to update {script_path.name}", "RED"))
            elif args.verbose:
                print(colorize(f"No updates needed for {script_path.name}", "YELLOW"))

        print(colorize(f"Updated documentation for {updated_count} scripts", "GREEN"))

    # Generate summary
    print(colorize("Generating scripts summary...", "CYAN"))
    summary = generate_scripts_summary(python_files)

    summary_path = SCRIPTS_DIR / "SCRIPTS_SUMMARY.md"
    try:
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        print(colorize(f"Generated summary at {summary_path}", "GREEN"))
    except Exception as e:
        print(colorize(f"Error writing summary: {e}", "RED"))
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
