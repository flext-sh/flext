"""Validação de configurações Poetry."""

from __future__ import annotations

import re
import subprocess
import tomllib
from typing import TYPE_CHECKING, Any

from flext_tools.utils import Colors, print_colored

if TYPE_CHECKING:
    from pathlib import Path


class PoetryValidator:
    """Valida configurações e projetos Poetry."""

    def validate_project(self, project_path: Path) -> dict[str, Any]:
        """Valida um projeto Poetry."""
        results: dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": [],
        }

        # Verifica pyproject.toml
        pyproject_path = project_path / "pyproject.toml"
        if not pyproject_path.exists():
            results["valid"] = False
            results["errors"].append("pyproject.toml não encontrado")
            return results

        # Valida sintaxe TOML
        toml_valid, toml_error = self._validate_toml_syntax(pyproject_path)
        if not toml_valid:
            results["valid"] = False
            results["errors"].append(f"Erro de sintaxe TOML: {toml_error}")
            return results

        try:
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)

            # Valida estrutura Poetry
            poetry_valid, poetry_issues = self._validate_poetry_structure(data)
            if not poetry_valid:
                results["valid"] = False
                results["errors"].extend(poetry_issues)

            # Valida metadados do projeto
            metadata_valid, metadata_issues = self._validate_project_metadata(data)
            if not metadata_valid:
                results["warnings"].extend(metadata_issues)

            # Valida dependências
            deps_valid, deps_issues = self._validate_dependencies(data)
            if not deps_valid:
                results["warnings"].extend(deps_issues)

            # Coleta informações do projeto
            results["info"] = self._collect_project_info(data)

        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Erro ao processar pyproject.toml: {e}")

        # Valida lock file
        lock_valid, lock_issues = self._validate_lock_file(project_path)
        if not lock_valid:
            results["warnings"].extend(lock_issues)

        return results

    def _validate_toml_syntax(self, file_path: Path) -> tuple[bool, str | None]:
        """Valida sintaxe TOML do arquivo."""
        try:
            with file_path.open("rb") as f:
                tomllib.load(f)
            return True, None
        except tomllib.TOMLDecodeError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Erro ao ler arquivo: {e}"

    def _validate_poetry_structure(
        self,
        data: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Valida estrutura Poetry no pyproject.toml."""
        issues = []

        # Verifica seção [tool.poetry]
        if "tool" not in data or "poetry" not in data["tool"]:
            issues.append("Seção [tool.poetry] não encontrada")
            return False, issues

        poetry = data["tool"]["poetry"]

        # Campos obrigatórios
        required_fields = ["name", "version", "description"]
        issues.extend(
            f"Campo obrigatório '{field}' não encontrado em [tool.poetry]"
            for field in required_fields
            if field not in poetry
        )

        # Verifica dependências
        if "dependencies" not in poetry:
            issues.append("Seção [tool.poetry.dependencies] não encontrada")
        elif "python" not in poetry["dependencies"]:
            issues.append("Versão do Python não especificada em dependencies")

        return len(issues) == 0, issues

    def _validate_project_metadata(
        self,
        data: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Valida metadados do projeto."""
        poetry = data.get("tool", {}).get("poetry", {})

        # Campos recomendados
        recommended_fields = ["authors", "readme", "homepage", "repository", "keywords"]
        issues = [
            f"Campo recomendado '{field}' não encontrado"
            for field in recommended_fields
            if field not in poetry
        ]

        # Valida formato de autores
        if "authors" in poetry:
            authors = poetry["authors"]
            if not isinstance(authors, list):
                issues.append("Campo 'authors' deve ser uma lista")
            elif len(authors) == 0:
                issues.append("Lista de autores está vazia")

        # Valida versão
        if "version" in poetry:
            version = poetry["version"]
            if not self._is_valid_version(version):
                issues.append(
                    f"Versão '{version}' não segue o padrão semântico (x.y.z)",
                )

        return len(issues) == 0, issues

    def _validate_dependencies(self, data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Valida dependências do projeto."""
        issues = []
        poetry = data.get("tool", {}).get("poetry", {})

        # Verifica dependências principais
        deps = poetry.get("dependencies", {})
        for name, spec in deps.items():
            if name == "python":
                continue

            if (
                isinstance(spec, dict)
                and "version" not in spec
                and "git" not in spec
                and "path" not in spec
            ):
                issues.append(f"Dependência '{name}' sem especificação de versão")

        # Verifica grupos de dependências
        groups = poetry.get("group", {})
        for group_name, group_data in groups.items():
            group_deps = group_data.get("dependencies", {})
            for name, spec in group_deps.items():
                if (
                    isinstance(spec, dict)
                    and "version" not in spec
                    and "git" not in spec
                    and "path" not in spec
                ):
                    issues.append(
                        f"Dependência '{name}' no grupo '{group_name}' sem "
                        f"especificação de versão",
                    )

        return len(issues) == 0, issues

    def _validate_lock_file(self, project_path: Path) -> tuple[bool, list[str]]:
        """Valida poetry.lock."""
        issues = []
        lock_path = project_path / "poetry.lock"

        if not lock_path.exists():
            issues.append("poetry.lock não encontrado - execute 'poetry lock'")
            return False, issues

        try:
            # S603: Use shell=False explicitly for security
            result = subprocess.run(
                ["poetry", "check"],  # Validated command list
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                shell=False,  # Explicit security setting
                timeout=30,  # Prevent hanging
            )

            if result.returncode != 0:
                issues.append("poetry.lock está desatualizado - execute 'poetry lock'")

        except Exception:
            issues.append("Não foi possível verificar status do poetry.lock")

        return len(issues) == 0, issues

    def _collect_project_info(self, data: dict[str, Any]) -> dict[str, Any]:
        """Coleta informações do projeto."""
        poetry = data.get("tool", {}).get("poetry", {})

        info = {
            "name": poetry.get("name", "unknown"),
            "version": poetry.get("version", "unknown"),
            "description": poetry.get("description", ""),
            "python_version": poetry.get("dependencies", {}).get("python", "unknown"),
            "dependency_count": len(poetry.get("dependencies", {}))
            - 1,  # -1 para excluir python
            "group_count": len(poetry.get("group", {})),
            "has_scripts": bool(poetry.get("scripts", {})),
            "has_plugins": bool(poetry.get("plugins", {})),
        }

        # Conta dependências por grupo
        groups = poetry.get("group", {})
        for group_name, group_data in groups.items():
            deps_count = len(group_data.get("dependencies", {}))
            info[f"group_{group_name}_count"] = deps_count

        return info

    def _is_valid_version(self, version: str) -> bool:
        """Verifica se versão segue padrão semântico."""
        # Padrão básico de versão semântica
        pattern = r"^\d+\.\d+\.\d+([.-].*)?$"
        return bool(re.match(pattern, version))

    def validate_workspace(self, workspace_path: Path) -> dict[str, dict[str, Any]]:
        """Valida todos os projetos Poetry no workspace.

        Args:
            workspace_path: Caminho do workspace

        Returns:
            Dict com validação por projeto

        """
        validations: dict[str, dict[str, Any]] = {}

        print_colored("🔍 Validando projetos Poetry no workspace...", Colors.BLUE)

        for pyproject in workspace_path.rglob("pyproject.toml"):
            # Ignora diretórios especiais
            if any(
                p in pyproject.parts
                for p in ["archive", "backup", "node_modules", ".git"]
            ):
                continue

            project_path = pyproject.parent
            project_name = project_path.name

            print_colored(f"\n  📁 Validando {project_name}...", Colors.CYAN)
            validation = self.validate_project(project_path)

            if validation["valid"]:
                print_colored("    ✅ Projeto válido", Colors.GREEN)
            else:
                print_colored("    ❌ Projeto inválido", Colors.RED)
                for error in validation["errors"]:
                    print_colored(f"      - {error}", Colors.RED)

            if validation["warnings"]:
                for warning in validation["warnings"]:
                    print_colored(f"      ⚠️ {warning}", Colors.YELLOW)

            validations[project_name] = validation

        return validations
