"""Análise de versões de pacotes."""

from __future__ import annotations

import re
from typing import Any

from packaging import version
from packaging.specifiers import SpecifierSet

from flext_tools.utils import Colors, print_colored

GROUPS_WITH_EXTRA = 3
GROUPS_WITHOUT_EXTRA = 2
MIN_PROJECTS_HIGH_SEVERITY = 2


class VersionAnalyzer:
    """Analisa versões de pacotes e suas constraints."""

    @staticmethod
    def parse_version_spec(spec: str) -> tuple[str, str | None]:
        """Extrai nome do pacote e versão de uma especificação.

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
                if len(match.groups()) == GROUPS_WITH_EXTRA:  # Com extra
                    return match.group(1), match.group(3)
                if len(match.groups()) == GROUPS_WITHOUT_EXTRA:  # Sem extra
                    return match.group(1), match.group(2)
                # Só nome
                return match.group(1), None

        return spec, None

    @staticmethod
    def normalize_constraint(constraint: str) -> str:
        """Normaliza constraint de versão para formato padrão.

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
            except (ValueError, AttributeError, TypeError):
                return constraint
            else:
                # ^0.0.x -> >=0.0.x,<0.0.(x+1) OR ^0.x.y -> >=0.x.y,<0.(x+1).0
                # OR ^x.y.z -> >=x.y.z,<(x+1).0.0
                if v.major == 0:
                    upper = (
                        f"0.0.{v.micro + 1}" if v.minor == 0 else f"0.{v.minor + 1}.0"
                    )
                else:
                    upper = f"{v.major + 1}.0.0"
                return f">={base_version},<{upper}"

        # Converte tilde (~) para range
        if constraint.startswith("~"):
            base_version = constraint[1:]
            try:
                v = version.parse(base_version)
            except (ValueError, AttributeError, TypeError):
                return constraint
            else:
                # ~x.y.z -> >=x.y.z,<x.(y+1).0
                upper = f"{v.major}.{v.minor + 1}.0"
                return f">={base_version},<{upper}"

        return constraint

    @staticmethod
    def check_version_compatibility(
        spec1: str,
        spec2: str,
    ) -> dict[str, Any]:
        """Verifica compatibilidade entre duas especificações de versão.

        Args:
            spec1: Primeira especificação de versão
            spec2: Segunda especificação de versão

        Returns:
            Análise de compatibilidade

        """
        if not spec1 or not spec2:
            return {
                "compatible": True,
                "conflict": False,
                "recommended": "*",
                "issues": [],
            }

        # Normaliza todas as constraints
        normalized1 = VersionAnalyzer.normalize_constraint(spec1)
        normalized2 = VersionAnalyzer.normalize_constraint(spec2)

        try:
            combined = SpecifierSet()
            if normalized1 != "*":
                combined &= SpecifierSet(normalized1)
            if normalized2 != "*":
                combined &= SpecifierSet(normalized2)
        except (ValueError, TypeError, AttributeError) as e:
            return {
                "compatible": False,
                "conflict": True,
                "recommended": None,
                "issues": [f"Erro ao processar constraints: {e}"],
            }
        else:
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
                "issues": [f"Constraints incompatíveis: {spec1}, {spec2}"],
            }

    @staticmethod
    def find_common_version_range(
        project_constraints: dict[str, str],
    ) -> str | None:
        """Encontra range de versão comum entre múltiplos projetos.

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
        result = VersionAnalyzer.check_version_compatibility(
            unique_constraints[0],
            unique_constraints[1],
        )
        return result.get("recommended")

    @staticmethod
    def _collect_package_versions(
        projects_data: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, str]]:
        """Coleta versões de cada package por projeto."""
        package_versions: dict[str, dict[str, str]] = {}

        for project_name, data in projects_data.items():
            # PEP 621 dependencies
            pep621_deps = data.get("project", {}).get("dependencies", [])
            for dep_spec in pep621_deps:
                package_name, version_spec = VersionAnalyzer.parse_version_spec(dep_spec)
                if package_name and version_spec:
                    if package_name not in package_versions:
                        package_versions[package_name] = {}
                    package_versions[package_name][project_name] = version_spec or "*"

            # Poetry dependencies
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for package_name, dep_spec in poetry_deps.items():
                if isinstance(dep_spec, str):
                    version_spec = dep_spec
                elif isinstance(dep_spec, dict):
                    version_spec = dep_spec.get("version", "*")
                else:
                    continue

                if package_name not in package_versions:
                    package_versions[package_name] = {}
                package_versions[package_name][project_name] = version_spec or "*"

        return package_versions

    @staticmethod
    def _detect_version_conflicts(
        package_versions: dict[str, dict[str, str]],
    ) -> dict[str, list[dict[str, Any]]]:
        """Detecta conflitos de versão entre packages."""
        conflicts: dict[str, list[dict[str, Any]]] = {}

        for package_name, versions in package_versions.items():
            if len(versions) > 1:
                unique_specs = set(versions.values())
                if len(unique_specs) > 1:
                    analysis = VersionAnalyzer.check_version_compatibility(
                        next(iter(unique_specs)),
                        list(unique_specs)[1],
                    )

                    if not analysis.get("compatible", True):
                        conflicts[package_name] = [
                            {
                                "type": "version_conflict",
                                "projects": versions,
                                "analysis": analysis,
                                "severity": (
                                    "high"
                                    if len(versions) > MIN_PROJECTS_HIGH_SEVERITY
                                    else "medium"
                                ),
                            },
                        ]

        return conflicts

    @staticmethod
    def analyze_version_conflicts(
        projects_data: dict[str, dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """Analisa conflitos de versão entre projetos."""
        print_colored("🔍 Analisando conflitos de versão...", Colors.BLUE)

        package_versions = VersionAnalyzer._collect_package_versions(projects_data)
        return VersionAnalyzer._detect_version_conflicts(package_versions)

    @staticmethod
    def suggest_version_resolution(
        conflicts: dict[str, dict[str, Any]],
    ) -> dict[str, str]:
        """Sugere resoluções para conflitos de versão.

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
            common_range = VersionAnalyzer.find_common_version_range(project_specs)
            if common_range:
                suggestions[package] = common_range
            else:
                # Sugere a constraint mais restritiva
                suggestions[package] = VersionAnalyzer._get_most_restrictive_spec(valid_specs)

        return suggestions

    @staticmethod
    def _get_most_restrictive_spec(specs: list[str]) -> str:
        """Retorna a especificação mais restritiva."""

        # Ordena por número de constraints
        def count_constraints(spec: str) -> int:
            return len(re.findall(r"[><=!]+", spec))

        sorted_specs = sorted(specs, key=count_constraints, reverse=True)
        return sorted_specs[0] if sorted_specs else "*"


