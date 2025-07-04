#!/usr/bin/env python3
"""Fix critical syntax errors breaking the code."""

import os
import re
from pathlib import Path


class CriticalSyntaxFixer:
    """Fix critical syntax errors that prevent code parsing."""

    def __init__(self):
        self.fixed_files = 0

    def fix_project(self, project_path: str) -> None:
        """Fix critical syntax errors in a project."""
        print(f"🚨 FIXING CRITICAL SYNTAX ERRORS: {project_path}")

        py_files = list(Path(project_path).rglob("*.py"))

        for py_file in py_files:
            if self.fix_file(str(py_file)):
                self.fixed_files += 1

        print(f"  Fixed {self.fixed_files} files")
        self.fixed_files = 0

    def fix_file(self, file_path: str) -> bool:
        """Fix critical syntax errors in a file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix the most critical syntax errors
            content = self.fix_malformed_function_parameters(content)
            content = self.fix_arrow_in_parameter_names(content)
            content = self.fix_undefined_variables(content)

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def fix_malformed_function_parameters(self, content: str) -> str:
        """Fix malformed function parameters with -> None: in them."""
        # Pattern: parameter_name -> None: type
        return re.sub(
            r"(\w+) -> None: ([^,)]+)",
            r"\1: \2",
            content
        )

    def fix_arrow_in_parameter_names(self, content: str) -> str:
        """Fix function definitions with -> None in parameter names."""
        lines = content.split("\n")
        fixed_lines = []

        for line in lines:
            # Fix function signatures with malformed parameters
            if "def " in line and "-> None:" in line and ", " in line:
                # This is a malformed function definition
                # Extract function name and fix parameters
                match = re.match(r"(\s*def\s+\w+\s*\()[^)]*(\)\s*->\s*[^:]+:)", line)
                if match:
                    # Rebuild the function signature properly
                    func_start = match.group(1)
                    func_end = match.group(2)

                    # Extract parameters and clean them
                    params_match = re.search(r"def\s+\w+\s*\(([^)]*)\)", line)
                    if params_match:
                        params_str = params_match.group(1)
                        # Remove -> None: from parameter names
                        clean_params = re.sub(r"\w+ -> None: ", "", params_str)
                        clean_params = re.sub(r"(\w+) -> None: ([^,)]+)", r"\1: \2", clean_params)

                        # Rebuild the line
                        func_name_match = re.search(r"def\s+(\w+)", line)
                        return_type_match = re.search(r"->\s*([^:]+):", line)

                        if func_name_match and return_type_match:
                            func_name = func_name_match.group(1)
                            return_type = return_type_match.group(1).strip()

                            indent = len(line) - len(line.lstrip())
                            fixed_line = f"{' ' * indent}def {func_name}({clean_params}) -> {return_type}:"
                            fixed_lines.append(fixed_line)
                            continue

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def fix_undefined_variables(self, content: str) -> str:
        """Fix undefined variables and imports."""
        # Fix profile_config undefined variable
        content = re.sub(
            r"return ConfigMapper\(profile_config\)",
            r"return ConfigMapper(config or {})",
            content
        )

        # Add missing logging import
        if "logger: logging.Logger" in content and "import logging" not in content:
            lines = content.split("\n")
            # Find the first import and add logging import
            for i, line in enumerate(lines):
                if line.startswith(("import ", "from ")):
                    lines.insert(i, "import logging")
                    break
            content = "\n".join(lines)

        return content


def main():
    """Main execution function."""
    fixer = CriticalSyntaxFixer()

    projects = [
        "/home/marlonsc/flext/flext-tap-oracle-wms",
        "/home/marlonsc/flext/flext-target-oracle",
        "/home/marlonsc/flext/gruponos-meltano-native"
    ]

    print("🚨 CRITICAL SYNTAX ERROR FIXES")
    print("=" * 40)

    for project in projects:
        if os.path.exists(project):
            fixer.fix_project(project)

    print("\n✅ Critical syntax fixes completed!")

    # Get final counts
    print("\n📊 FINAL ERROR COUNT CHECK:")
    import subprocess

    for project in projects:
        if os.path.exists(project):
            project_name = os.path.basename(project)
            print(f"\n{project_name}:")

            try:
                # Count mypy errors
                if "gruponos-meltano-native" in project:
                    mypy_result = subprocess.run(
                        ["python", "-m", "mypy", "--strict", "src/"],
                        cwd=project, capture_output=True, text=True, check=False
                    )
                else:
                    src_dir = "src/" if "tap-oracle" in project else f'{project_name.replace("-", "_")}/'
                    mypy_result = subprocess.run(
                        ["python", "-m", "mypy", "--strict", src_dir],
                        cwd=project, capture_output=True, text=True, check=False
                    )

                mypy_errors = mypy_result.stderr.strip().split("\n") if mypy_result.stderr.strip() else []
                mypy_count = len([e for e in mypy_errors if e.strip() and not e.startswith("Success:")])

                # Count ruff errors
                if "gruponos-meltano-native" in project:
                    ruff_result = subprocess.run(
                        ["python", "-m", "ruff", "check", "src/"],
                        cwd=project, capture_output=True, text=True, check=False
                    )
                else:
                    src_dir = "src/" if "tap-oracle" in project else f'{project_name.replace("-", "_")}/'
                    ruff_result = subprocess.run(
                        ["python", "-m", "ruff", "check", src_dir],
                        cwd=project, capture_output=True, text=True, check=False
                    )

                ruff_errors = ruff_result.stdout.strip().split("\n") if ruff_result.stdout.strip() else []
                ruff_count = len([e for e in ruff_errors if e.strip() and not e.startswith("Found") and ":" in e])

                total = mypy_count + ruff_count
                print(f"  mypy: {mypy_count} | ruff: {ruff_count} | total: {total}")

            except Exception as e:
                print(f"  Error checking: {e}")


if __name__ == "__main__":
    main()
