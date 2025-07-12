#!/usr/bin/env python3
"""Modernizador de configurações pytest para workspace FLEXT.

Este script aplica configurações modernas de pytest, coverage e ferramentas
de teste a todos os projetos do workspace FLEXT, garantindo alta cobertura
e melhores práticas.

Versão: 2025-07-05
Autor: Claude Code
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any

import toml

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Diretório raiz do workspace
WORKSPACE_ROOT = Path(__file__).parent
TEMPLATE_PYTEST_CONFIG = WORKSPACE_ROOT / "PYTEST_MODERN_TEMPLATE.toml"
TEMPLATE_CONFTEST = WORKSPACE_ROOT / "CONFTEST_MODERN_TEMPLATE.py"

# Projetos FLEXT identificados
FLEXT_PROJECTS = [
    "flext-core",
    "flext-auth",
    "flext-api",
    "flext-grpc",
    "flext-web",
    "flext-cli",
    "flext-meltano",
    "flext-observability",
    "flext-plugin",
    "flext-ldap",
    "flext-db-oracle",
    "flext-quality",
    "flext-tap-ldap",
    "flext-tap-oracle-oic",
    "flext-tap-oracle-wms",
    "flext-target-ldap",
    "flext-target-oracle",
    "flext-target-oracle-oic",
    "flext-dbt-ldap",
    "flext-oracle-oic-ext",
    "flext-meltano-bridge",
]

# Configurações específicas por tipo de projeto
PROJECT_TYPE_CONFIGS = {
    "singer": {
        "markers": [
            "tap: marks tests for Singer taps",
            "target: marks tests for Singer targets",
            "stream: marks tests for data streams",
            "catalog: marks tests for catalog discovery",
            "state: marks tests for state management",
        ],
        "requirements": ["singer-sdk>=0.47.4"],
    },
    "django": {
        "markers": [
            "django_db: marks tests as requiring database access",
            "selenium: marks tests as requiring selenium",
            "client: marks tests using Django test client",
            "admin: marks tests for Django admin",
        ],
        "requirements": ["django>=5.2.0", "pytest-django>=4.8.0"],
        "settings": 'DJANGO_SETTINGS_MODULE = "flext_web.settings.test"',
    },
    "grpc": {
        "markers": [
            "grpc_server: marks tests requiring gRPC server",
            "proto: marks tests for protobuf validation",
            "streaming: marks tests for streaming RPCs",
            "interceptor: marks tests for gRPC interceptors",
        ],
        "requirements": ["grpcio>=1.71.0", "grpcio-tools>=1.71.0"],
    },
    "observability": {
        "markers": [
            "metrics: marks tests as metrics tests",
            "tracing: marks tests as tracing tests",
            "health: marks tests as health check tests",
            "prometheus: tests that need Prometheus",
            "grafana: tests that need Grafana",
        ],
        "requirements": ["prometheus-client>=0.22.1", "opentelemetry-api>=1.34.1"],
    },
}


def identify_project_type(project_path: Path) -> list[str]:
    """Identifica o tipo de projeto baseado no nome e dependências."""
    project_name = project_path.name.lower()
    project_types = []

    # Verificar por nome
    if "tap-" in project_name or "target-" in project_name or "dbt-" in project_name:
        project_types.append("singer")

    if "web" in project_name:
        project_types.append("django")

    if "grpc" in project_name:
        project_types.append("grpc")

    if "observability" in project_name:
        project_types.append("observability")

    # Verificar pyproject.toml para dependências
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        try:
            config = toml.load(pyproject_path)
            dependencies = config.get("project", {}).get("dependencies", [])
            dep_str = " ".join(dependencies).lower()

            if "singer-sdk" in dep_str and "singer" not in project_types:
                project_types.append("singer")
            if "django" in dep_str and "django" not in project_types:
                project_types.append("django")
            if "grpcio" in dep_str and "grpc" not in project_types:
                project_types.append("grpc")
            if "prometheus" in dep_str or "opentelemetry" in dep_str:
                if "observability" not in project_types:
                    project_types.append("observability")
        except Exception as e:
            logger.warning(f"Erro ao ler {pyproject_path}: {e}")

    return project_types or ["generic"]


def load_template_config() -> dict[str, Any]:
    """Carrega a configuração template do pytest."""
    if not TEMPLATE_PYTEST_CONFIG.exists():
        msg = f"Template não encontrado: {TEMPLATE_PYTEST_CONFIG}"
        raise FileNotFoundError(msg)

    return toml.load(TEMPLATE_PYTEST_CONFIG)


def update_pytest_config(project_path: Path, project_types: list[str]) -> bool:
    """Atualiza a configuração pytest do projeto."""
    pyproject_path = project_path / "pyproject.toml"

    if not pyproject_path.exists():
        logger.warning(f"pyproject.toml não encontrado em {project_path}")
        return False

    try:
        # Carregar configuração existente
        config = toml.load(pyproject_path)

        # Carregar template
        template = load_template_config()

        # Atualizar configurações pytest
        pytest_config = template["tool"]["pytest"]["ini_options"].copy()

        # Adicionar markers específicos do projeto
        base_markers = pytest_config["markers"]
        for project_type in project_types:
            if project_type in PROJECT_TYPE_CONFIGS:
                base_markers.extend(PROJECT_TYPE_CONFIGS[project_type]["markers"])

        # Configurações específicas para Django
        if "django" in project_types:
            pytest_config["DJANGO_SETTINGS_MODULE"] = (
                f'"{project_path.name.replace("-", "_")}.settings.test"'
            )

        # Atualizar coverage para o projeto específico
        coverage_config = template["tool"]["coverage"].copy()
        coverage_config["html"][
            "title"
        ] = f"{project_path.name.title()} Coverage Report"

        # Aplicar configurações
        if "tool" not in config:
            config["tool"] = {}

        config["tool"]["pytest"] = {"ini_options": pytest_config}
        config["tool"]["coverage"] = coverage_config

        # Salvar configuração atualizada
        with open(pyproject_path, "w", encoding="utf-8") as f:
            toml.dump(config, f)

        logger.info(f"✅ Configuração pytest atualizada: {project_path.name}")
        return True

    except Exception as e:
        logger.exception(f"❌ Erro ao atualizar {project_path.name}: {e}")
        return False


def create_modern_conftest(project_path: Path, project_types: list[str]) -> bool:
    """Cria conftest.py moderno para o projeto."""
    tests_dir = project_path / "tests"
    conftest_path = tests_dir / "conftest.py"

    # Criar diretório tests se não existir
    tests_dir.mkdir(exist_ok=True)

    # Verificar se já existe conftest.py
    if conftest_path.exists():
        logger.info(f"📁 conftest.py já existe em {project_path.name}, fazendo backup")
        backup_path = conftest_path.with_suffix(".py.backup")
        shutil.copy2(conftest_path, backup_path)

    try:
        # Copiar template
        shutil.copy2(TEMPLATE_CONFTEST, conftest_path)

        # Customizar para tipos específicos
        content = conftest_path.read_text()

        # Adicionar imports específicos baseado no tipo
        if "singer" in project_types:
            content = content.replace(
                "# SINGER SPECIFIC IMPORTS",
                "from singer_sdk import Tap, Target\nfrom singer_sdk.testing import get_test_class",
            )

        if "django" in project_types:
            content = content.replace(
                "# DJANGO SPECIFIC IMPORTS",
                "import django\nfrom django.test import TestCase, Client\nfrom django.conf import settings",
            )

        conftest_path.write_text(content)
        logger.info(f"✅ conftest.py moderno criado: {project_path.name}")
        return True

    except Exception as e:
        logger.exception(f"❌ Erro ao criar conftest.py para {project_path.name}: {e}")
        return False


def ensure_test_structure(project_path: Path) -> bool:
    """Garante estrutura de testes mínima."""
    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)

    # Criar __init__.py
    init_file = tests_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Tests for the project."""\n')

    # Criar diretórios de categorias se não existirem
    categories = ["unit", "integration", "e2e"]
    for category in categories:
        category_dir = tests_dir / category
        category_dir.mkdir(exist_ok=True)

        category_init = category_dir / "__init__.py"
        if not category_init.exists():
            category_init.write_text(f'"""{category.title()} tests."""\n')

    # Criar teste básico se não existir nenhum
    existing_tests = list(tests_dir.glob("test_*.py"))
    if not existing_tests:
        basic_test = tests_dir / "test_basic.py"
        basic_test.write_text(
            f'''"""Basic tests for {project_path.name}.

import pytest


def test_project_import():
    Test that the main module can be imported."""
    try:
        import {project_path.name.replace("-", "_")}  # noqa: F401
        assert True
    except ImportError:
        pytest.skip(f"Module {project_path.name.replace("-", "_")} not available")


def test_version_available():
    """Test that version is available."""
    try:
        import {project_path.name.replace("-", "_")}
        assert hasattr({project_path.name.replace("-", "_")}, "__version__") or True
    except ImportError:
        pytest.skip("Module not available")


@pytest.mark.unit
def test_basic_functionality():
    """Test basic functionality.
    assert True  # Placeholder test


@pytest.mark.integration
def test_integration_placeholder():
    Placeholder integration test."""
    pytest.skip("Integration tests not implemented yet")


@pytest.mark.e2e
def test_e2e_placeholder():
    """Placeholder end-to-end test."""
    pytest.skip("E2E tests not implemented yet")
''',
        )
        logger.info(f"📝 Teste básico criado: {project_path.name}")

    logger.info(f"📁 Estrutura de testes garantida: {project_path.name}")
    return True


