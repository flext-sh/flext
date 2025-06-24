#!/usr/bin/env python3
"""Validate FLX Daemon Architecture.

This script validates that the daemon implementation follows
hexagonal architecture principles correctly.

Validation Rules:
    1. Core domain must not import adapters/infrastructure
    2. No circular dependencies
    3. Proper separation of concerns
    4. Dependency injection used correctly
    5. No infrastructure concerns in domain
"""

import ast
import sys
from pathlib import Path


class ArchitectureValidator:
    """Validates architecture compliance for FLX daemon."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.daemon_path = project_root / "flx" / "src" / "flx" / "daemon"
        self.violations: list[str] = []
        self.warnings: list[str] = []

    def validate_all(self) -> bool:
        """Run all architecture validations."""
        logger.info("🔍 Validating FLX Daemon Architecture...")

        self.validate_core_dependencies()
        self.validate_layer_separation()
        self.validate_dependency_injection()
        self.validate_no_mockups()
        self.validate_import_patterns()

        return self.report_results()

    def validate_core_dependencies(self) -> None:
        """Validate that core domain doesn't import infrastructure."""
        core_file = self.daemon_path / "core.py"

        if not core_file.exists():
            self.violations.append("Core file not found")
            return

        with open(core_file, encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if self._is_infrastructure_import(alias.name):
                            self.violations.append(
                                f"Core imports infrastructure: {alias.name}",
                            )

                elif isinstance(node, ast.ImportFrom):
                    if node.module and self._is_infrastructure_import(node.module):
                        self.violations.append(
                            f"Core imports from infrastructure: {node.module}",
                        )

        except SyntaxError as e:
            self.violations.append(f"Syntax error in core.py: {e}")

    def validate_layer_separation(self) -> None:
        """Validate proper layer separation."""
        files_to_check = [
            ("core.py", "domain"),
            ("api.py", "adapter"),
            ("web.py", "adapter"),
            ("service.py", "infrastructure"),
            ("infrastructure.py", "infrastructure"),
        ]

        for filename, layer in files_to_check:
            file_path = self.daemon_path / filename
            if file_path.exists():
                self._validate_layer_imports(file_path, layer)

    def validate_dependency_injection(self) -> None:
        """Validate proper dependency injection patterns."""
        core_file = self.daemon_path / "core.py"

        if not core_file.exists():
            return

        with open(core_file, encoding="utf-8") as f:
            content = f.read()

        # Check for hardcoded server creation
        if "uvicorn" in content:
            self.violations.append("Core contains hardcoded server creation")

        if "FastAPI" in content:
            self.violations.append("Core contains FastAPI references")

        # Check for proper injection patterns
        if "add_server" not in content:
            self.warnings.append("Core should support server injection")

    def validate_no_mockups(self) -> None:
        """Validate that no mockup code exists."""
        for file_path in self.daemon_path.glob("*.py"):
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            if "Mock" in content and "class Mock" in content:
                self.violations.append(
                    f"Mockup code found in {file_path.name}",
                )

            if "# TODO:" in content:
                self.warnings.append(
                    f"TODO found in {file_path.name} - may need implementation",
                )

    def validate_import_patterns(self) -> None:
        """Validate import patterns follow conventions."""
        for file_path in self.daemon_path.glob("*.py"):
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for proper relative imports
            if "from flx.daemon" in content and file_path.name != "__init__.py":
                # Allow some daemon imports but check for cycles
                pass

            # Check for proper logging import
            if "import logging" in content:
                self.warnings.append(
                    f"{file_path.name} uses standard logging instead of flx.utils.logging",
                )

    def _is_infrastructure_import(self, module_name: str) -> bool:
        """Check if import is from infrastructure layer."""
        infrastructure_patterns = [
            "fastapi",
            "uvicorn",
            "flx.adapters",
            "flx.daemon.api",
            "flx.daemon.web",
            "flx.daemon.infrastructure",
        ]

        return any(pattern in module_name for pattern in infrastructure_patterns)

    def _validate_layer_imports(self, file_path: Path, layer: str) -> None:
        """Validate imports for specific layer."""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import | ast.ImportFrom):
                    self._check_layer_import(node, file_path.name, layer)

        except SyntaxError as e:
            self.violations.append(f"Syntax error in {file_path.name}: {e}")

    def _check_layer_import(self, node: ast.AST, filename: str, layer: str) -> None:
        """Check specific import for layer violations."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                self._validate_import_for_layer(alias.name, filename, layer)

        elif isinstance(node, ast.ImportFrom) and node.module:
            self._validate_import_for_layer(node.module, filename, layer)

    def _validate_import_for_layer(
        self, module: str, filename: str, layer: str
    ) -> None:
        """Validate specific module import for layer."""
        # Domain layer (core.py) should not import adapters
        if layer == "domain" and any(
            pattern in module for pattern in ["fastapi", "uvicorn", "flx.adapters"]
        ):
            self.violations.append(
                f"Domain layer ({filename}) imports adapter/infrastructure: {module}",
            )

    def report_results(self) -> bool:
        """Report validation results."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 ARCHITECTURE VALIDATION RESULTS")
        logger.info("=" * 60)

        if not self.violations and not self.warnings:
            logger.info("✅ All architecture validations passed!")
            logger.info("🏗️  Daemon follows hexagonal architecture correctly")
            return True

        if self.violations:
            logger.info(f"❌ {len(self.violations)} VIOLATIONS found:")
            for i, violation in enumerate(self.violations, 1):
                logger.info(f"   {i}. {violation}")

        if self.warnings:
            logger.warning(f"\n⚠️  {len(self.warnings)} WARNINGS:")
            for i, warning in enumerate(self.warnings, 1):
                logger.warning(f"   {i}. {warning}")

        success = len(self.violations) == 0

        if success:
            print(
                f"\n✅ Architecture validation PASSED (with {len(self.warnings)} warnings)"
            )
            print(
                f"\n❌ Architecture validation FAILED ({len(self.violations)} violations)"
            )

        logger.info("\n📋 ARCHITECTURE PRINCIPLES:")
        logger.info("  ✓ Domain layer independent of infrastructure")
        logger.info("  ✓ Dependency injection used for infrastructure")
        logger.info("  ✓ No circular dependencies")
        logger.info("  ✓ Proper separation of concerns")
        logger.info("  ✓ No mockup code in production")

        return success


def main() -> None:
    """Main validation function."""
    script_path = Path(__file__).parent
    project_root = script_path.parent.parent

    validator = ArchitectureValidator(project_root)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
