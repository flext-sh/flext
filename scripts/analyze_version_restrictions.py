#!/usr/bin/env python3
"""
Analisa TODAS as dependências do workspace e identifica quem segura atualizações.
"""

import re
import sys
import tomllib
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_version_constraint(constraint: str) -> dict[str, str]:
    """Analisa constraint de versão."""
    constraint = constraint.strip()

    patterns = [
        (r"^==(.+)$", "exact"),  # ==1.2.3
        (r"^~=(.+)$", "compatible"),  # ~=1.2.3
        (r"^>=(.+),<(.+)$", "range"),  # >=1.0,<2.0
        (r"^>=(.+)$", "minimum"),  # >=1.0
        (r"^\^(.+)$", "caret"),  # ^1.2.3
        (r"^~(.+)$", "tilde"),  # ~1.2.3
        (r"^>(.+),<(.+)$", "range"),  # >1.0,<2.0
        (r"^<(.+)$", "maximum"),  # <2.0
        (r"^<=(.+)$", "maximum"),  # <=2.0
    ]

    for pattern, constraint_type in patterns:
        match = re.match(pattern, constraint)
        if match:
            return {
                "type": constraint_type,
                "version": match.group(1) if match.groups() else constraint,
                "raw": constraint,
            }

    # Se tem vírgula, provavelmente é um range complexo
    if "," in constraint:
        return {"type": "range", "version": constraint, "raw": constraint}

    return {"type": "unknown", "version": constraint, "raw": constraint}


def collect_all_dependencies(workspace: Path) -> dict[str, dict[str, str]]:
    """Coleta TODAS as dependências de TODOS os projetos."""
    all_deps: defaultdict[str, dict[str, str]] = defaultdict(dict)

    for pyproject in workspace.rglob("pyproject.toml"):
        # Pula diretórios não relevantes
        if any(
            part in pyproject.parts
            for part in [".venv", "backup", "tmp", "__pycache__", "node_modules"]
        ):
            continue

        try:
            with open(pyproject, "rb") as f:
                data = tomllib.load(f)

            project_name = pyproject.parent.name

            # Se o nome está vazio, usa o caminho relativo
            if not project_name or project_name == ".":
                project_name = str(pyproject.parent.relative_to(workspace))

            # Dependências principais
            deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for pkg, version in deps.items():
                if pkg != "python":  # Ignora python version
                    all_deps[pkg][project_name] = str(version)

            # Dependências de grupos
            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_name, group_data in groups.items():
                group_deps = group_data.get("dependencies", {})
                for pkg, version in group_deps.items():
                    all_deps[pkg][f"{project_name}[{group_name}]"] = str(version)

        except Exception as e:
            print(f"⚠️  Erro ao ler {pyproject}: {e}")

    return dict(all_deps)


def analyze_package_restrictions(versions: dict[str, str]) -> dict[str, Any]:
    """Analisa um pacote e identifica restrições."""
    analysis = {
        "total_projects": len(versions),
        "versions": versions,
        "parsed": {},
        "restrictions": {
            "exact": [],
            "maximum": [],
            "range_limited": [],
            "flexible": [],
        },
        "most_restrictive": None,
        "different_versions": set(),
    }

    for project, version in versions.items():
        parsed = parse_version_constraint(version)
        analysis["parsed"][project] = parsed

        # Classifica por tipo de restrição
        if parsed["type"] == "exact":
            analysis["restrictions"]["exact"].append(project)
        elif parsed["type"] == "maximum":
            analysis["restrictions"]["maximum"].append(project)
        elif parsed["type"] == "range" and "<" in parsed["raw"]:
            analysis["restrictions"]["range_limited"].append(project)
        else:
            analysis["restrictions"]["flexible"].append(project)

        # Coleta versões diferentes
        base_version = re.sub(r"[^\d.]", "", parsed["version"])
        if base_version:
            analysis["different_versions"].add(base_version)

    # Identifica o mais restritivo
    if analysis["restrictions"]["exact"]:
        analysis["most_restrictive"] = analysis["restrictions"]["exact"][0]
    elif analysis["restrictions"]["maximum"]:
        analysis["most_restrictive"] = analysis["restrictions"]["maximum"][0]
    elif analysis["restrictions"]["range_limited"]:
        analysis["most_restrictive"] = analysis["restrictions"]["range_limited"][0]

    return analysis


