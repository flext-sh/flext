#!/usr/bin/env python3
"""Organize all FLEXT submodules and projects systematically."""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

class SubmoduleOrganizer:
    """Organize all FLEXT submodules comprehensively."""

    def __init__(self):
        self.workspace_root = Path(__file__).parent
        self.backup_root = self.workspace_root / "submodule_cleanup_backup"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define FLEXT modules
        self.flext_modules = [
            "flext-core", "flext-auth", "flext-api", "flext-grpc",
            "flext-web", "flext-cli", "flext-meltano", "flext-plugin",
            "flext-observability", "flext-ldap", "flext-db-oracle",
            "flext-quality"
        ]

        # Define project directories
        self.project_dirs = [
            "algar-oud-mig", "gruponos-meltano-native", "gruponos-poc-oic-wms"
        ]

        # Files/patterns to cleanup
        self.cleanup_patterns = {
            "temp_files": [
                "*.log", "*.tmp", "*.temp", "*.bak", "*.backup",
                "*.orig", "*.swp", "*.cache", "debug_*.txt",
                "temp_*", "tmp_*", "*_temp.*", "*_tmp.*"
            ],
            "build_artifacts": [
                "__pycache__", "*.pyc", "*.pyo", "*.egg-info",
                "dist/", "build/", ".eggs/", "*.egg",
                ".pytest_cache/", ".coverage", "coverage.xml",
                ".mypy_cache/", ".ruff_cache/"
            ],
            "editor_files": [
                ".vscode/settings.json", ".idea/", "*.sublime-*",
                ".DS_Store", "Thumbs.db", "desktop.ini"
            ],
            "old_scripts": [
                "test_*.py", "debug_*.py", "temp_*.py", "old_*.py",
                "backup_*.py", "fix_*.py", "check_*.py"
            ],
            "output_files": [
                "*.jsonl", "*.state", "*.pid", "nohup.out",
                "*.sqlite3", "*.db", "*.rdb"
            ]
        }

    def analyze_submodule(self, module_path: Path) -> dict:
        """Analyze a submodule for cleanup opportunities."""
        analysis = {
            "module_name": module_path.name,
            "has_pyproject": (module_path / "pyproject.toml").exists(),
            "has_makefile": (module_path / "Makefile").exists(),
            "has_tests": (module_path / "tests").exists(),
            "has_src": (module_path / "src").exists(),
            "cleanup_candidates": {},
            "file_counts": {"total": 0, "cleanup": 0},
            "issues": []
        }

        if not module_path.exists():
            analysis["issues"].append("Module directory not found")
            return analysis

        # Count files and identify cleanup candidates
        for category, patterns in self.cleanup_patterns.items():
            candidates = []
            for pattern in patterns:
                if pattern.endswith("/"):
                    # Directory pattern
                    candidates.extend(module_path.rglob(pattern.rstrip("/")))
                else:
                    # File pattern
                    candidates.extend(module_path.rglob(pattern))

            # Filter out false positives
            valid_candidates = []
            for candidate in candidates:
                if self._should_cleanup(candidate, module_path):
                    valid_candidates.append(candidate.relative_to(module_path))

            if valid_candidates:
                analysis["cleanup_candidates"][category] = valid_candidates
                analysis["file_counts"]["cleanup"] += len(valid_candidates)

        # Count total files
        analysis["file_counts"]["total"] = len(list(module_path.rglob("*")))

        return analysis

    def _should_cleanup(self, file_path: Path, module_root: Path) -> bool:
        """Determine if a file should be cleaned up."""
        relative_path = file_path.relative_to(module_root)

        # Keep important directories
        keep_dirs = [
            "src/", "tests/", "docs/", ".git/", ".github/",
            "examples/", "scripts/"
        ]

        # Keep important files
        keep_files = [
            "pyproject.toml", "Makefile", "README.md", "CLAUDE.md",
            "requirements.txt", "setup.py", "conftest.py"
        ]

        # Check if in keep directories
        for keep_dir in keep_dirs:
            if str(relative_path).startswith(keep_dir):
                return False

        # Check if important file
        if file_path.name in keep_files:
            return False

        # Check if it's a proper test file (not temp test)
        if (file_path.name.startswith("test_") and
            "tests/" in str(relative_path) and
            not any(x in file_path.name for x in ["temp", "old", "backup"])):
            return False

        return True

    def create_backup_structure(self) -> Path:
        """Create backup directory structure."""
        backup_dir = self.backup_root / self.timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create documentation
        readme_content = f"""# Submodule Cleanup Backup - {self.timestamp}

## Overview

This backup contains files removed during FLEXT submodule organization.
Files were categorized and removed to clean up the workspace.

## Categories Cleaned

- **temp_files** - Temporary files and logs
- **build_artifacts** - Python build artifacts and cache
- **editor_files** - Editor configuration and system files
- **old_scripts** - Deprecated test and debug scripts
- **output_files** - Runtime output and database files

## Restoration

To restore any file:
```bash
# Find the file
find . -name "filename"

# Copy back to workspace
cp path/to/file /home/marlonsc/flext/module-name/
```

## Modules Cleaned

This backup contains cleanup from all FLEXT modules and projects.
Each module maintains its directory structure in the backup.

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(backup_dir / "README.md", "w") as f:
            f.write(readme_content)

        return backup_dir

    def cleanup_submodule(self, module_path: Path, backup_dir: Path) -> dict:
        """Clean up a specific submodule."""
        analysis = self.analyze_submodule(module_path)

        if not analysis["cleanup_candidates"]:
            return {"moved": 0, "errors": 0}

        module_backup = backup_dir / module_path.name
        moved_count = 0
        error_count = 0

        for category, candidates in analysis["cleanup_candidates"].items():
            category_backup = module_backup / category

            for relative_path in candidates:
                source_path = module_path / relative_path

                if not source_path.exists():
                    continue

                # Create target directory
                target_path = category_backup / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    if source_path.is_dir():
                        shutil.move(str(source_path), str(target_path))
                    else:
                        shutil.move(str(source_path), str(target_path))
                    moved_count += 1
                except Exception as e:
                    console.print(f"⚠️ Failed to move {relative_path}: {e}", style="yellow")
                    error_count += 1

        return {"moved": moved_count, "errors": error_count}

    def standardize_makefile(self, module_path: Path) -> bool:
        """Standardize Makefile for a module."""
        makefile_path = module_path / "Makefile"

        # Standard Makefile template for FLEXT modules
        makefile_content = f"""# {module_path.name.upper()} Makefile