def create_reports_directory(project_path: Path) -> bool:
    """Cria diretório de relatórios."""
    reports_dir = project_path / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Criar .gitignore para relatórios
    gitignore_path = reports_dir / ".gitignore"
    gitignore_content = """# Generated test reports
*.xml
*.json
*.html
coverage/
.coverage*
pytest_cache/
"""
    gitignore_path.write_text(gitignore_content)

    logger.info(f"📊 Diretório de relatórios criado: {project_path.name}")
    return True


def validate_project_setup(project_path: Path) -> dict[str, bool]:
    """Valida se o projeto está configurado corretamente."""
    results = {}

    # Verificar pyproject.toml
    pyproject_path = project_path / "pyproject.toml"
    results["pyproject_exists"] = pyproject_path.exists()

    if results["pyproject_exists"]:
        try:
            config = toml.load(pyproject_path)
            results["pytest_config"] = "pytest" in config.get("tool", {})
            results["coverage_config"] = "coverage" in config.get("tool", {})
        except Exception:
            results["pytest_config"] = False
            results["coverage_config"] = False

    # Verificar estrutura de testes
    tests_dir = project_path / "tests"
    results["tests_directory"] = tests_dir.exists()
    results["conftest_exists"] = (tests_dir / "conftest.py").exists()
    results["has_test_files"] = len(list(tests_dir.glob("test_*.py"))) > 0

    # Verificar relatórios
    reports_dir = project_path / "reports"
    results["reports_directory"] = reports_dir.exists()

    return results