def main() -> int:
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analisa versões de dependências e identifica projetos restritivos"
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Diretório raiz do workspace (padrão: diretório atual)",
    )
    parser.add_argument("--package", help="Analisa apenas um pacote específico")
    parser.add_argument("--save-report", help="Salva relatório completo em arquivo")
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Mostra todos os pacotes, não apenas os problemáticos",
    )

    args = parser.parse_args()

    workspace = Path(args.workspace)

    print("📊 ANÁLISE DE RESTRIÇÕES DE VERSÃO")
    print("=" * 60)
    print(f"Workspace: {workspace.absolute()}")
    print()

    # Coleta todas as dependências
    print("🔍 Coletando dependências de todos os projetos...")
    all_deps = collect_all_dependencies(workspace)

    print(f"✅ Encontrados {len(all_deps)} pacotes únicos")
    print()

    # Analisa cada pacote
    problematic_packages = []
    all_analyses = {}

    for package in sorted(all_deps.keys()):
        if args.package and package != args.package:
            continue

        versions = all_deps[package]
        analysis = analyze_package_restrictions(versions)
        all_analyses[package] = analysis

        # Identifica pacotes problemáticos
        has_restrictions = (
            analysis["restrictions"]["exact"]
            or analysis["restrictions"]["maximum"]
            or analysis["restrictions"]["range_limited"]
        )

        has_conflicts = len(analysis["different_versions"]) > 1

        if has_restrictions or has_conflicts:
            problematic_packages.append((package, analysis))

    # Mostra resultados
    if problematic_packages or args.show_all:
        print("🚨 PACOTES COM RESTRIÇÕES OU CONFLITOS:")
        print("=" * 60)

        packages_to_show = (
            problematic_packages
            if not args.show_all
            else [(pkg, all_analyses[pkg]) for pkg in sorted(all_analyses.keys())]
        )

        for package, analysis in packages_to_show:
            print(f"\n📦 {package}")
            print(f"   Usado em {analysis['total_projects']} projetos")

            if len(analysis["different_versions"]) > 1:
                print(
                    f"   ⚠️  CONFLITO: {len(analysis['different_versions'])} versões diferentes!"
                )

            if analysis["restrictions"]["exact"]:
                print("   🔒 Versões EXATAS (mais restritivas):")
                for proj in analysis["restrictions"]["exact"]:
                    print(f"      - {proj}: {analysis['versions'][proj]}")

            if analysis["restrictions"]["maximum"]:
                print("   📍 Com limite MÁXIMO:")
                for proj in analysis["restrictions"]["maximum"]:
                    print(f"      - {proj}: {analysis['versions'][proj]}")

            if analysis["restrictions"]["range_limited"]:
                print("   📏 Ranges com limite superior:")
                for proj in analysis["restrictions"]["range_limited"]:
                    print(f"      - {proj}: {analysis['versions'][proj]}")

            if analysis["most_restrictive"]:
                print(f"   🚫 SEGURANDO ATUALIZAÇÕES: {analysis['most_restrictive']}")

    # Salva relatório se solicitado
    if args.save_report:
        report_path = Path(args.save_report)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("ANÁLISE DE RESTRIÇÕES DE VERSÃO\n")
            f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Workspace: {workspace.absolute()}\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Total de pacotes: {len(all_deps)}\n")
            f.write(f"Pacotes problemáticos: {len(problematic_packages)}\n\n")

            for package in sorted(all_deps.keys()):
                analysis = all_analyses.get(package)
                if not analysis:
                    continue

                f.write(f"\n{package}:\n")
                f.write(f"  Projetos: {analysis['total_projects']}\n")

                if analysis["most_restrictive"]:
                    f.write(f"  RESTRITIVO: {analysis['most_restrictive']}\n")

                f.writelines(
                    f"    {project}: {version}\n"
                    for project, version in sorted(analysis["versions"].items())
                )

        print(f"\n💾 Relatório salvo em: {report_path}")

    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO:")
    print(f"   Total de pacotes analisados: {len(all_deps)}")
    print(f"   Pacotes com restrições: {len(problematic_packages)}")

    # Top 5 projetos mais restritivos
    restrictive_count: defaultdict[str, int] = defaultdict(int)
    for analysis in all_analyses.values():
        if analysis["most_restrictive"]:
            # Remove sufixo [group] se existir
            proj = analysis["most_restrictive"].split("[")[0]
            restrictive_count[proj] += 1

    if restrictive_count:
        print("\n🏆 TOP PROJETOS MAIS RESTRITIVOS:")
        for proj, count in sorted(restrictive_count.items(), key=lambda x: -x[1])[:5]:
            print(f"   {proj}: segurando {count} pacotes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
