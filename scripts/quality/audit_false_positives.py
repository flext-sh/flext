#!/usr/bin/env python3
"""AUDITORIA MANUAL CRÍTICA - Análise de Falsos Positivos.

Este script examina cada dependência detectada como "faltante" para
identificar falsos positivos antes de permitir modificações reais.

OBJETIVO: Zero falsos positivos antes de remover o lock de segurança.
"""

import importlib.util
import sys
from pathlib import Path

from flext_tools import Colors, DependencyDiscovery, get_stdlib_modules, print_colored


class FalsePositiveAuditor:
    """Auditor manual para identificar falsos positivos com precisão."""

    def __init__(self) -> None:
        self.stdlib_modules = get_stdlib_modules()
        self.discovery = DependencyDiscovery()

        # Módulos que sabemos que são internos do FLEXT
        self.known_flext_modules = {
            "flext_core",
            "flext_auth",
            "flext_api",
            "flext_grpc",
            "flext_web",
            "flext_cli",
            "flext_plugin",
            "flext_observability",
            "flext_meltano",
            "flext_ldap",
            "flext_quality",
            "flext_db_oracle",
            "flext_tap_ldap",
            "flext_tap_oracle_oic",
            "flext_tap_oracle_wms",
            "flext_target_ldap",
            "flext_target_oracle",
            "flext_target_oracle_oic",
            "flext_target_oracle_wms",
            "flext_dbt_ldap",
            "flext_oracle_oic_ext",
        }

        # Módulos que são aliases ou imports especiais
        self.known_aliases = {
            "cv2": "opencv-python",
            "PIL": "Pillow",
            "yaml": "PyYAML",
            "dotenv": "python-dotenv",
            "jwt": "PyJWT",
            "ldap3": "ldap3",
            "ldap": "python-ldap",
        }

    def audit_project_dependencies(
        self,
        project_path: Path,
    ) -> dict[str, list[FlextTypes.Core.Dict]]:
        """Audita dependências de um projeto específico.

        Returns:
            Dict com categorização detalhada dos imports encontrados

        """
        print_colored(f"\n🔍 AUDITANDO: {project_path.name}", Colors.BLUE)
        print_colored("=" * 60, Colors.BLUE)

        # Descobre dependências usando o sistema atual
        dependencies = self.discovery.discover_project_dependencies(
            project_path,
            include_dev=True,
            include_test=True,
        )

        # Analisa cada dependência encontrada
        analysis: dict[str, list[FlextTypes.Core.Dict]] = {
            "stdlib": [],  # Módulos da standard library
            "flext_internal": [],  # Módulos internos do FLEXT
            "relative_imports": [],  # Imports relativos locais
            "aliases": [],  # Aliases conhecidos (cv2, PIL, etc)
            "legitimate": [],  # Dependências realmente faltantes
            "suspicious": [],  # Possíveis problemas
            "unknown": [],  # Requer investigação manual
        }

        all_imports = set()
        for deps in dependencies.values():
            all_imports.update(deps)

        print_colored(
            f"📦 Total de imports únicos detectados: {len(all_imports)}",
            Colors.CYAN,
        )

        for import_name in sorted(all_imports):
            category = self._categorize_import(import_name, project_path)
            analysis[category].append(
                {
                    "import": import_name,
                    "reason": self._get_categorization_reason(
                        import_name,
                        category,
                        project_path,
                    ),
                },
            )

        # Mostra resultados da auditoria
        self._print_audit_results(analysis)

        return analysis

    def _categorize_import(self, import_name: str, project_path: Path) -> str:
        """Categoriza um import específico."""
        # 1. Standard library
        if import_name in self.stdlib_modules:
            return "stdlib"

        # 2. Módulos FLEXT conhecidos
        if import_name in self.known_flext_modules:
            return "flext_internal"

        # 3. Padrões FLEXT (flext_*, flext-*)
        if (
            import_name.startswith(("flext_", "flext-"))
            or "flext" in import_name.lower()
        ):
            return "flext_internal"

        # 4. Aliases conhecidos
        if import_name in self.known_aliases:
            return "aliases"

        # 5. Imports relativos ou locais
        if self._is_local_module(import_name, project_path):
            return "relative_imports"

        # 6. Verifica se é realmente necessário
        if self._is_legitimate_dependency(import_name, project_path):
            return "legitimate"

        # 7. Padrões suspeitos
        if self._is_suspicious_import(import_name):
            return "suspicious"

        # 8. Requer investigação
        return "unknown"

    def _is_local_module(self, import_name: str, project_path: Path) -> bool:
        """Verifica se é módulo local do projeto."""
        # Verifica se existe arquivo .py correspondente
        possible_paths = [
            project_path / "src" / f"{import_name}.py",
            project_path / "src" / import_name / "__init__.py",
            project_path / f"{import_name}.py",
            project_path / import_name / "__init__.py",
        ]

        for path in possible_paths:
            if path.exists():
                return True

        # Verifica se é parte do próprio projeto
        return project_path.name.replace("-", "_") in import_name

    def _is_legitimate_dependency(
        self,
        import_name: str,
        _project_path: Path,
    ) -> bool:
        """Verifica se é dependência legítima que deve estar no pyproject.toml."""
        # Lista de dependências comuns que são legítimas
        common_packages = {
            "requests",
            "urllib3",
            "certifi",
            "charset-normalizer",
            "idna",
            "click",
            "colorama",
            "packaging",
            "setuptools",
            "wheel",
            "pip",
            "pydantic",
            "fastapi",
            "uvicorn",
            "starlette",
            "typing-extensions",
            "sqlalchemy",
            "alembic",
            "psycopg2-binary",
            "redis",
            "celery",
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "mypy",
            "django",
            "djangorestframework",
            "django-cors-headers",
            "pandas",
            "numpy",
            "scipy",
            "matplotlib",
            "seaborn",
            "aiohttp",
            "httpx",
            "websockets",
            "pyyaml",
            "toml",
            "tomli",
            "python-dotenv",
            "python-multipart",
            "jinja2",
            "markupsafe",
            "cryptography",
            "bcrypt",
            "passlib",
            "python-jose",
            "authlib",
            "loguru",
            "structlog",
            "rich",
            "typer",
            "tqdm",
            "progressbar2",
        }

        if import_name in common_packages:
            return True

        # Verifica se já está instalado no ambiente atual
        try:
            spec = importlib.util.find_spec(import_name)
            if spec and spec.origin:
                # Se está instalado mas não no pyproject.toml, pode ser legítimo
                return True
        except (ImportError, ValueError, AttributeError):
            pass

        return False

    def _is_suspicious_import(self, import_name: str) -> bool:
        """Identifica imports suspeitos que provavelmente são falsos positivos."""
        suspicious_patterns = [
            # Muito curtos (provavelmente aliases)
            len(import_name) <= 2,
            # Contém caracteres especiais suspeitos
            any(c in import_name for c in [".", "-", "_"] * 3),
            # Padrões de código gerado
            import_name.startswith("__"),
            import_name.endswith("__"),
            # Padrões de test
            "test" in import_name.lower() and len(import_name) < 6,
            # Números no nome (geralmente interno)
            any(c.isdigit() for c in import_name),
        ]

        return any(suspicious_patterns)

    def _get_categorization_reason(
        self,
        import_name: str,
        category: str,
        project_path: Path,
    ) -> str:
        """Retorna razão detalhada da categorização."""
        if category == "stdlib":
            return "Módulo da standard library Python"
        if category == "flext_internal":
            return "Módulo interno do ecossistema FLEXT"
        if category == "relative_imports":
            return f"Import local/relativo do projeto {project_path.name}"
        if category == "aliases":
            real_package = self.known_aliases.get(import_name, "")
            return f"Alias conhecido para {real_package}"
        if category == "legitimate":
            return "Dependência legítima que deve estar no pyproject.toml"
        if category == "suspicious":
            return "Padrão suspeito - provavelmente falso positivo"
        return "Requer investigação manual"

    def _print_audit_results(
        self,
        analysis: dict[str, list[FlextTypes.Core.Dict]],
    ) -> None:
        """Imprime resultados da auditoria de forma organizada."""
        total = sum(len(items) for items in analysis.values())

        print_colored("\n📊 RESULTADOS DA AUDITORIA:", Colors.BLUE)
        print_colored("-" * 40, Colors.BLUE)

        for category, items in analysis.items():
            if not items:
                continue

            # Cores por categoria
            colors = {
                "stdlib": Colors.GREEN,
                "flext_internal": Colors.GREEN,
                "relative_imports": Colors.GREEN,
                "aliases": Colors.CYAN,
                "legitimate": Colors.YELLOW,
                "suspicious": Colors.RED,
                "unknown": Colors.MAGENTA,
            }

            color = colors.get(category, Colors.GRAY)
            count = len(items)
            percentage = (count / total * 100) if total > 0 else 0

            print_colored(f"\n{category.upper()}: {count} ({percentage:.1f}%)", color)

            for _item in items[:5]:  # Mostra apenas primeiros 5
                pass

            if len(items) > 5:
                pass

        # Resumo crítico
        false_positives = (
            len(analysis["stdlib"])
            + len(analysis["flext_internal"])
            + len(analysis["relative_imports"])
            + len(analysis["suspicious"])
        )

        legitimate_missing = len(analysis["legitimate"])
        needs_investigation = len(analysis["unknown"]) + len(analysis["aliases"])

        print_colored("\n🎯 RESUMO CRÍTICO:", Colors.BLUE)
        print_colored(
            f"✅ Falsos positivos identificados: {false_positives}",
            Colors.GREEN,
        )
        print_colored(
            f"⚠️ Dependências realmente faltantes: {legitimate_missing}",
            Colors.YELLOW,
        )
        print_colored(f"🔍 Requer investigação: {needs_investigation}", Colors.MAGENTA)


