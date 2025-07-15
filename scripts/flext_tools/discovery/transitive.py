"""Resolução de dependências transitivas via path dependencies"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

from flext_tools.utils import Colors, print_colored


@dataclass
class PathDependency:
    """Representa uma dependência path-based."""

    name: str
    path: Path
    develop: bool = False


@dataclass
class TransitiveDependencies:
    """Resultado da resolução de dependências transitivas."""

    direct: set[str]
    transitive: set[str]
    path_dependencies: list[PathDependency]


class TransitiveDependencyResolver:
    """Resolve dependências transitivas através de path dependencies."""

    def __init__(self):
        self._cache: dict[str, TransitiveDependencies] = {}
        self._resolving: set[str] = set()  # Prevent circular dependencies

    def resolve_transitive_dependencies(
        self, project_path: Path, max_depth: int = 3
    ) -> TransitiveDependencies:
        """
        Resolve dependências transitivas de um projeto.

        Args:
            project_path: Caminho do projeto
            max_depth: Profundidade máxima de resolução (evita loops infinitos)

        Returns:
            TransitiveDependencies com dependências diretas e transitivas
        """
        project_key = str(project_path.resolve())

        # Cache hit
        if project_key in self._cache:
            return self._cache[project_key]

        # Circular dependency detection
        if project_key in self._resolving:
            print_colored(
                f"  ⚠️ Dependência circular detectada: {project_path.name}",
                Colors.YELLOW,
            )
            return TransitiveDependencies(set(), set(), [])

        self._resolving.add(project_key)

        try:
            result = self._resolve_recursive(project_path, max_depth)
            self._cache[project_key] = result
            return result

        finally:
            self._resolving.discard(project_key)

    def _resolve_recursive(
        self, project_path: Path, depth: int
    ) -> TransitiveDependencies:
        """Resolve dependências recursivamente."""
        if depth <= 0:
            return TransitiveDependencies(set(), set(), [])

        pyproject_path = project_path / "pyproject.toml"
        if not pyproject_path.exists():
            return TransitiveDependencies(set(), set(), [])

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            print_colored(f"  ⚠️ Erro ao ler {pyproject_path}: {e}", Colors.YELLOW)
            return TransitiveDependencies(set(), set(), [])

        # Coleta dependências diretas
        direct_deps = self._extract_direct_dependencies(data)

        # Coleta path dependencies
        path_deps = self._extract_path_dependencies(data, project_path)

        # Resolve dependências transitivas através de path dependencies
        transitive_deps = set()

        for path_dep in path_deps:
            if path_dep.path.exists():
                child_result = self._resolve_recursive(path_dep.path, depth - 1)
                # Adiciona dependências diretas do path dependency como transitivas
                transitive_deps.update(child_result.direct)
                # Adiciona dependências transitivas do path dependency
                transitive_deps.update(child_result.transitive)

        return TransitiveDependencies(
            direct=direct_deps, transitive=transitive_deps, path_dependencies=path_deps
        )

    def _extract_direct_dependencies(self, data: dict) -> set[str]:
        """Extrai dependências diretas do pyproject.toml."""
        dependencies = set()

        # PEP 621 dependencies
        pep621_deps = data.get("project", {}).get("dependencies", [])
        for dep_spec in pep621_deps:
            dep_name = self._extract_package_name(dep_spec)
            if dep_name and dep_name != "python":
                dependencies.add(dep_name)

        # Poetry dependencies
        poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        for dep_name, dep_spec in poetry_deps.items():
            if dep_name != "python" and not isinstance(dep_spec, dict):
                dependencies.add(dep_name)
            elif isinstance(dep_spec, dict) and "path" not in dep_spec:
                # Dependência Poetry normal (não path-based)
                dependencies.add(dep_name)

        # Poetry group dependencies
        groups = data.get("tool", {}).get("poetry", {}).get("group", {})
        for group_data in groups.values():
            group_deps = group_data.get("dependencies", {})
            for dep_name, dep_spec in group_deps.items():
                if not isinstance(dep_spec, dict) or "path" not in dep_spec:
                    dependencies.add(dep_name)

        return dependencies

    def _extract_path_dependencies(
        self, data: dict, project_path: Path
    ) -> list[PathDependency]:
        """Extrai path dependencies do pyproject.toml."""
        path_deps = []

        # Poetry path dependencies
        poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        for dep_name, dep_spec in poetry_deps.items():
            if isinstance(dep_spec, dict) and "path" in dep_spec:
                path = project_path / dep_spec["path"]
                develop = dep_spec.get("develop", False)
                path_deps.append(PathDependency(dep_name, path.resolve(), develop))

        # Poetry group path dependencies
        groups = data.get("tool", {}).get("poetry", {}).get("group", {})
        for group_data in groups.values():
            group_deps = group_data.get("dependencies", {})
            for dep_name, dep_spec in group_deps.items():
                if isinstance(dep_spec, dict) and "path" in dep_spec:
                    path = project_path / dep_spec["path"]
                    develop = dep_spec.get("develop", False)
                    path_deps.append(PathDependency(dep_name, path.resolve(), develop))

        return path_deps

    def _extract_package_name(self, dep_spec: str) -> str:
        """Extrai nome do pacote de uma especificação de dependência."""
        import re

        dep_spec = dep_spec.strip().replace("(", "").replace(")", "")
        match = re.match(r"^([a-zA-Z0-9_-]+)", dep_spec)
        if match:
            return match.group(1)
        return ""

    def get_all_available_dependencies(self, project_path: Path) -> set[str]:
        """
        Obtém todas as dependências disponíveis para um projeto.
        Inclui dependências diretas + transitivas via path dependencies.
        """
        result = self.resolve_transitive_dependencies(project_path)
        return result.direct | result.transitive

    def is_dependency_available_transitively(
        self, project_path: Path, package_name: str
    ) -> bool:
        """
        Verifica se uma dependência está disponível transitivamente.
        """
        available = self.get_all_available_dependencies(project_path)

        # Normaliza nomes para comparação
        normalized_available = {self._normalize_name(dep) for dep in available}
        normalized_package = self._normalize_name(package_name)

        return normalized_package in normalized_available

    def _normalize_name(self, name: str) -> str:
        """Normaliza nome de pacote para comparação."""
        return name.lower().replace("_", "").replace("-", "")

    def clear_cache(self):
        """Limpa cache de resolução."""
        self._cache.clear()
        self._resolving.clear()
