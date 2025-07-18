"""Base para descoberta de dependências"""

import tomllib
from pathlib import Path

from flext_tools.discovery.config import ConfigFileDiscovery
from flext_tools.discovery.python import PythonImportDiscovery
from flext_tools.discovery.transitive import TransitiveDependencyResolver
from flext_tools.utils import (
    Colors,
    get_stdlib_modules,
    print_colored,
)


class DependencyDiscovery:
    """Classe principal para descoberta de dependências."""

    def __init__(self, resolve_transitive: bool = True):
        self.stdlib_modules = get_stdlib_modules()
        self.python_discovery = PythonImportDiscovery(self.stdlib_modules)
        self.config_discovery = ConfigFileDiscovery()
        self.resolve_transitive = resolve_transitive
        if resolve_transitive:
            self.transitive_resolver = TransitiveDependencyResolver()

    def discover_project_dependencies(
        self, project_path: Path, include_dev: bool = True, include_test: bool = True,
    ) -> dict[str, set[str]]:
        """
        Descobre todas as dependências de um projeto.

        Args:
            project_path: Caminho para o projeto
            include_dev: Incluir dependências de desenvolvimento
            include_test: Incluir dependências de teste

        Returns:
            Dicionário com categorias de dependências
        """
        print_colored(f"🔍 Analisando projeto: {project_path.name}", Colors.BLUE)

        # Obtém dependências já instaladas
        installed = self.get_installed_dependencies(project_path)
        print_colored(f"  📦 Dependências instaladas: {len(installed)}", Colors.CYAN)

        # Descobre imports Python
        python_deps = self.python_discovery.discover(project_path, installed)

        # Descobre em arquivos de configuração
        config_deps = self.config_discovery.discover(project_path, installed)

        # Combina resultados
        result = {
            "runtime": python_deps.get("runtime", set())
            | config_deps.get("runtime", set()),
            "test": set(),
            "dev": set(),
        }

        if include_test:
            result["test"] = python_deps.get("test", set()) | config_deps.get(
                "test", set(),
            )

        if include_dev:
            result["dev"] = config_deps.get("dev", set())

        # NOVA FUNCIONALIDADE: Remove dependências transitivas (opcional)
        if self.resolve_transitive and hasattr(self, "transitive_resolver"):
            available_transitive = (
                self.transitive_resolver.get_all_available_dependencies(project_path)
            )
            print_colored(
                f"  🔗 Dependências transitivas detectadas: {len(available_transitive)}",
                Colors.CYAN,
            )

            # Remove dependências que estão disponíveis transitivamente
            for category in result:
                original_count = len(result[category])
                result[category] = {
                    dep
                    for dep in result[category]
                    if not self._is_dependency_available_transitively(
                        dep, available_transitive,
                    )
                }
                removed_count = original_count - len(result[category])
                if removed_count > 0:
                    print_colored(
                        f"    ✓ {removed_count} dependências transitivas removidas de {category}",
                        Colors.GREEN,
                    )

        # Remove dependências já instaladas do resultado
        for category in result:
            result[category] = {
                dep
                for dep in result[category]
                if not self._is_installed(dep, installed)
            }

        return result

    def get_installed_dependencies(self, project_path: Path) -> set[str]:
        """Obtém lista de dependências já instaladas no projeto."""
        installed = set()
        pyproject_path = project_path / "pyproject.toml"

        if not pyproject_path.exists():
            return installed

        try:
            with Path(pyproject_path).open("rb") as f:
                data = tomllib.load(f)

            # CORREÇÃO CRÍTICA: Suporte para PEP 621 (project.dependencies)
            pep621_deps = data.get("project", {}).get("dependencies", [])
            if pep621_deps:
                print_colored(
                    f"  🔍 PEP 621 detectado: {len(pep621_deps)} dependências",
                    Colors.CYAN,
                )
                for dep_spec in pep621_deps:
                    # Extrai nome do pacote da especificação (ex: "pydantic>=2.0.0" -> "pydantic")
                    dep_name = self._extract_package_name(dep_spec)
                    if dep_name and dep_name != "python":
                        self._add_package_variations(installed, dep_name)

            # Dependências Poetry principais
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for dep_name in poetry_deps:
                if dep_name != "python":
                    self._add_package_variations(installed, dep_name)

            # Dependências de grupos Poetry
            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_data in groups.values():
                group_deps = group_data.get("dependencies", {})
                for dep_name in group_deps:
                    self._add_package_variations(installed, dep_name)

        except Exception as e:
            print_colored(f"  ⚠️ Erro ao ler pyproject.toml: {e}", Colors.YELLOW)

        return installed

    def _is_installed(self, package: str, installed: set[str]) -> bool:
        """Verifica se um pacote já está instalado."""
        variations = {
            package,
            package.lower(),
            package.replace("_", "-"),
            package.replace("-", "_"),
            self._normalize_name(package),
        }
        return any(var in installed for var in variations)

    def _normalize_name(self, name: str) -> str:
        """Normaliza nome de pacote para comparação."""
        return name.lower().replace("_", "").replace("-", "")

    def _extract_package_name(self, dep_spec: str) -> str:
        """Extrai nome do pacote de uma especificação PEP 621.

        Exemplos:
            "pydantic>=2.0.0" -> "pydantic"
            "fastapi (>=0.116.1,<0.117.0)" -> "fastapi"
            "passlib[bcrypt]>=1.7.4" -> "passlib"
        """
        import re

        # Remove espaços e parênteses extras
        dep_spec = dep_spec.strip().replace("(", "").replace(")", "")

        # Extrai nome antes de qualquer operador de versão ou extra
        match = re.match(r"^([a-zA-Z0-9_-]+)", dep_spec)
        if match:
            return match.group(1)
        return ""

    def _add_package_variations(self, installed: set[str], dep_name: str):
        """Adiciona todas as variações de um nome de pacote ao conjunto."""
        installed.add(dep_name)
        installed.add(dep_name.lower())
        installed.add(dep_name.replace("-", "_"))
        installed.add(dep_name.replace("_", "-"))

    def _is_dependency_available_transitively(
        self, package: str, available_transitive: set[str],
    ) -> bool:
        """Verifica se uma dependência está disponível transitivamente."""
        variations = {
            package,
            package.lower(),
            package.replace("_", "-"),
            package.replace("-", "_"),
            self._normalize_name(package),
        }

        # Normaliza dependências transitivas para comparação
        normalized_transitive = {
            self._normalize_name(dep) for dep in available_transitive
        }

        return any(
            self._normalize_name(var) in normalized_transitive for var in variations
        )