def audit_workspace() -> tuple[
    dict[str, dict[str, list[FlextTypes.Core.Dict]]],
    dict[str, set[str]],
]:
    """Audita todo o workspace FLEXT."""
    print_colored("🔍 AUDITORIA COMPLETA DE FALSOS POSITIVOS", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)
    print_colored(
        "OBJETIVO: Identificar TODOS os falsos positivos antes de permitir modificações",
        Colors.YELLOW,
    )
    workspace_path = Path.cwd()
    auditor: FalsePositiveAuditor = FalsePositiveAuditor()

    # Encontra projetos Python
    projects: list[Path] = [
        project_dir
        for project_dir in workspace_path.iterdir()
        if project_dir.is_dir()
        and project_dir.name.startswith("flext-")
        and (project_dir / "pyproject.toml").exists()
    ]

    if not projects:
        print_colored("❌ Nenhum projeto FLEXT encontrado!", Colors.RED)
        return {}, {}

    print_colored(
        f"📁 Encontrados {len(projects)} projetos para auditoria",
        Colors.CYAN,
    )

    # Auditoria consolidada
    global_analysis: dict[str, set[str]] = {
        "stdlib": set(),
        "flext_internal": set(),
        "relative_imports": set(),
        "aliases": set(),
        "legitimate": set(),
        "suspicious": set(),
        "unknown": set(),
    }

    project_details: dict[str, dict[str, list[FlextTypes.Core.Dict]]] = {}

    for project_path in projects:
        try:
            analysis = auditor.audit_project_dependencies(project_path)
            project_details[project_path.name] = analysis

            # Consolida resultados globais
            for category, items in analysis.items():
                for item in items:
                    global_analysis[category].add(item["import"])

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Erro ao auditar {project_path.name}: {e}", Colors.RED)

    # Relatório final consolidado
    print_colored("\n📋 RELATÓRIO FINAL CONSOLIDADO", Colors.BLUE)
    print_colored("=" * 60, Colors.BLUE)

    total_imports = sum(len(items) for items in global_analysis.values())

    for category, items_set in global_analysis.items():
        if not items_set:
            continue

        count = len(items_set)
        percentage = (count / total_imports * 100) if total_imports > 0 else 0

        print_colored(
            f"{category.upper()}: {count} únicos ({percentage:.1f}%)",
            Colors.CYAN,
        )

    # Estatísticas críticas
    false_positives = (
        len(global_analysis["stdlib"])
        + len(global_analysis["flext_internal"])
        + len(global_analysis["relative_imports"])
        + len(global_analysis["suspicious"])
    )

    legitimate = len(global_analysis["legitimate"])
    investigation = len(global_analysis["unknown"]) + len(global_analysis["aliases"])

    print_colored("\n🎯 ESTATÍSTICAS CRÍTICAS:", Colors.BLUE)
    print_colored(f"Total de imports únicos detectados: {total_imports}", Colors.CYAN)
    print_colored(
        "Falsos positivos confirmados: "
        f"{false_positives} ({false_positives / total_imports * 100:.1f}%)",
        Colors.GREEN,
    )
    print_colored(
        f"Dependências legítimas faltantes: {legitimate} ({legitimate / total_imports * 100:.1f}%)",
        Colors.YELLOW,
    )
    print_colored(
        f"Requer investigação manual: {investigation} ({investigation / total_imports * 100:.1f}%)",
        Colors.MAGENTA,
    )

    # Recomendações
    print_colored("\n📋 RECOMENDAÇÕES:", Colors.BLUE)

    if false_positives > legitimate:
        print_colored(
            "⚠️ ALTA taxa de falsos positivos - filtros precisam melhorar",
            Colors.YELLOW,
        )

    if investigation > 0:
        print_colored(
            f"🔍 {investigation} imports precisam de investigação manual",
            Colors.MAGENTA,
        )

    if legitimate == 0:
        print_colored(
            "✅ Nenhuma dependência legítima detectada - possível problema de detecção",
            Colors.GREEN,
        )
    elif legitimate < 10:
        print_colored(
            f"✅ Apenas {legitimate} dependências realmente faltantes",
            Colors.GREEN,
        )
    else:
        print_colored(
            f"⚠️ {legitimate} dependências podem estar realmente faltando",
            Colors.YELLOW,
        )

    return project_details, global_analysis


def main() -> int:
    """Executa auditoria manual."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_colored("🔍 Auditoria de Falsos Positivos", Colors.BLUE)
        return 0

    _project_details, _global_analysis = audit_workspace()

    print_colored("\n✅ Auditoria manual concluída!", Colors.GREEN)
    print_colored(
        "📋 Revise os resultados antes de proceder com modificações",
        Colors.CYAN,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
