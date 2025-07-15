"""Descoberta de dependências em arquivos de configuração"""

import re
import tomllib
from pathlib import Path
from typing import Dict, Optional, Set

from flext_tools.utils import Colors, print_colored, should_ignore_path


class ConfigFileDiscovery:
    """Descobre dependências mencionadas em arquivos de configuração."""

    def discover(self, project_path: Path, installed: set[str]) -> dict[str, set[str]]:
        """Descobre dependências em arquivos de configuração."""
        dependencies = {"runtime": set(), "test": set(), "dev": set()}

        # Analisa diferentes tipos de arquivos de configuração
        self._analyze_pytest_config(project_path, dependencies, installed)
        self._analyze_precommit_config(project_path, dependencies, installed)
        self._analyze_tox_config(project_path, dependencies, installed)
        self._analyze_dockerfile(project_path, dependencies, installed)
        self._analyze_requirements_files(project_path, dependencies, installed)

        return dependencies

    def _analyze_pytest_config(
        self, project_path: Path, deps: dict[str, set[str]], installed: set[str]
    ) -> None:
        """Analisa configuração do pytest em pyproject.toml."""
        pyproject_path = project_path / "pyproject.toml"
        if not pyproject_path.exists():
            return

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            pytest_config = (
                data.get("tool", {}).get("pytest", {}).get("ini_options", {})
            )

            # Procura por plugins do pytest
            if "plugins" in pytest_config:
                plugins = pytest_config["plugins"]
                if isinstance(plugins, list):
                    for plugin in plugins:
                        if isinstance(plugin, str) and not self._is_installed(
                            plugin, installed
                        ):
                            deps["test"].add(plugin)

        except Exception:
            pass

    def _analyze_precommit_config(
        self, project_path: Path, deps: dict[str, set[str]], installed: set[str]
    ) -> None:
        """Analisa .pre-commit-config.yaml."""
        precommit_file = project_path / ".pre-commit-config.yaml"
        if not precommit_file.exists():
            return

        try:
            import yaml

            with open(precommit_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data and "repos" in data:
                # Mapeamento de hooks conhecidos para pacotes
                hook_to_package = {
                    "black": "black",
                    "isort": "isort",
                    "flake8": "flake8",
                    "mypy": "mypy",
                    "ruff": "ruff",
                    "bandit": "bandit",
                    "pytest": "pytest",
                    "pylint": "pylint",
                    "autopep8": "autopep8",
                    "yapf": "yapf",
                }

                for repo in data["repos"]:
                    if "hooks" in repo:
                        for hook in repo["hooks"]:
                            hook_id = hook.get("id", "")
                            if hook_id in hook_to_package:
                                package = hook_to_package[hook_id]
                                if not self._is_installed(package, installed):
                                    deps["dev"].add(package)

        except Exception:
            pass

    def _analyze_tox_config(
        self, project_path: Path, deps: dict[str, set[str]], installed: set[str]
    ) -> None:
        """Analisa tox.ini."""
        tox_file = project_path / "tox.ini"
        if not tox_file.exists():
            return

        try:
            with open(tox_file, encoding="utf-8") as f:
                content = f.read()

            # Procura por deps em tox
            deps_pattern = re.compile(r"deps\s*=\s*([^\n]+(?:\n\s+[^\n]+)*)")
            matches = deps_pattern.findall(content)

            for match in matches:
                for line in match.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Extrai nome do pacote (remove versão)
                        pkg = re.split(r"[>=<!=]", line)[0].strip()
                        if pkg and not self._is_installed(pkg, installed):
                            deps["test"].add(pkg)

        except Exception:
            pass

    def _analyze_dockerfile(
        self, project_path: Path, deps: dict[str, set[str]], installed: set[str]
    ) -> None:
        """Analisa Dockerfile."""
        dockerfile = project_path / "Dockerfile"
        if not dockerfile.exists():
            return

        try:
            with open(dockerfile, encoding="utf-8") as f:
                content = f.read()

            # Procura por pip install em Dockerfile
            pip_pattern = re.compile(r"pip\s+install\s+([^\s&|;]+)")
            matches = pip_pattern.findall(content)

            for match in matches:
                pkg = match.strip()
                if (
                    pkg
                    and not pkg.startswith("-")
                    and not self._is_installed(pkg, installed)
                ):
                    deps["runtime"].add(pkg)

        except Exception:
            pass

    def _analyze_requirements_files(
        self, project_path: Path, deps: dict[str, set[str]], installed: set[str]
    ) -> None:
        """Analisa arquivos requirements.txt."""
        for req_file in project_path.rglob("requirements*.txt"):
            if should_ignore_path(req_file):
                continue

            try:
                with open(req_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Extrai nome do pacote (remove versão)
                            package_name = re.split(r"[>=<!=]", line)[0].strip()
                            if package_name and not self._is_installed(
                                package_name, installed
                            ):
                                deps["runtime"].add(package_name)

            except Exception:
                pass

    def _is_installed(self, package: str, installed: set[str]) -> bool:
        """Verifica se um pacote já está instalado."""
        variations = {
            package,
            package.lower(),
            package.replace("_", "-"),
            package.replace("-", "_"),
        }
        return any(var in installed for var in variations)
