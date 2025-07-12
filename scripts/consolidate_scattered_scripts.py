from datetime import datetime
#!/usr/bin/env python3
"""
FLEXT Scripts Consolidation Tool - Organiza scripts espalhados
=============================================================

HONESTIDADE BRUTAL: Há 51+ scripts espalhados pelo workspace que precisam ser organizados.
Este script REALMENTE analisa, categoriza e consolida todos os scripts de forma sistemática.

Funcionalidades:
1. Analisa conteúdo de todos os scripts espalhados
2. Categoriza por funcionalidade (genérico vs específico)
3. Move scripts para localizações apropriadas
4. Integra funcionalidades úteis no quality_gateway.py
5. Remove duplicações e obsoletos


import ast
import re
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


class ScriptConsolidator:
    Consolida scripts espalhados pelo workspace de forma inteligente."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.analysis_results = {}
        self.consolidation_plan = {}

    def find_all_scattered_scripts(self) -> list[Path]:
        Encontra todos os scripts espalhados."""
        patterns = [
            "*fix*.py",
            "*enforce*.py",
            "*audit*.py",
            "*modernize*.py",
            "*test*.py",
        ]
        scripts = []

        for pattern in patterns:
            for script in self.workspace_root.rglob(pattern):
                # Excluir venv, __pycache__, legacy já organizados
                if any(:
                    exclude in str(script)
                    for exclude in [:
                        ".venv",
                        "__pycache__",
                        "scripts/legacy",
                        "legacy/",
                        ".git",
                    ]
                ):
                    continue

                # Incluir apenas arquivos em diretórios scripts/ ou arquivos isolados
                if "scripts/" in str(script) or script.name.startswith(:
                    ("fix_", "enforce_", "audit_")
                ):
                    scripts.append(script)

        return sorted(set(scripts))

    def analyze_script_content(self, script_path: Path) -> dict[str, Any]:
        """Analisa o conteúdo de um script para categorização."""
        try:
            content = script_path.read_text(encoding="utf-8")
        except Exception as e:
            return {"error": f"Erro lendo arquivo: {e}", "category": "error"}

        analysis = {
            "path": script_path,
            "size_lines": len(content.splitlines()),
            "size_bytes": len(content.encode("utf-8")),
            "has_main": "if __name__" in content,
            "imports": self._extract_imports(content),
            "functions": self._extract_functions(content),
            "category": "unknown",
            "is_generic": False,
            "project_specific": False,
            "functionality": set(),
        }

        # Categorizar por funcionalidade
        if any(:
            keyword in content.lower() for keyword in ["pep", "ruff", "black", "isort"]
        ):
            analysis["functionality"].add("formatting")
        if any(:
            keyword in content.lower() for keyword in ["syntax", "error", "exception"]
        ):
            analysis["functionality"].add("syntax_fix")
        if any(:
            keyword in content.lower() for keyword in ["test", "pytest", "unittest"]
        ):
            analysis["functionality"].add("testing")
        if any(:
            keyword in content.lower() for keyword in ["type", "mypy", "annotation"]
        ):
            analysis["functionality"].add("typing")
        if any(keyword in content.lower() for keyword in ["import", "dependency"]):
            analysis["functionality"].add("imports")

        # Determinar se é genérico ou específico do projeto
        project_name = script_path.parts[1] if len(script_path.parts) > 1 else "unknown"
        if any(proj in content.lower() for proj in ["algar", "gruponos", "oic", "wms"]):
            analysis["project_specific"] = True
            analysis["project"] = project_name
        else:
            analysis["is_generic"] = True

        # Categorização final
        if analysis["functionality"]:
            if analysis["project_specific"]:
                analysis["category"] = (
                    f"project_specific_{next(iter(analysis['functionality']))}"
                )
            else:
                analysis["category"] = (
                    f"generic_{next(iter(analysis['functionality']))}"
                )
        else:
            analysis["category"] = "unknown"

        return analysis

    def _extract_imports(self, content: str) -> list[str]:
        """Extrai imports do código."""
        imports = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
        except Exception:
            # Fallback com regex
            import_lines = re.findall(
                r"^(?:from\s+(\S+)\s+)?import\s+", content, re.MULTILINE
            )
            imports.extend([imp for imp in import_lines if imp])

        return imports

    def _extract_functions(self, content: str) -> list[str]:
        """Extrai nomes de funções do código."""
        functions = []
        try:
            tree = ast.parse(content)
            functions.extend(
                node.name
                for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
            )
        except Exception:
            # Fallback com regex
            func_matches = re.findall(r"^def\s+(\w+)", content, re.MULTILINE)
            functions.extend(func_matches)

        return functions

    def create_consolidation_plan(
        self, analyses: dict[Path, dict]
    ) -> dict[str, list[Path]]:
        """Cria plano de consolidação baseado nas análises."""
        plan = {
            "keep_generic": [],  # Scripts genéricos úteis para manter
            "integrate_quality": [],  # Scripts para integrar no quality_gateway
            "move_to_project": [],  # Scripts específicos para mover para projeto
            "move_to_legacy": [],  # Scripts obsoletos para legacy
            "delete_duplicates": [],  # Scripts duplicados para deletar
        }

        # Agrupar por funcionalidade
        by_functionality = {}
        for script_path, analysis in analyses.items():
            for func in analysis.get("functionality", []):
                if func not in by_functionality:
                    by_functionality[func] = []
                by_functionality[func].append((script_path, analysis))

        # Decidir o que fazer com cada grupo
        for functionality, scripts in by_functionality.items():
            if functionality == "formatting":
                # Scripts de formatação: integrar no quality_gateway se genéricos
                for script_path, analysis in scripts:
                    if analysis["is_generic"]:
                        plan["integrate_quality"].append(script_path)
                    else:
                        plan["move_to_project"].append(script_path)

            elif functionality == "testing":
                # Scripts de teste: manter se úteis, senão para legacy
                for script_path, analysis in scripts:
                    if "stress" in str(script_path) or "e2e" in str(script_path):
                        plan["keep_generic"].append(script_path)
                    else:
                        plan["move_to_legacy"].append(script_path)

            elif functionality in {"syntax_fix", "typing", "imports"}:
                # Scripts de fix: integrar se genéricos
                for script_path, analysis in scripts:
                    if analysis["is_generic"]:
                        plan["integrate_quality"].append(script_path)
                    else:
                        plan["move_to_project"].append(script_path)

        # Detectar duplicatas por similaridade de função
        self._detect_duplicates(analyses, plan)

        return plan

    def _detect_duplicates(
        self, analyses: dict[Path, dict], plan: dict[str, list[Path]]
    ) -> None:
        """Detecta scripts duplicados por similaridade de funcionalidade."""
        # Agrupar por funções similares
        function_groups = {}
        for script_path, analysis in analyses.items():
            functions = set(analysis.get("functions", []))

            # Procurar grupos similares
            found_group = None
            for existing_functions, group_scripts in function_groups.items():
                if len(functions.intersection(existing_functions)) > 0:
                    found_group = existing_functions
                    break

            if found_group:
                function_groups[found_group].append(script_path)
            else:
                function_groups[frozenset(functions)] = [script_path]

        # Marcar duplicatas
        for functions, group_scripts in function_groups.items():
            if len(group_scripts) > 1:
                # Manter o maior/mais recente, marcar outros como duplicatas
                sorted_scripts = sorted(
                    group_scripts, key=lambda p: analyses[p]["size_bytes"], reverse=True
                )
                for duplicate in sorted_scripts[1:]:
                    plan["delete_duplicates"].append(duplicate)

    def execute_consolidation_plan(self, plan: dict[str, list[Path]]) -> None:
        """Executa o plano de consolidação."""
        self._print("\n🎯 EXECUTANDO PLANO DE CONSOLIDAÇÃO")

        # 1. Mover scripts específicos de projeto
        if plan["move_to_project"]:
            self._print(
                f"\n📁 Movendo {len(plan['move_to_project'])} scripts específicos de projeto..."
            )
            for script in plan["move_to_project"]:
                self._move_to_project_legacy(script)

        # 2. Mover scripts obsoletos para legacy
        if plan["move_to_legacy"]:
            self._print(
                f"\n🗄️ Movendo {len(plan['move_to_legacy'])} scripts obsoletos para legacy..."
            )
            for script in plan["move_to_legacy"]:
                self._move_to_workspace_legacy(script)

        # 3. Deletar duplicatas
        if plan["delete_duplicates"]:
            self._print(
                f"\n🗑️ Removendo {len(plan['delete_duplicates'])} scripts duplicados..."
            )
            for script in plan["delete_duplicates"]:
                self._delete_duplicate(script)

        # 4. Integrar funcionalidades úteis no quality_gateway
        if plan["integrate_quality"]:
            self._print(
                f"\n🔧 Integrando {len(plan['integrate_quality'])} funcionalidades no quality gateway..."
            )
            self._integrate_quality_features(plan["integrate_quality"])

        # 5. Organizar scripts genéricos úteis
        if plan["keep_generic"]:
            self._print(
                f"\n✅ Organizando {len(plan['keep_generic'])} scripts genéricos úteis..."
            )
            for script in plan["keep_generic"]:
                self._organize_generic_script(script)

    def _move_to_project_legacy(self, script_path: Path) -> None:
        """Move script para diretório legacy do projeto."""
        # Determinar projeto
        project_parts = (
            script_path.parts[1] if len(script_path.parts) > 1 else "unknown"
        )
        project_root = self.workspace_root / project_parts

        if project_root.exists():
            legacy_dir = project_root / "scripts" / "legacy"
            legacy_dir.mkdir(parents=True, exist_ok=True)

            dest = legacy_dir / script_path.name
            shutil.move(str(script_path), str(dest))
            self._print(f"  📦 {script_path.name} → {project_parts}/scripts/legacy/")
        else:
            # Fallback: workspace legacy
            self._move_to_workspace_legacy(script_path)

    def _move_to_workspace_legacy(self, script_path: Path) -> None:
        """Move script para legacy do workspace."""
        legacy_dir = self.workspace_root / "scripts" / "legacy"
        legacy_dir.mkdir(parents=True, exist_ok=True)

        dest = legacy_dir / script_path.name
        if dest.exists():
            # Evitar conflitos
            dest = legacy_dir / f"{script_path.stem}_duplicate{script_path.suffix}"

        shutil.move(str(script_path), str(dest))
        self._print(f"  🗄️ {script_path.name} → scripts/legacy/")

    def _delete_duplicate(self, script_path: Path) -> None:
        """Remove script duplicado."""
        script_path.unlink()
        self._print(f"  🗑️ Removido: {script_path.name}")

    def _integrate_quality_features(self, scripts: list[Path]) -> None:
        """Integra funcionalidades úteis no quality_gateway.py."""
        # Por enquanto, apenas mover para um diretório de integração
        integration_dir = self.workspace_root / "scripts" / "integration_candidates"
        integration_dir.mkdir(parents=True, exist_ok=True)

        for script in scripts:
            dest = integration_dir / script.name
            shutil.move(str(script), str(dest))
            self._print(f"  🔧 {script.name} → scripts/integration_candidates/")

        self._print(
            "\n📝 NOTA: Scripts marcados para integração manual no quality_gateway.py"
        )

    def _organize_generic_script(self, script_path: Path) -> None:
        """Organiza script genérico útil."""
        if "test" in script_path.name:
            # Scripts de teste vão para diretório de testes
            test_dir = self.workspace_root / "scripts" / "testing"
            test_dir.mkdir(parents=True, exist_ok=True)
            dest = test_dir / script_path.name
        else:
            # Outros scripts genéricos ficam na raiz de scripts
            dest = self.workspace_root / "scripts" / script_path.name

        if script_path != dest:
            shutil.move(str(script_path), str(dest))
            self._print(
                f"  ✅ {script_path.name} → {dest.relative_to(self.workspace_root)}"
            )

    def generate_report(
        self,
        scripts: list[Path],
        analyses: dict[Path, dict],
        plan: dict[str, list[Path]],
    ) -> str:
        """Gera relatório completo da consolidação."""
        report = []
        report.extend(
            (
                "# SCRIPTS CONSOLIDATION REPORT",
                f"**Data**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Scripts Analisados**: {len(scripts)}",
                "",
            )
        )

        # Estatísticas por categoria
        categories = {}
        for analysis in analyses.values():
            cat = analysis.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        report.append("## 📊 CATEGORIAS ENCONTRADAS")
        for category, count in sorted(categories.items()):
            report.append(f"- **{category}**: {count} scripts")
        report.append("")

        # Plano de ação
        report.append("## 🎯 PLANO DE CONSOLIDAÇÃO")
        for action, script_list in plan.items():
            if script_list:
                report.append(
                    f"\n### {action.replace('_', ' ').title()} ({len(script_list)} scripts)"
                )
                report.extend(
                    f"- {script.relative_to(self.workspace_root)}"
                    for script in script_list:
                )

        return "\n".join(report)

    def run_full_consolidation(self) -> None:
        """Executa consolidação completa dos scripts."""
        self._print("🔍 FLEXT SCRIPTS CONSOLIDATION - ANÁLISE COMPLETA")
        self._print("=" * 60)

        # 1. Encontrar todos os scripts
        self._print("\n📂 Encontrando scripts espalhados...")
        scripts = self.find_all_scattered_scripts()
        self._print(f"   Encontrados: {len(scripts)} scripts")

        if not scripts:
            self._print("✅ Nenhum script espalhado encontrado!")
            return

        # 2. Analisar cada script
        self._print("\n🔍 Analisando conteúdo dos scripts...")
        analyses = {}

        if RICH_AVAILABLE:
            with Progress(:
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Analisando...", total=len(scripts))

                for script in scripts:
                    progress.update(task, description=f"📝 {script.name}")
                    analyses[script] = self.analyze_script_content(script)
                    progress.advance(task)
        else:
            for i, script in enumerate(scripts):
                print(f"[{i + 1}/{len(scripts)}] Analisando {script.name}...")
                analyses[script] = self.analyze_script_content(script)

        # 3. Criar plano de consolidação
        self._print("\n📋 Criando plano de consolidação...")
        plan = self.create_consolidation_plan(analyses)

        # 4. Mostrar plano
        self._print("\n📊 PLANO DE CONSOLIDAÇÃO:")
        for action, script_list in plan.items():
            if script_list:
                self._print(
                    f"  {action.replace('_', ' ').title()}: {len(script_list)} scripts"
                )

        # 5. Gerar relatório
        report = self.generate_report(scripts, analyses, plan)
        report_path = (
            self.workspace_root
            / "scripts"
            / "consolidation_analysis"
            / "consolidation_report.md"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        self._print(
            f"\n📄 Relatório salvo: {report_path.relative_to(self.workspace_root)}"
        )

        # 6. Executar consolidação
        response = input("\n❓ Executar plano de consolidação? [y/N]: ")
        if response.lower() in {"y", "yes"}:
            self.execute_consolidation_plan(plan)
            self._print("\n🎉 CONSOLIDAÇÃO CONCLUÍDA!")
        else:
            self._print(
                "\n📝 Plano criado mas não executado. Use o relatório para revisão."
            )

    def _print(self, message: str) -> None:
        """Print otimizado.
        if RICH_AVAILABLE and console:
            console.print(message)
        else:
            print(message)


def main() -> int:
    Função principal."""
    workspace_root = Path("/home/marlonsc/flext")

    if not workspace_root.exists():
        print(f"❌ Workspace não encontrado: {workspace_root}")
        return 1

    consolidator = ScriptConsolidator(workspace_root)
    consolidator.run_full_consolidation()
    return 0


if __name__ == "__main__":
    sys.exit(main())