# ========================

.PHONY: help install test clean lint format build docs

# Default target
help: ## Show this help message
\t@echo "{module_path.name.upper()} Development Commands"
\t@echo "===================================="
\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}}'

# Installation
install: ## Install dependencies
\t@echo "📦 Installing dependencies for {module_path.name}..."
\t@if [ -f pyproject.toml ]; then \\
\t\tpoetry install; \\
\telse \\
\t\tpip install -r requirements.txt; \\
\tfi

# Testing
test: ## Run tests
\t@echo "🧪 Running tests for {module_path.name}..."
\t@if [ -d tests ]; then \\
\t\tpython -m pytest tests/ -v; \\
\telse \\
\t\techo "No tests directory found"; \\
\tfi

test-coverage: ## Run tests with coverage
\t@echo "🧪 Running tests with coverage for {module_path.name}..."
\t@python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

# Code quality
lint: ## Run linters
\t@echo "🔍 Running linters for {module_path.name}..."
\t@python -m ruff check .
\t@python -m mypy src/ || true

format: ## Format code
\t@echo "🎨 Formatting code for {module_path.name}..."
\t@python -m black .
\t@python -m ruff check --fix .

check: lint test ## Run all quality checks
\t@echo "✅ All quality checks complete for {module_path.name}!"

# Build
build: ## Build the package
\t@echo "🔨 Building {module_path.name}..."
\t@if [ -f pyproject.toml ]; then \\
\t\tpoetry build; \\
\telse \\
\t\tpython setup.py build; \\
\tfi

# Documentation
docs: ## Generate documentation
\t@echo "📚 Generating documentation for {module_path.name}..."
\t@if [ -f docs/conf.py ]; then \\
\t\tcd docs && make html; \\
\telse \\
\t\techo "No docs configuration found"; \\
\tfi

# Cleanup
clean: ## Clean build artifacts
\t@echo "🧹 Cleaning build artifacts for {module_path.name}..."
\t@rm -rf build/ dist/ *.egg-info/
\t@find . -type d -name "__pycache__" -exec rm -rf {{}} + 2>/dev/null || true
\t@find . -name "*.pyc" -delete 2>/dev/null || true
\t@find . -name "*.pyo" -delete 2>/dev/null || true

# Development
dev-setup: install ## Complete development setup
\t@echo "🎯 Setting up development environment for {module_path.name}..."
\t@echo "Development setup complete!"

