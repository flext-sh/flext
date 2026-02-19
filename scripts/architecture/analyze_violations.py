#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-architecture/SKILL.md
"""Analisador de Violações Arquiteturais - FLEXT Workspace.

Identifica módulos em camadas incorretas e violations de dependências.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


# Cores simples para output
class Colors:
    """Cores para output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_colored(text: str, color: str) -> None:
    """Print text with color formatting."""


class LayerType(Enum):
    """Tipos de camadas arquiteturais."""

    BASE = "base"  # flext-core
    INTERMEDIATE = "intermediate"  # flext-cli, flext-observability, etc
    SPECIFIC = "specific"  # flext-*-oracle, flext-*-ldap, etc
    APPLICATION = "application"  # flext-oud-mig, flext-meltano-native


@dataclass
class Project:
    """Representa um projeto no workspace."""

    name: str
    path: Path
    layer: LayerType
    dependencies: set[str]


@dataclass
class Violation:
    """Representa uma violação arquitetural."""

    file_path: Path
    violation_type: str
    description: str
    severity: str  # HIGH, MEDIUM, LOW
    suggested_action: str


class ArchitectureAnalyzer:
    """Analisador principal de violações arquiteturais."""

    def __init__(self, workspace_root: Path) -> None:
        """Initialize the architecture analyzer."""
        self.workspace_root = workspace_root
        self.projects = self._discover_projects()
        self.violations: list[Violation] = []

        # Definir hierarquia de camadas
        self.layer_hierarchy = {
            LayerType.BASE: 0,
            LayerType.INTERMEDIATE: 1,
            LayerType.SPECIFIC: 2,
            LayerType.APPLICATION: 3,
        }

    def _discover_projects(self) -> dict[str, Project]:
        """Descobre todos os projetos no workspace."""
        projects: dict[str, Project] = {}

        for item in self.workspace_root.iterdir():
            if not item.is_dir() or item.name.startswith("."):
                continue

            project_name = item.name
            layer = self._classify_project_layer(project_name)

            projects[project_name] = Project(
                name=project_name,
                path=item,
                layer=layer,
                dependencies=set(),
            )

        return projects

    def _classify_project_layer(self, project_name: str) -> LayerType:
        """Classifica a camada de um projeto baseado no nome."""
        # Camada BASE
        if project_name == "flext-core":
            return LayerType.BASE

        # Camada APPLICATION
        if project_name in {"flext-oud-mig", "flext-meltano-native"}:
            return LayerType.APPLICATION

        # Camada INTERMEDIATE
        intermediate_projects = [
            "flext-cli",
            "flext-observability",
            "flext-grpc",
            "flext-web",
            "flext-api",
            "flext-auth",
        ]
        if project_name in intermediate_projects:
            return LayerType.INTERMEDIATE

        # Camada SPECIFIC (padrão para flext-*)
        if project_name.startswith("flext-"):
            return LayerType.SPECIFIC

        # Default para APPLICATION
        return LayerType.APPLICATION

    def analyze_import_violations(self) -> None:
        """Analisa violações de imports entre camadas."""
        print_colored(
            "🔍 Analisando violações de imports entre camadas...",
            Colors.BLUE,
        )

        for project in self.projects.values():
            src_path = project.path / "src"
            if not src_path.exists():
                continue

            self._analyze_project_imports(project)

    def _analyze_project_imports(self, project: Project) -> None:
        """Analisa imports de um projeto específico."""
        src_path = project.path / "src"

        for py_file in src_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            try:
                with py_file.open(encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                imports = self._extract_imports(tree)

                for import_name in imports:
                    violation = self._check_import_violation(
                        project,
                        py_file,
                        import_name,
                    )
                    if violation:
                        self.violations.append(violation)

            except (OSError, SyntaxError, UnicodeDecodeError) as e:
                print_colored(f"⚠️  Erro ao analisar {py_file}: {e}", Colors.YELLOW)

    def _extract_imports(self, tree: ast.AST) -> set[str]:
        """Extrai todos os imports de um arquivo Python."""
        imports: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])

        return imports

    def _check_import_violation(
        self,
        project: Project,
        file_path: Path,
        import_name: str,
    ) -> Violation | None:
        """Verifica se um import viola a arquitetura."""
        # Ignorar imports padrão do Python e bibliotecas externas
        if not self._is_flext_import(import_name):
            return None

        imported_project = self._get_project_from_import(import_name)
        if not imported_project:
            return None

        # Verificar violação de camada
        if self._is_layer_violation(project, imported_project):
            return Violation(
                file_path=file_path,
                violation_type="LAYER_VIOLATION",
                description=(
                    f"Projeto {project.name} (camada {project.layer.value}) "
                    f"importa {imported_project.name} "
                    f"(camada {imported_project.layer.value})"
                ),
                severity="HIGH",
                suggested_action=(
                    f"Mover {file_path.name} para .bak e reimplementar usando DI"
                ),
            )

        return None

    def _is_flext_import(self, import_name: str) -> bool:
        """Verifica se é um import de projeto FLEXT."""
        flext_patterns = [r"^flext[_-]", r"^flext[_-]", r"^flext[_-]"]

        return any(re.match(pattern, import_name) for pattern in flext_patterns)

    def _get_project_from_import(self, import_name: str) -> Project | None:
        """Obtém o projeto correspondente a um import."""
        # Mapear nomes de import para projetos
        import_mappings = {
            "flext_core": "flext-core",
            "flext_cli": "flext-cli",
            "flext_quality": "flext-core",  # flext_quality está em flext-core
            "flext_oud_mig": "flext-oud-mig",
            # ... adicionar outros mapeamentos conforme necessário
        }
        project_name = import_mappings.get(import_name)
        return self.projects.get(project_name) if project_name else None

    def _is_layer_violation(
        self,
        importing_project: Project,
        imported_project: Project,
    ) -> bool:
        """Verifica se há violação entre camadas."""
        importing_level = self.layer_hierarchy[importing_project.layer]
        imported_level = self.layer_hierarchy[imported_project.layer]

        # Violação: camada inferior importando camada superior
        return importing_level < imported_level

    def analyze_module_placement(self) -> None:
        """Analisa módulos em camadas incorretas."""
        print_colored("📁 Analisando posicionamento de módulos...", Colors.BLUE)

        for project in self.projects.values():
            src_path = project.path / "src"
            if not src_path.exists():
                continue

            self._analyze_project_modules(project)

    def _analyze_project_modules(self, project: Project) -> None:
        """Analisa módulos de um projeto específico."""
        src_path = project.path / "src"

        for py_file in src_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue

            # Analisar conteúdo do arquivo para determinar se está na camada correta
            violation = self._check_module_placement(project, py_file)
            if violation:
                self.violations.append(violation)

    def _check_module_placement(
        self,
        project: Project,
        file_path: Path,
    ) -> Violation | None:
        """Verifica se um módulo está na camada correta."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Verificar padrões que indicam camada incorreta
            concrete_patterns = [
                r"meltano",
                r"oracle",
                r"ldap",
                r"singer",
                r"flext",
                r"flext",
            ]

            # Se está no flext-core mas tem código específico/concreto
            if project.name == "flext-core":
                for pattern in concrete_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        return Violation(
                            file_path=file_path,
                            violation_type="MISPLACED_MODULE",
                            description=(
                                f"Módulo com código específico ({pattern}) em camada base"
                            ),
                            severity="HIGH",
                            suggested_action=(
                                f"Renomear {file_path.name} para .bak e mover "
                                f"funcionalidade para camada apropriada"
                            ),
                        )

        except (OSError, UnicodeDecodeError) as e:
            print_colored(f"⚠️  Erro ao analisar {file_path}: {e}", Colors.YELLOW)

        return None

    def generate_report(self) -> None:
        """Gera relatório completo de violações."""
        print_colored("\n" + "=" * 80, Colors.CYAN)
        print_colored("📊 RELATÓRIO DE VIOLAÇÕES ARQUITETURAIS", Colors.CYAN)
        print_colored("=" * 80, Colors.CYAN)

        if not self.violations:
            print_colored("✅ Nenhuma violação arquitetural encontrada!", Colors.GREEN)
            return

        # Agrupar violações por tipo
        violations_by_type: dict[str, list[Violation]] = {}
        for violation in self.violations:
            if violation.violation_type not in violations_by_type:
                violations_by_type[violation.violation_type] = []
            violations_by_type[violation.violation_type].append(violation)

        for violation_type, violations in violations_by_type.items():
            print_colored(
                f"\n🚨 {violation_type} ({len(violations)} violações):",
                Colors.RED,
            )

            for violation in violations:
                severity_color = (
                    Colors.RED if violation.severity == "HIGH" else Colors.YELLOW
                )
                print_colored(f"  📁 {violation.file_path}", severity_color)
                print_colored(f"     {violation.description}", Colors.WHITE)
                print_colored(f"     💡 {violation.suggested_action}", Colors.BLUE)

        # Estatísticas finais
        print_colored("\n📈 ESTATÍSTICAS:", Colors.CYAN)
        print_colored(f"  Total de violações: {len(self.violations)}", Colors.WHITE)
        high_severity = len([v for v in self.violations if v.severity == "HIGH"])
        print_colored(f"  Violações críticas: {high_severity}", Colors.RED)

    def generate_fix_script(self) -> None:
        """Gera script para correção automática."""
        script_path = (
            self.workspace_root / "scripts" / "architecture" / "fix_violations.sh"
        )
        script_path.parent.mkdir(parents=True, exist_ok=True)

        with script_path.open("w", encoding="utf-8") as f:
            f.write("#!/bin/bash\n")
            f.write(
                "# Script gerado automaticamente para correção de violações arquiteturais\n\n",
            )

            for violation in self.violations:
                if "Renomear" in violation.suggested_action:
                    relative_path = violation.file_path.relative_to(self.workspace_root)
                    f.write(f"# {violation.description}\n")
                    f.write(f"mv {relative_path} {relative_path}.bak\n\n")

        script_path.chmod(0o755)
        print_colored(f"💾 Script de correção gerado: {script_path}", Colors.GREEN)


def main() -> None:
    """Função principal."""
    workspace_root = Path.cwd()

    print_colored("🏗️  ANALISADOR DE VIOLAÇÕES ARQUITETURAIS - FLEXT", Colors.CYAN)
    print_colored(f"📁 Workspace: {workspace_root}", Colors.WHITE)

    analyzer = ArchitectureAnalyzer(workspace_root)

    # Executar análises
    analyzer.analyze_import_violations()
    analyzer.analyze_module_placement()

    # Gerar relatórios
    analyzer.generate_report()
    analyzer.generate_fix_script()

    print_colored("\n✅ Análise concluída!", Colors.GREEN)


if __name__ == "__main__":
    main()
