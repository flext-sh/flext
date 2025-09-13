#!/usr/bin/env python3
"""Descobrir e analisar dependências faltantes em projetos FLEXT.

Script que usa flext_tools.DependencyDiscovery para encontrar dependências
faltantes baseado em análise AST de imports Python.
"""

from __future__ import annotations

import sys
from pathlib import Path

from src.flext_tools import Colors, print_colored
from src.flext_tools.discovery_base import DependencyDiscovery
from src.flext_tools.script_base import FlextScript, ScriptMetadata

from ..common import discover_projects


class MissingDependenciesDiscoverer(FlextScript):
    """Descobre dependências faltantes usando flext_tools."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="discover_missing_deps",
            description="Descobrir e analisar dependências faltantes em projetos FLEXT",
            category="dependencies",
            version="2.0.0",
        )

    def validate_preconditions(self) -> bool:
        """Validar pré-condições."""
        workspace_root = Path.cwd()

        # Verificar se estamos no workspace FLEXT
        flext_projects = [
            p
            for p in workspace_root.iterdir()
            if p.is_dir()
            and p.name.startswith("flext-")
            and (p / "pyproject.toml").exists()
        ]

        if not flext_projects:
            print_colored("❌ Execute do diretório raiz do workspace FLEXT", Colors.RED)
            return False

        print_colored(
            f"✅ Encontrados {len(flext_projects)} projetos FLEXT",
            Colors.GREEN,
        )
        return True

    def execute_main_logic(self, **kwargs: object) -> bool:
        """Executar descoberta de dependências faltantes."""
        try:
            workspace_root = Path.cwd()
            detailed = kwargs.get("verbose", False)
            projects_filter = kwargs.get("projects")
            if projects_filter is not None and not isinstance(projects_filter, str):
                projects_filter = None

            print_colored("🔍 DESCOBERTA DE DEPENDÊNCIAS FALTANTES", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Usar DependencyDiscovery do flext_tools
            discovery = DependencyDiscovery(resolve_transitive=True)

            # Descobrir projetos
            projects = self._discover_projects(workspace_root, projects_filter)

            total_missing = 0
            projects_with_issues = 0

            # Analisar cada projeto
            for project_path in projects:
                project_name = project_path.name

                print_colored(f"\n📦 Analisando {project_name}...", Colors.BLUE)

                # Usar flext_tools para descobrir dependências
                missing_deps = discovery.discover_project_dependencies(
                    project_path,
                    include_dev=True,
                    include_test=True,
                )

                # Processar resultados
                project_total = sum(len(deps) for deps in missing_deps.values())

                if project_total > 0:
                    projects_with_issues += 1
                    total_missing += project_total

                    print_colored(
                        f"  ⚠️ {project_total} dependências faltantes encontradas",
                        Colors.YELLOW,
                    )

                    if detailed:
                        self._print_detailed_missing(missing_deps)
                else:
                    print_colored(
                        "  ✅ Todas as dependências estão presentes",
                        Colors.GREEN,
                    )

            # Resumo final
            self._print_summary(len(projects), projects_with_issues, total_missing)

            return True

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Erro durante análise: {e}", Colors.RED)
            return False

    def _discover_projects(
        self,
        workspace_root: Path,
        projects_filter: str | None = None,
    ) -> list[Path]:
        """Descobrir projetos para analisar."""
        return discover_projects(workspace_root, projects_filter)

    def _print_detailed_missing(self, missing_deps: dict[str, set[str]]) -> None:
        """Imprimir detalhes das dependências faltantes."""
        for category, deps in missing_deps.items():
            if deps:
                print_colored(f"    📋 {category.title()}:", Colors.CYAN)
                for _dep in sorted(deps):
                    pass

    def _print_summary(
        self,
        _total_projects: int,
        projects_with_issues: int,
        total_missing: int,
    ) -> None:
        """Imprimir resumo final."""
        print_colored("\n📊 RESUMO DA ANÁLISE", Colors.BLUE)
        print_colored("=" * 40, Colors.BLUE)

        if total_missing == 0:
            print_colored(
                "\n🎉 Todos os projetos estão com dependências completas!",
                Colors.GREEN,
            )
        else:
            print_colored(
                f"\n⚠️ {projects_with_issues} projetos precisam de atenção",
                Colors.YELLOW,
            )
            print_colored("\n💡 Sugestões:", Colors.CYAN)

    def create_parser(self) -> object:
        """Criar parser com argumentos específicos."""
        parser = super().create_parser()

        parser.add_argument(
            "--projects",
            help="Filtrar projetos específicos (separados por vírgula)",
        )

        return parser

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Função principal."""
    script = MissingDependenciesDiscoverer()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