# Helper functions following flext-core pattern
def parse_version_spec(spec: str) -> tuple[str, str | None]:
    """Parse version specification into package name and version constraint.

    Args:
        spec: Package specification (e.g., "django>=3.2")

    Returns:
        Tuple (package_name, version_specification)

    """
    return VersionAnalyzer.parse_version_spec(spec)


def normalize_constraint(constraint: str) -> str:
    """Normalize version constraint to standard format.

    Args:
        constraint: Original constraint (e.g., "^1.2.3")

    Returns:
        Normalized constraint (e.g., ">=1.2.3,<2.0.0")

    """
    return VersionAnalyzer.normalize_constraint(constraint)


def check_version_compatibility(spec1: str, spec2: str) -> dict[str, Any]:
    """Check compatibility between two version specifications.

    Args:
        spec1: First version specification
        spec2: Second version specification

    Returns:
        Compatibility analysis dict

    """
    return VersionAnalyzer.check_version_compatibility(spec1, spec2)


def analyze_version_conflicts(projects_data: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Analyze version conflicts between projects.

    Args:
        projects_data: Dictionary of project data from pyproject.toml files

    Returns:
        Dictionary of conflicts by package name

    """
    return VersionAnalyzer.analyze_version_conflicts(projects_data)


def suggest_version_resolution(conflicts: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Suggest resolutions for version conflicts.

    Args:
        conflicts: Dictionary of conflicts from analyze_version_conflicts

    Returns:
        Suggested versions by package name

    """
    return VersionAnalyzer.suggest_version_resolution(conflicts)
