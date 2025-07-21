#!/usr/bin/env python3
"""Validador de segurança para operações críticas."""

from __future__ import annotations

import shutil
import tomllib
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import requests
import structlog

if TYPE_CHECKING:
    from pathlib import Path


MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 50

logger = structlog.get_logger(__name__)


class SafetyValidator:
    """Valida operações antes de executá-las para evitar problemas."""

    def __init__(self) -> None:
        """Initialize safety validator."""
        self.known_safe_packages = {
            # Pacotes Python seguros e comuns
            "requests",
            "urllib3",
            "certifi",
            "charset-normalizer",
            "idna",
            "click",
            "colorama",
            "packaging",
            "setuptools",
            "wheel",
            "pip",
            "pydantic",
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "alembic",
            "psycopg2-binary",
            "pytest",
            "pytest-cov",
            "mypy",
            "ruff",
            "black",
            "isort",
            "pre-commit",
            "poetry",
            "pyyaml",
            "tomli",
            "tomllib-w",
            "structlog",
            "python-dotenv",
            "rich",
            "typer",
            # Flext packages
            "flext-core",
            "flext-auth",
            "flext-api",
            "flext-observability",
        }

        self.dangerous_packages = {
            # Pacotes potencialmente perigosos ou problemáticos
            "os-sys",
            "setup-tools",
            "urllib",  # Typosquatting comum
            "request",  # Typosquatting comum
            "beautifulsoup",  # Nome correto é beautifulsoup4
            "PIL",  # Nome correto é Pillow
            "yaml",  # Nome correto é pyyaml
        }

    def validate_package_safety(self, package_name: str) -> dict[str, Any]:
        """Valida se um pacote é seguro para instalação.

        Args:
            package_name: Nome do pacote a validar

        Returns:
            Dict com resultado da validação

        """
        result: dict[str, Any] = {
            "safe": True,
            "package": package_name,
            "issues": [],
            "recommendations": [],
            "confidence": "high",
        }

        # Normaliza nome do pacote
        normalized_name = package_name.lower().replace("_", "-")

        # Verifica se está na lista de pacotes perigosos
        if normalized_name in self.dangerous_packages:
            result["safe"] = False
            result["issues"].append(
                f"Pacote '{package_name}' está na lista de pacotes perigosos",
            )
            result["confidence"] = "high"
            return result

        # Verifica comprimento do nome
        if len(package_name) < MIN_NAME_LENGTH:
            result["safe"] = False
            result["issues"].append("Nome do pacote muito curto")
            result["confidence"] = "high"

        if len(package_name) > MAX_NAME_LENGTH:
            result["safe"] = False
            result["issues"].append("Nome do pacote muito longo")
            result["confidence"] = "medium"

        # Verifica caracteres suspeitos
        suspicious_chars = set(package_name) & {"@", "#", "$", "%", "^", "&", "*"}
        if suspicious_chars:
            result["safe"] = False
            result["issues"].append(f"Caracteres suspeitos no nome: {suspicious_chars}")
            result["confidence"] = "high"

        # Verifica se é pacote conhecido como seguro
        if normalized_name in self.known_safe_packages:
            result["confidence"] = "high"
            result["recommendations"].append("Pacote conhecido como seguro")

        # Verifica existência no PyPI (apenas se não houver issues críticos)
        if result["safe"] and not self._package_exists_on_pypi(package_name):
            result["safe"] = False
            result["issues"].append("Pacote não encontrado no PyPI oficial")
            result["confidence"] = "high"

        return result

    def validate_file_operation(
        self,
        file_path: Path,
        operation: str,
        backup_required: bool = True,
    ) -> dict[str, Any]:
        """Valida operação em arquivo crítico.

        Args:
            file_path: Caminho do arquivo
            operation: Tipo de operação (read, write, delete)
            backup_required: Se backup é obrigatório

        Returns:
            Dict com resultado da validação

        """
        result: dict[str, Any] = {
            "safe": True,
            "file": str(file_path),
            "operation": operation,
            "issues": [],
            "recommendations": [],
        }

        # Verifica se arquivo existe (para operações que precisam)
        if operation in {"read", "write", "delete"} and not file_path.exists():
            result["safe"] = False
            result["issues"].append("Arquivo não encontrado")
            return result

        # Verifica se é arquivo crítico
        critical_files = {
            "pyproject.toml",
            "poetry.lock",
            "Makefile",
            ".gitignore",
            "requirements.txt",
            "setup.py",
            "setup.cfg",
        }

        if file_path.name in critical_files:
            result["recommendations"].append("Arquivo crítico - backup recomendado")

            if backup_required and operation in {"write", "delete"}:
                result["recommendations"].append(
                    "Backup obrigatório para esta operação",
                )

        # Verifica permissões
        if operation == "write" and not self._can_write_file(file_path):
            result["safe"] = False
            result["issues"].append("Sem permissão de escrita")

        if operation == "delete" and not self._can_delete_file(file_path):
            result["safe"] = False
            result["issues"].append("Sem permissão de exclusão")

        return result

    def validate_command_execution(
        self,
        command: list[str],
        working_dir: Path | None = None,
    ) -> dict[str, Any]:
        """Valida execução de comando do sistema.

        Args:
            command: Comando a ser executado
            working_dir: Diretório de trabalho

        Returns:
            Dict com resultado da validação

        """
        result: dict[str, Any] = {
            "safe": True,
            "command": " ".join(command),
            "issues": [],
            "recommendations": [],
        }

        if not command:
            result["safe"] = False
            result["issues"].append("Comando vazio")
            return result

        executable = command[0]

        # Verifica se executável é seguro
        safe_executables = {
            "poetry",
            "pip",
            "python",
            "python3",
            "git",
            "make",
            "pytest",
            "mypy",
            "ruff",
            "black",
            "isort",
        }

        if executable not in safe_executables:
            result["safe"] = False
            result["issues"].append(
                f"Executável '{executable}' não está na lista de comandos seguros",
            )
            return result

        # Verifica se executável existe
        if not shutil.which(executable):
            result["safe"] = False
            result["issues"].append(f"Executável '{executable}' não encontrado no PATH")

        # Verifica argumentos perigosos
        dangerous_args = {"rm", "delete", "--force", "-f", "sudo", "su"}
        command_args = set(command)

        if command_args & dangerous_args:
            result["safe"] = False
            result["issues"].append("Argumentos perigosos detectados")

        # Verifica diretório de trabalho
        if working_dir and not working_dir.exists():
            result["safe"] = False
            result["issues"].append("Diretório de trabalho não existe")

        return result

    def validate_poetry_operation(
        self,
        project_path: Path,
        operation: str,
        packages: list[str] | None = None,
    ) -> dict[str, Any]:
        """Valida operação Poetry específica.

        Args:
            project_path: Caminho do projeto
            operation: Tipo de operação (add, remove, update, install)
            packages: Lista de pacotes (se aplicável)

        Returns:
            Dict com resultado da validação

        """
        result: dict[str, Any] = {
            "safe": True,
            "project": str(project_path),
            "operation": operation,
            "issues": [],
            "recommendations": [],
        }

        # Verifica se projeto Poetry é válido
        pyproject_path = project_path / "pyproject.toml"
        if not pyproject_path.exists():
            result["safe"] = False
            result["issues"].append("pyproject.toml não encontrado")
            return result

        try:
            with pyproject_path.open("rb") as f:
                data = tomllib.load(f)

            if "tool" not in data or "poetry" not in data["tool"]:
                result["safe"] = False
                result["issues"].append(
                    "Configuração Poetry não encontrada no pyproject.toml",
                )
                return result

        except Exception as e:
            result["safe"] = False
            result["issues"].append(f"Erro ao ler pyproject.toml: {e}")
            return result

        # Valida pacotes se fornecidos
        if packages:
            for package in packages:
                package_validation = self.validate_package_safety(package)
                if not package_validation["safe"]:
                    result["safe"] = False
                    result["issues"].extend(
                        [
                            f"Pacote '{package}': {issue}"
                            for issue in package_validation["issues"]
                        ],
                    )

        # Recomendações específicas por operação
        if operation == "add":
            result["recommendations"].append("Verificar compatibilidade de versões")
        elif operation == "update":
            result["recommendations"].append("Criar backup antes de atualizar")
        elif operation == "remove":
            result["recommendations"].append("Verificar dependências antes de remover")

        return result

    def _can_write_file(self, file_path: Path) -> bool:
        """Verifica se é possível escrever no arquivo."""
        try:
            if file_path.exists():
                return file_path.is_file() and bool(file_path.stat().st_mode & 0o200)
            # Verifica se pode criar arquivo no diretório pai
            parent = file_path.parent
            return (
                parent.exists()
                and parent.is_dir()
                and bool(parent.stat().st_mode & 0o200)
            )
        except Exception:
            return False

    def _can_delete_file(self, file_path: Path) -> bool:
        """Verifica se é possível deletar o arquivo."""
        try:
            if not file_path.exists():
                return False
            # Verifica permissão de escrita no diretório pai (necessária para deletar)
            parent = file_path.parent
            return bool(parent.stat().st_mode & 0o200)
        except Exception:
            return False

    def _is_stdlib_module(self, module_name: str) -> bool:
        """Verifica se módulo é da standard library."""
        # Lista básica de módulos stdlib - em produção usar bibliotecas especializadas
        stdlib_modules = {
            "os",
            "sys",
            "re",
            "json",
            "csv",
            "math",
            "random",
            "datetime",
            "pathlib",
            "typing",
            "collections",
            "itertools",
            "functools",
            "subprocess",
            "threading",
            "asyncio",
            "unittest",
            "logging",
            "copy",
            "operator",
            "contextlib",
            "io",
            "string",
            "types",
            "traceback",
            "inspect",
            "ast",
            "hashlib",
            "secrets",
            "uuid",
            "urllib",
            "http",
            "email",
            "sqlite3",
            "pickle",
            "base64",
        }

        return module_name.lower() in stdlib_modules

    def _package_exists_on_pypi(self, package_name: str) -> bool:
        """Verifica se pacote existe no PyPI oficial."""
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"

            # S310: Validate URL scheme before opening
            parsed_url = urlparse(url)
            if parsed_url.scheme not in {"https", "http"}:
                return False

            response = requests.get(
                url,
                timeout=10,
                headers={"User-Agent": "flext-tools/1.0"},
            )

            return response.status_code == 200

        except Exception:
            # Em caso de erro de rede, assumir que existe (falso positivo é melhor)
            return True

    def get_safety_recommendations(
        self,
        operation_type: str,
        context: dict[str, Any],
    ) -> list[str]:
        """Obtém recomendações de segurança para uma operação.

        Args:
            operation_type: Tipo de operação
            context: Contexto da operação

        Returns:
            Lista de recomendações

        """
        recommendations = []

        if operation_type == "package_install":
            recommendations.extend(
                [
                    "Sempre revisar dependências antes de instalar",
                    "Verificar se há versões conhecidamente vulneráveis",
                    "Usar ambientes virtuais isolados",
                    "Manter log de mudanças para rollback",
                ],
            )

        elif operation_type == "file_modification":
            recommendations.extend(
                [
                    "Criar backup antes de modificar arquivos críticos",
                    "Validar integridade após modificação",
                    "Usar controle de versão para track changes",
                ],
            )

        elif operation_type == "command_execution":
            recommendations.extend(
                [
                    "Sempre usar shell=False em subprocess",
                    "Validar entrada de usuário antes de executar",
                    "Usar timeout para evitar hanging",
                    "Log de comandos executados para auditoria",
                ],
            )

        return recommendations
