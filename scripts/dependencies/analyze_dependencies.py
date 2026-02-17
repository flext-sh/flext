#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-dependencies/SKILL.md
"""Script refatorado para analisar conflitos e bloqueadores de atualização.

Usa flext_quality.tools para análise modular e cache.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from flext_quality.tools import Colors, ConflictAnalyzer, print_colored


def main() -> int:
    """Analisa quem bloqueia atualizações de dependências."""
    print_colored("🔍 Analisando bloqueadores de atualização...\n", Colors.BLUE)

    # Workspace path
    workspace_path = Path.cwd()

    # Inicializa analisador
    analyzer = ConflictAnalyzer()

    # Análise direta sem cache
    def get_workspace_analysis() -> dict[str, object]:
        result = analyzer.analyze_dependencies(str(workspace_path))
        if result.is_success:
            dependencies = result.value or []
            return {
                "stats": {"dependencies_analyzed": len(dependencies)},
                "version_conflicts": [],
                "dependency_details": dependencies,
            }
        return {
            "error": result.error or "Analysis failed",
            "stats": {},
            "version_conflicts": [],
        }

    # Executa análise
    print_colored("📊 Analisando workspace...", Colors.CYAN)
    analysis = get_workspace_analysis()

    # Mostra estatísticas
    analysis["stats"]
    print_colored("\n📈 Estatísticas Gerais:", Colors.BLUE)

    # Mostra conflitos de versão
    if analysis["version_conflicts"]:
        version_conflicts = analysis.get("version_conflicts", {})
        conflicts_count = (
            len(version_conflicts) if isinstance(version_conflicts, dict) else 0
        )
        print_colored(
            f"\n⚠️ Conflitos de Versão ({conflicts_count} pacotes):",
            Colors.YELLOW,
        )

        # Ordena por severidade
        version_conflicts = analysis.get("version_conflicts", {})
        if isinstance(version_conflicts, dict):
            conflicts_sorted = sorted(
                version_conflicts.items(),
                key=lambda x: (x[1].get("severity", "low"), len(x[1]["projects"])),
                reverse=True,
            )
        else:
            conflicts_sorted: list[object] = []
        # Mostra top 10 ou todos se --all
        show_all = "--all" in sys.argv
        limit = len(conflicts_sorted) if show_all else min(10, len(conflicts_sorted))

        for _i, (_package, conflict_data) in enumerate(conflicts_sorted[:limit]):
            conflict_data.get("severity", "medium")

            # Mostra versões
            for _project, _version in sorted(conflict_data["projects"].items()):
                pass

    # Mostra bloqueadores
    if analysis["update_blockers"]:
        print_colored("\n🚫 Principais Bloqueadores de Atualização:", Colors.RED)

        # Ordena por número de projetos bloqueados
        update_blockers = analysis.get("update_blockers", {})
        if isinstance(update_blockers, dict):
            blockers_sorted = sorted(
                update_blockers.items(),
                key=lambda x: len(x[1]["blocking_projects"]),
                reverse=True,
            )
        else:
            blockers_sorted: list[object] = []
        # Top 10 bloqueadores
        for _i, (_package, blocker_data) in enumerate(blockers_sorted[:10]):
            # Agrupa por constraint
            for projects in blocker_data["constraints"].values():
                if len(projects) > 3:
                    pass

    # Mostra resoluções sugeridas
    if analysis["suggested_resolutions"] and "--suggest" in sys.argv:
        print_colored("\n💡 Resoluções Sugeridas:", Colors.GREEN)

        suggested_resolutions = analysis.get("suggested_resolutions", {})
        if isinstance(suggested_resolutions, dict):
            for _package, _suggestion in sorted(suggested_resolutions.items())[:10]:
                pass

    # Gera relatório completo se solicitado
    if "--report" in sys.argv:
        report_path = Path("conflict_report.md")
        # Generate simple report from analysis data
        report_lines = [
            "# Dependency Conflict Analysis Report",
            "",
            f"**Total Projects Analyzed:** {analysis.get('total_projects', 0)}",
            f"**Conflicts Found:** {analysis.get('conflict_count', 0)}",
            "",
            "## Analysis Summary",
            f"```json\n{json.dumps(analysis, indent=2)}\n```",
        ]
        report = "\n".join(report_lines)

        Path(report_path).write_text(report, encoding="utf-8")

        print_colored(f"\n📄 Relatório completo salvo em: {report_path}", Colors.GREEN)

    # Mostra cache stats se verboso
    if "-v" in sys.argv or "--verbose" in sys.argv:
        print_colored(
            "\n📊 Cache: Análise em cache para melhor performance",
            Colors.CYAN,
        )

    # Dicas finais
    print_colored("\n💡 Dicas:", Colors.CYAN)

    return 0


if __name__ == "__main__":
    sys.exit(main())