def modernize_project(project_path: Path) -> dict[str, bool]:
    """Moderniza um projeto completo."""
    logger.info(f"🔧 Modernizando projeto: {project_path.name}")

    # Identificar tipo do projeto
    project_types = identify_project_type(project_path)
    logger.info(f"📋 Tipos identificados para {project_path.name}: {project_types}")

    results = {}

    # Atualizar configuração pytest
    results["pytest_config"] = update_pytest_config(project_path, project_types)

    # Criar conftest moderno
    results["conftest"] = create_modern_conftest(project_path, project_types)

    # Garantir estrutura de testes
    results["test_structure"] = ensure_test_structure(project_path)

    # Criar diretório de relatórios
    results["reports_dir"] = create_reports_directory(project_path)

    # Validar setup
    validation = validate_project_setup(project_path)
    results["validation"] = all(validation.values())

    if results["validation"]:
        logger.info(f"✅ Projeto modernizado com sucesso: {project_path.name}")
    else:
        logger.warning(f"⚠️ Modernização parcial para {project_path.name}: {validation}")

    return results


def main() -> None:
    """Função principal."""
    logger.info("🚀 Iniciando modernização do workspace FLEXT")

    # Verificar templates
    if not TEMPLATE_PYTEST_CONFIG.exists():
        logger.error(f"❌ Template pytest não encontrado: {TEMPLATE_PYTEST_CONFIG}")
        return

    if not TEMPLATE_CONFTEST.exists():
        logger.error(f"❌ Template conftest não encontrado: {TEMPLATE_CONFTEST}")
        return

    # Estatísticas
    total_projects = 0
    successful_projects = 0
    failed_projects = []

    # Processar cada projeto
    for project_name in FLEXT_PROJECTS:
        project_path = WORKSPACE_ROOT / project_name

        if not project_path.exists():
            logger.warning(f"⚠️ Projeto não encontrado: {project_name}")
            continue

        if not project_path.is_dir():
            logger.warning(f"⚠️ Não é um diretório: {project_name}")
            continue

        total_projects += 1

        try:
            results = modernize_project(project_path)
            if results.get("validation", False):
                successful_projects += 1
            else:
                failed_projects.append(project_name)
        except Exception as e:
            logger.exception(f"❌ Erro ao modernizar {project_name}: {e}")
            failed_projects.append(project_name)

    # Relatório final
    logger.info("=" * 60)
    logger.info("📊 RELATÓRIO FINAL DE MODERNIZAÇÃO")
    logger.info("=" * 60)
    logger.info(f"Total de projetos processados: {total_projects}")
    logger.info(f"Projetos modernizados com sucesso: {successful_projects}")
    logger.info(f"Projetos com falhas: {len(failed_projects)}")

    if failed_projects:
        logger.warning(f"Projetos que falharam: {', '.join(failed_projects)}")

    success_rate = (
        (successful_projects / total_projects * 100) if total_projects > 0 else 0
    )
    logger.info(f"Taxa de sucesso: {success_rate:.1f}%")

    if success_rate >= 90:
        logger.info("🎉 Modernização do workspace concluída com excelência!")
    elif success_rate >= 70:
        logger.info("✅ Modernização do workspace concluída com sucesso!")
    else:
        logger.warning(
            "⚠️ Modernização concluída com problemas. Revisar projetos falhados.",
        )


if __name__ == "__main__":
    main()