# Environment variables
export PYTHONPATH := $(PYTHONPATH):$(PWD)/src
"""

        try:
            with open(makefile_path, "w") as f:
                f.write(makefile_content)
            return True
        except Exception as e:
            console.print(f"⚠️ Failed to create Makefile for {module_path.name}: {e}", style="yellow")
            return False

    def test_cli_commands(self) -> dict:
        """Test the unified CLI commands."""
        console.print("🧪 Testing unified CLI commands...", style="blue")

        test_results = {}

        cli_tests = [
            ("help", ["./flx", "--help"]),
            ("info", ["./flx", "info"]),
            ("workspace_status", ["./flx", "workspace", "status"]),
            ("quality_check", ["./flx", "quality", "check"]),
        ]

        for test_name, command in cli_tests:
            try:
                result = subprocess.run(
                    command,
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=30, check=False
                )

                test_results[test_name] = {
                    "success": result.returncode == 0,
                    "output_length": len(result.stdout),
                    "has_error": len(result.stderr) > 0
                }

                if result.returncode == 0:
                    console.print(f"✅ CLI test '{test_name}' passed", style="green")
                else:
                    console.print(f"❌ CLI test '{test_name}' failed", style="red")

            except Exception as e:
                test_results[test_name] = {
                    "success": False,
                    "error": str(e)
                }
                console.print(f"❌ CLI test '{test_name}' error: {e}", style="red")

        return test_results

    def run_pytest_all_modules(self) -> dict:
        """Run pytest on all modules that have tests."""
        console.print("🔬 Running pytest on all modules...", style="blue")

        test_results = {}

        # Test FLEXT modules
        for module_name in self.flext_modules:
            module_path = self.workspace_root / module_name
            if not module_path.exists():
                continue

            tests_dir = module_path / "tests"
            if not tests_dir.exists():
                test_results[module_name] = {"status": "no_tests", "message": "No tests directory"}
                continue

            console.print(f"🧪 Testing {module_name}...")

            try:
                result = subprocess.run(
                    ["python", "-m", "pytest", "tests/", "-v", "--tb=short"],
                    cwd=module_path,
                    capture_output=True,
                    text=True,
                    timeout=120, check=False
                )

                test_results[module_name] = {
                    "status": "passed" if result.returncode == 0 else "failed",
                    "return_code": result.returncode,
                    "output_lines": len(result.stdout.split("\n")),
                    "error_lines": len(result.stderr.split("\n")) if result.stderr else 0
                }

                if result.returncode == 0:
                    console.print(f"✅ {module_name} tests passed", style="green")
                else:
                    console.print(f"❌ {module_name} tests failed", style="red")

            except subprocess.TimeoutExpired:
                test_results[module_name] = {"status": "timeout", "message": "Tests timed out"}
                console.print(f"⏰ {module_name} tests timed out", style="yellow")
            except Exception as e:
                test_results[module_name] = {"status": "error", "error": str(e)}
                console.print(f"❌ {module_name} test error: {e}", style="red")

        return test_results

def main():
    """Main execution."""
    organizer = SubmoduleOrganizer()

    console.print("🎯 FLEXT Submodule Organization - Complete Cleanup", style="bold blue")
    console.print("=" * 60)

    # Step 1: Analyze all modules
    console.print("\n📊 Analyzing all modules for cleanup opportunities...")

    all_modules = organizer.flext_modules + organizer.project_dirs
    analyses = {}

    for module_name in all_modules:
        module_path = organizer.workspace_root / module_name
        if module_path.exists():
            analyses[module_name] = organizer.analyze_submodule(module_path)

    # Show analysis summary
    table = Table(title="Submodule Cleanup Analysis")
    table.add_column("Module", style="cyan")
    table.add_column("Files to Clean", style="green")
    table.add_column("Has Tests", style="yellow")
    table.add_column("Has Makefile", style="blue")

    total_cleanup = 0
    for module_name, analysis in analyses.items():
        cleanup_count = analysis["file_counts"]["cleanup"]
        total_cleanup += cleanup_count

        table.add_row(
            module_name,
            str(cleanup_count),
            "✅" if analysis["has_tests"] else "❌",
            "✅" if analysis["has_makefile"] else "❌"
        )

    console.print(table)
    console.print(f"\n📊 Total files to clean: {total_cleanup}")

    # Step 2: Create backup and cleanup
    console.print("\n🧹 Creating backup and cleaning up modules...")
    backup_dir = organizer.create_backup_structure()

    cleanup_summary = {}
    for module_name, analysis in analyses.items():
        if analysis["file_counts"]["cleanup"] > 0:
            module_path = organizer.workspace_root / module_name
            result = organizer.cleanup_submodule(module_path, backup_dir)
            cleanup_summary[module_name] = result
            console.print(f"✅ Cleaned {module_name}: {result['moved']} files moved")

    # Step 3: Standardize Makefiles
    console.print("\n⚙️ Standardizing Makefiles...")
    makefile_results = {}

    for module_name in all_modules:
        module_path = organizer.workspace_root / module_name
        if module_path.exists():
            success = organizer.standardize_makefile(module_path)
            makefile_results[module_name] = success
            if success:
                console.print(f"✅ Standardized Makefile for {module_name}")

    # Step 4: Test CLI
    console.print("\n🧪 Testing unified CLI...")
    cli_results = organizer.test_cli_commands()

    # Step 5: Run pytest on all modules
    console.print("\n🔬 Running pytest on all modules...")
    pytest_results = organizer.run_pytest_all_modules()

    # Final summary
    console.print("\n" + "=" * 60)
    console.print("🎉 FLEXT SUBMODULE ORGANIZATION COMPLETE!", style="bold green")
    console.print("=" * 60)

    console.print(f"📦 Backup created: {backup_dir}")
    console.print(f"🧹 Files cleaned: {sum(r.get('moved', 0) for r in cleanup_summary.values())}")
    console.print(f"⚙️ Makefiles standardized: {sum(1 for success in makefile_results.values() if success)}")
    console.print(f"🧪 CLI tests passed: {sum(1 for r in cli_results.values() if r.get('success'))}/{len(cli_results)}")
    console.print(f"🔬 Module tests passed: {sum(1 for r in pytest_results.values() if r.get('status') == 'passed')}")

    console.print("\n✅ Ready for development with clean, standardized modules!")

if __name__ == "__main__":
    main()
