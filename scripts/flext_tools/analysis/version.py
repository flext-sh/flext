"""Análise de versões de pacotes"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from packaging import version
from packaging.specifiers import SpecifierSet

from flext_tools.utils import Colors, print_colored


class VersionAnalyzer:
    """Analisa versões de pacotes e suas constraints."""

    def __init__(self):
        self.version_cache = {}

    def parse_version_spec(self, spec: str) -> tuple[str, str | None]:
        """
        Extrai nome do pacote e versão de uma especificação.

        Args:
            spec: Especificação do pacote (ex: "django>=3.2")

        Returns:
            Tupla (nome_pacote, especificação_versão)
        """
        # Padrões comuns de especificação
        patterns = [
            r"^([a-zA-Z0-9_\-\.]+)\s*([><=!]+.*)$",  # package>=1.0
            r"^([a-zA-Z0-9_\-\.]+)\[([^\]]+)\]\s*([><=!]+.*)$",  # package[extra]>=1.0
            r"^([a-zA-Z0-9_\-\.]+)$",  # package sem versão
        ]

        for pattern in patterns:
            match = re.match(pattern, spec.strip())
            if match:
                if len(match.groups()) == 3:  # Com extra
                    return match.group(1), match.group(3)
                if len(match.groups()) == 2:  # Sem extra
                    return match.group(1), match.group(2)
                # Só nome
                return match.group(1), None

        return spec, None

    def normalize_constraint(self, constraint: str) -> str:
        """
        Normaliza constraint de versão para formato padrão.

        Args:
            constraint: Constraint original (ex: "^1.2.3")

        Returns:
            Constraint normalizado (ex: ">=1.2.3,<2.0.0")
        """
        if not constraint:
            return "*"

        # Remove espaços
        constraint = constraint.strip()

        # Converte caret (^) para range semântico
        if constraint.startswith("^"):
            base_version = constraint[1:]
            try:
                v = version.parse(base_version)
                if v.major == 0:
                    if v.minor == 0:
                        # ^0.0.x -> >=0.0.x,<0.0.(x+1)
                        upper = f"0.0.{v.micro + 1}"
                    else:
                        # ^0.x.y -> >=0.x.y,<0.(x+1).0
                        upper = f"0.{v.minor + 1}.0"
                else:
                    # ^x.y.z -> >=x.y.z,<(x+1).0.0
                    upper = f"{v.major + 1}.0.0"
                return f">={base_version},<{upper}"
            except:
                return constraint

        # Converte tilde (~) para range
        if constraint.startswith("~"):
            base_version = constraint[1:]
            try:
                v = version.parse(base_version)
                # ~x.y.z -> >=x.y.z,<x.(y+1).0
                upper = f"{v.major}.{v.minor + 1}.0"
                return f">={base_version},<{upper}"
            except:
                return constraint

        return constraint

    def check_version_compatibility(
        self, constraints: list[str], package_name: str
    ) -> dict[str, any]:
        """
        Verifica compatibilidade entre múltiplas constraints de versão.

        Args:
            constraints: Lista de constraints (ex: [">=1.0", "<2.0"])
            package_name: Nome do pacote

        Returns:
            Dicionário com análise de compatibilidade
        """
        if not constraints:
            return {
                "compatible": True,
                "conflict": False,
                "recommended": "*",
                "issues": [],
            }

        # Normaliza todas as constraints
        normalized = [self.normalize_constraint(c) for c in constraints]

        # Tenta combinar em um SpecifierSet
        try:
            combined = SpecifierSet()
            for spec in normalized:
                if spec != "*":
                    combined &= SpecifierSet(spec)

            # Verifica se há interseção válida
            if combined:
                return {
                    "compatible": True,
                    "conflict": False,
                    "recommended": str(combined),
                    "issues": [],
                }
            return {
                "compatible": False,
                "conflict": True,
                "recommended": None,
                "issues": [f"Constraints incompatíveis: {', '.join(constraints)}"],
            }

        except Exception as e:
            return {
                "compatible": False,
                "conflict": True,
                "recommended": None,
                "issues": [f"Erro ao analisar constraints: {e!s}"],
            }

    def find_common_version_range(
        self, project_constraints: dict[str, str]
    ) -> str | None:
        """
        Encontra range de versão comum entre múltiplos projetos.

        Args:
            project_constraints: Dict {projeto: constraint}

        Returns:
            Range comum ou None se incompatível
        """
        if not project_constraints:
            return None

        constraints = list(project_constraints.values())
        unique_constraints = list({c for c in constraints if c})

        if not unique_constraints:
            return "*"

        if len(unique_constraints) == 1:
            return unique_constraints[0]

        # Tenta encontrar interseção
        result = self.check_version_compatibility(unique_constraints, "")
        return result.get("recommended")

    def analyze_version_conflicts(
        self, workspace_dependencies: dict[str, dict[str, str]]
    ) -> dict[str, list[dict]]:
        """
        Analisa conflitos de versão em todo o workspace.

        Args:
            workspace_dependencies: {projeto: {pacote: versão}}

        Returns:
            Dicionário com análise de conflitos por pacote
        """
        conflicts = {}

        # Agrupa por pacote
        package_versions = {}
        for project, deps in workspace_dependencies.items():
            for package, version_spec in deps.items():
                if package not in package_versions:
                    package_versions[package] = {}
                package_versions[package][project] = version_spec

        # Analisa cada pacote
        for package, project_specs in package_versions.items():
            if len(project_specs) > 1:
                # Verifica se há versões diferentes
                unique_specs = set(project_specs.values())
                if len(unique_specs) > 1:
                    analysis = self.check_version_compatibility(
                        list(unique_specs), package
                    )

                    if analysis["conflict"]:
                        conflicts[package] = {
                            "projects": project_specs,
                            "analysis": analysis,
                            "severity": "high" if len(project_specs) > 2 else "medium",
                        }

        return conflicts

    def suggest_version_resolution(self, conflicts: dict[str, dict]) -> dict[str, str]:
        """
        Sugere resoluções para conflitos de versão.

        Args:
            conflicts: Dicionário de conflitos do analyze_version_conflicts

        Returns:
            Sugestões de versão por pacote
        """
        suggestions = {}

        for package, conflict_data in conflicts.items():
            project_specs = conflict_data["projects"]

            # Tenta encontrar versão mais recente compatível
            all_specs = list(project_specs.values())

            # Remove especificações vazias ou "*"
            valid_specs = [s for s in all_specs if s and s != "*"]

            if not valid_specs:
                suggestions[package] = "*"
                continue

            # Se todas as specs são iguais, usa ela
            if len(set(valid_specs)) == 1:
                suggestions[package] = valid_specs[0]
                continue

            # Tenta encontrar interseção
            common_range = self.find_common_version_range(project_specs)
            if common_range:
                suggestions[package] = common_range
            else:
                # Sugere a constraint mais restritiva
                suggestions[package] = self._get_most_restrictive_spec(valid_specs)

        return suggestions

    def _get_most_restrictive_spec(self, specs: list[str]) -> str:
        """Retorna a especificação mais restritiva."""

        # Ordena por número de constraints
        def count_constraints(spec):
            return len(re.findall(r"[><=!]+", spec))

        sorted_specs = sorted(specs, key=count_constraints, reverse=True)
        return sorted_specs[0] if sorted_specs else "*"
