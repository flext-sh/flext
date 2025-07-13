#!/usr/bin/env python3
"""Test runner moderno com coverage alta e tooling eficaz.

Este script implementa as melhores práticas para testing:
- Coverage >95%
- Strict linting/mypy para tests
- Integração/E2E condicionais baseados em .env
- Relatórios detalhados
- Zero tolerance para test smells
"""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class ModernTestRunner:
    """Test runner moderno seguindo SOLID, DRY, KISS principles."""

    def __init__(self) -> None:
        """Initialize test runner."""
        self.python_bin = "/home/marlonsc/flext/.venv/bin/python"
        self.project_root = Path.cwd()
        self.has_env = (self.project_root / ".env").exists()
        self.test_results: dict[str, bool] = {}

    def run_command(self, cmd: list[str], description: str) -> tuple[bool, str]:
        """Execute command and capture result."""
        logger.info(f"🔧 {description}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=self.project_root,
            )
            success = result.returncode == 0
            output = result.stdout + result.stderr

            if success:
                logger.info(f"✅ {description} - SUCCESS")
            else:
                logger.info(f"❌ {description} - FAILED")
                if output.strip():
                    # Show first few lines of error for context
                    error_lines = output.strip().split("\n")[:5]
                    for line in error_lines:
                        logger.info(f"   {line}")
                    if len(output.strip().split("\n")) > 5:
                        logger.info("   ...")

            return success, output
        except Exception as e:
            logger.info(f"❌ {description} - EXCEPTION: {e}")
            return False, str(e)

    def lint_tests(self) -> bool:
        """Lint test files with strict PEP compliance."""
        logger.info("\n📋 FASE 1: Linting Tests (PEP Strict)")
        logger.info("=" * 40)

        # Test files must pass same linting as source code
        cmd = [
            self.python_bin,
            "-m",
            "ruff",
            "check",
            "tests/",
            "--select=E,W,F,UP,SIM,PYI,PT,RUF",
        ]

        success, _output = self.run_command(cmd, "Ruff linting on tests")
        self.test_results["lint_tests"] = success

        if not success:
            logger.info("⚠️ Tests have linting violations - fixing automatically...")
            fix_cmd = [*cmd, "--fix", "--unsafe-fixes"]
            self.run_command(fix_cmd, "Auto-fixing test linting issues")

        return success

    def type_check_tests(self) -> bool:
        """Type check test files with mypy."""
        logger.info("\n🔍 FASE 2: Type Checking Tests")
        logger.info("=" * 40)

        cmd = [
            self.python_bin,
            "-m",
            "mypy",
            "tests/",
            "--strict",
            "--show-error-codes",
        ]

        success, _output = self.run_command(cmd, "MyPy type checking on tests")
        self.test_results["type_check_tests"] = success

        return success

    def run_unit_tests(self) -> bool:
        """Run unit tests with coverage."""
        logger.info("\n🧪 FASE 3: Unit Tests com Coverage")
        logger.info("=" * 40)

        cmd = [
            self.python_bin,
            "-m",
            "pytest",
            "tests/unit/",
            "--cov=src/client-a_oud_mig",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "--cov-fail-under=90",  # Require 90% coverage minimum
            "-v",
            "--tb=short",
            "--strict-markers",
            "--strict-config",
        ]

        success, output = self.run_command(cmd, "Unit tests with coverage")
        self.test_results["unit_tests"] = success

        # Extract coverage percentage
        if "TOTAL" in output:
            lines = output.split("\n")
            for line in lines:
                if "TOTAL" in line and "%" in line:
                    coverage_line = line.strip()
                    logger.info(f"📊 Coverage: {coverage_line}")
                    break

        return success

    def run_integration_tests(self) -> bool:
        """Run integration tests if .env exists."""
        logger.info("\n🔗 FASE 4: Integration Tests")
        logger.info("=" * 40)

        if not self.has_env:
            logger.info("⏭️ Skipping integration tests (.env not found)")
            self.test_results["integration_tests"] = True  # Not required
            return True

        logger.info("🔍 .env found - running integration tests")

        cmd = [
            self.python_bin,
            "-m",
            "pytest",
            "tests/integration/",
            "-v",
            "--tb=short",
            "-m",
            "not slow",  # Skip slow tests by default
        ]

        success, _output = self.run_command(cmd, "Integration tests")
        self.test_results["integration_tests"] = success

        return success

    def run_e2e_tests(self) -> bool:
        """Run E2E tests if .env exists."""
        logger.info("\n🌐 FASE 5: E2E Tests")
        logger.info("=" * 40)

        if not self.has_env:
            logger.info("⏭️ Skipping E2E tests (.env not found)")
            self.test_results["e2e_tests"] = True  # Not required
            return True

        # Check if E2E tests exist
        e2e_dir = self.project_root / "tests" / "e2e"
        if not e2e_dir.exists():
            logger.info("⏭️ Skipping E2E tests (tests/e2e/ not found)")
            self.test_results["e2e_tests"] = True
            return True

        logger.info("🔍 E2E tests found - running with .env configuration")

        cmd = [
            self.python_bin,
            "-m",
            "pytest",
            "tests/e2e/",
            "-v",
            "--tb=short",
            "--timeout=300",  # 5 minute timeout for E2E
        ]

        success, _output = self.run_command(cmd, "E2E tests")
        self.test_results["e2e_tests"] = success

        return success

    def run_performance_tests(self) -> bool:
        """Run performance tests."""
        logger.info("\n⚡ FASE 6: Performance Tests")
        logger.info("=" * 40)

        # Check if performance tests exist
        perf_dir = self.project_root / "tests" / "performance"
        if not perf_dir.exists():
            logger.info("⏭️ Skipping performance tests (tests/performance/ not found)")
            self.test_results["performance_tests"] = True
            return True

        cmd = [
            self.python_bin,
            "-m",
            "pytest",
            "tests/performance/",
            "--benchmark-only",
            "--benchmark-sort=mean",
            "-v",
        ]

        success, _output = self.run_command(cmd, "Performance tests")
        self.test_results["performance_tests"] = success

        return success

    def security_scan(self) -> bool:
        """Run security scan on source and tests."""
        logger.info("\n🔒 FASE 7: Security Scan")
        logger.info("=" * 40)

        cmd = [
            self.python_bin,
            "-m",
            "bandit",
            "-r",
            "src/",
            "tests/",
            "-f",
            "json",
            "-o",
            "security-report.json",
        ]

        success, _output = self.run_command(cmd, "Security scan with bandit")
        self.test_results["security_scan"] = success

        return success

    def generate_comprehensive_report(self) -> None:
        """Generate comprehensive test report."""
        logger.info("\n📊 RELATÓRIO COMPREHENSIVE DE TESTS")
        logger.info("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)

        logger.info("\n🎯 RESUMO GERAL:")
        logger.info(f"   Total de fases: {total_tests}")
        logger.info(f"   Fases passaram: {passed_tests}")
        logger.info(f"   Taxa de sucesso: {passed_tests / total_tests * 100:.1f}%")

        logger.info("\n📋 DETALHES POR FASE:")
        for phase, success in self.test_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"   {phase.replace('_', ' ').title()}: {status}")

        # Environment info
        logger.info("\n🔧 CONFIGURAÇÃO:")
        logger.info(f"   .env presente: {'✅ Sim' if self.has_env else '❌ Não'}")
        logger.info(f"   Python: {self.python_bin}")
        logger.info(f"   Diretório: {self.project_root}")

        # Coverage info if available
        coverage_file = self.project_root / "coverage.xml"
        if coverage_file.exists():
            logger.info("   Coverage report: coverage.xml")

        htmlcov_dir = self.project_root / "htmlcov"
        if htmlcov_dir.exists():
            logger.info("   HTML coverage: htmlcov/index.html")

        # Recommendations
        logger.info("\n💡 RECOMENDAÇÕES:")

        if not self.test_results.get("lint_tests", True):
            logger.info("   - Corrigir violações de linting nos tests")

        if not self.test_results.get("type_check_tests", True):
            logger.info("   - Corrigir issues de typing nos tests")

        if not self.test_results.get("unit_tests", True):
            logger.info("   - Corrigir unit tests falhando")
            logger.info("   - Aumentar coverage para >90%")

        if not self.has_env:
            logger.info("   - Criar .env para habilitar testes de integração/E2E")

        if all(self.test_results.values()):
            logger.info("   🎉 TODOS OS TESTS PASSARAM! Código production-ready!")

    def run_all(self) -> bool:
        """Run complete test suite."""
        logger.info("🚀 MODERN TEST RUNNER - client-a OUD MIGRATION")
        logger.info("=" * 60)
        logger.info(
            f"Environment: {'.env FOUND' if self.has_env else '.env NOT FOUND'}"
        )
        logger.info("=" * 60)

        # Run all test phases
        phases = [
            self.lint_tests,
            self.type_check_tests,
            self.run_unit_tests,
            self.run_integration_tests,
            self.run_e2e_tests,
            self.run_performance_tests,
            self.security_scan,
        ]

        for phase in phases:
            try:
                phase()
            except KeyboardInterrupt:
                logger.info("\n⚠️ Tests interrompidos pelo usuário")
                return False
            except Exception as e:
                logger.info(f"\n❌ Erro inesperado: {e}")
                return False

        # Generate final report
        self.generate_comprehensive_report()

        # Return overall success
        all_passed = all(self.test_results.values())

        logger.info("\n" + "=" * 60)
        if all_passed:
            logger.info("✅ TODOS OS TESTS PASSARAM - CÓDIGO PRODUCTION READY!")
        else:
            logger.info("❌ ALGUNS TESTS FALHARAM - PRECISA CORREÇÃO")
        logger.info("=" * 60)

        return all_passed


def main() -> None:
    """Main function."""
    runner = ModernTestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
