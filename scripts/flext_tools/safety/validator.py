"""Validador de segurança para operações críticas"""

import subprocess
from pathlib import Path


class SafetyValidator:
    """Valida operações antes de executá-las para evitar problemas."""

    def __init__(self):
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
            "starlette",
            "typing-extensions",
            "sqlalchemy",
            "alembic",
            "psycopg2-binary",
            "redis",
            "celery",
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "mypy",
            "django",
            "djangorestframework",
            "django-cors-headers",
            "pandas",
            "numpy",
            "scipy",
            "matplotlib",
            "seaborn",
            "aiohttp",
            "httpx",
            "websockets",
            "pyyaml",
            "toml",
            "tomli",
            "python-dotenv",
            "python-multipart",
            "jinja2",
            "markupsafe",
            "cryptography",
            "bcrypt",
            "passlib",
            "python-jose",
            "authlib",
            "loguru",
            "structlog",
            "rich",
            "typer",
            "tqdm",
            "progressbar2",
        }

        self.suspicious_packages = {
            # Pacotes que podem ser problemáticos
            "os",
            "sys",
            "subprocess",
            "eval",
            "exec",
            "compile",
            "importlib",
            "__import__",
            "globals",
            "locals",
            "vars",
            # Pacotes que são frequentemente typosquatting
            "reqeusts",
            "urllib",
            "numpy-stubs",
            "beautifulsoup",
        }

    def validate_package_safety(self, package_name: str) -> tuple[bool, list[str]]:
        """
        Valida se um pacote é seguro para instalação.

        Args:
            package_name: Nome do pacote

        Returns:
            Tupla (é_seguro, lista_de_warnings)
        """
        warnings = []
        is_safe = True

        # Remove extras do nome do pacote ([dev], [test], etc)
        clean_package = package_name.split("[")[0].strip()

        # Verifica se é pacote suspeito
        if clean_package.lower() in self.suspicious_packages:
            warnings.append(f"Pacote suspeito: {clean_package}")
            is_safe = False

        # Verifica naming patterns suspeitos
        if self._is_suspicious_naming(clean_package):
            warnings.append(f"Nome suspeito (possível typosquatting): {clean_package}")
            is_safe = False

        # Verifica se é módulo da stdlib
        if self._is_stdlib_module(clean_package):
            warnings.append(f"Tentativa de instalar módulo da stdlib: {clean_package}")
            is_safe = False

        # Verifica se pacote existe no PyPI
        if not self._package_exists_on_pypi(clean_package):
            warnings.append(f"Pacote não encontrado no PyPI: {clean_package}")
            is_safe = False

        return is_safe, warnings

    def validate_dependency_addition(
        self, project_path: Path, dependencies: dict[str, set[str]],
    ) -> tuple[bool, dict[str, list[str]]]:
        """
        Valida adição de dependências a um projeto.

        Args:
            project_path: Caminho do projeto
            dependencies: Dependências por categoria

        Returns:
            Tupla (é_seguro, warnings_por_categoria)
        """
        all_safe = True
        warnings_by_category = {}

        for category, deps in dependencies.items():
            category_warnings = []

            for dep in deps:
                is_safe, dep_warnings = self.validate_package_safety(dep)
                if not is_safe:
                    all_safe = False
                    category_warnings.extend([f"{dep}: {w}" for w in dep_warnings])

            if category_warnings:
                warnings_by_category[category] = category_warnings

        # Validações específicas do projeto
        project_warnings = self._validate_project_specific(project_path, dependencies)
        if project_warnings:
            warnings_by_category["project"] = project_warnings
            all_safe = False

        return all_safe, warnings_by_category

    def validate_poetry_operation(
        self, project_path: Path, operation: str,
    ) -> tuple[bool, list[str]]:
        """
        Valida se uma operação Poetry pode ser executada com segurança.

        Args:
            project_path: Caminho do projeto
            operation: Tipo de operação (add, remove, update, lock)

        Returns:
            Tupla (é_seguro, lista_de_warnings)
        """
        warnings = []
        is_safe = True

        # Verifica se é projeto Poetry válido
        pyproject_path = project_path / "pyproject.toml"
        if not pyproject_path.exists():
            warnings.append("pyproject.toml não encontrado")
            is_safe = False

        # Verifica se Poetry está disponível
        if not self._poetry_is_available():
            warnings.append("Poetry não está instalado ou acessível")
            is_safe = False

        # Verifica se projeto não está corrompido
        if not self._check_project_integrity(project_path):
            warnings.append("Projeto pode estar corrompido")
            is_safe = False

        # Validações específicas por operação
        if operation == "add":
            # Verifica se há espaço em disco
            if not self._has_sufficient_disk_space(project_path):
                warnings.append("Espaço em disco insuficiente")
                is_safe = False

        elif operation == "lock":
            # Verifica se não há dependências conflitantes
            conflicts = self._check_dependency_conflicts(project_path)
            if conflicts:
                warnings.extend([f"Conflito detectado: {c}" for c in conflicts])

        return is_safe, warnings

    def pre_operation_check(
        self, project_path: Path, operation_type: str, details: dict,
    ) -> dict[str, any]:
        """
        Verificação completa antes de operação crítica.

        Args:
            project_path: Caminho do projeto
            operation_type: Tipo de operação (add_dependencies, update_versions, etc)
            details: Detalhes específicos da operação

        Returns:
            Resultado completo da validação
        """
        result = {
            "safe": True,
            "warnings": [],
            "errors": [],
            "recommendations": [],
            "backup_required": True,
            "estimated_time": "desconhecido",
            "risk_level": "low",
        }

        # Verificações gerais
        if not project_path.exists():
            result["safe"] = False
            result["errors"].append(f"Projeto não existe: {project_path}")
            return result

        # Verificações específicas por tipo
        if operation_type == "add_dependencies":
            deps = details.get("dependencies", {})
            is_safe, warnings = self.validate_dependency_addition(project_path, deps)

            if not is_safe:
                result["safe"] = False
                result["risk_level"] = "high"

            for cat_warnings in warnings.values():
                result["warnings"].extend(cat_warnings)

            # Estima tempo baseado no número de dependências
            total_deps = sum(len(deps) for deps in deps.values())
            result["estimated_time"] = f"{total_deps * 10} segundos"

        elif operation_type == "update_versions":
            # Operação de atualização é sempre de risco médio
            result["risk_level"] = "medium"
            result["recommendations"].append("Teste em ambiente isolado primeiro")

        return result

    def _is_suspicious_naming(self, package_name: str) -> bool:
        """Detecta padrões suspeitos no nome do pacote."""
        suspicious_patterns = [
            # Caracteres suspeitos
            lambda x: any(c in x for c in ["_", "-", "."])
            and len(x.split(max([x.count("_"), x.count("-"), x.count(".")]))) < 2,
            # Nomes muito curtos ou muito longos
            lambda x: len(x) < 2 or len(x) > 50,
            # Padrões de typosquatting comum
            lambda x: any(
                known in x.lower() for known in ["reqeusts", "urllib2", "numpy-stubs"]
            ),
        ]

        return any(pattern(package_name) for pattern in suspicious_patterns)

    def _is_stdlib_module(self, module_name: str) -> bool:
        """Verifica se é módulo da stdlib."""
        # Lista básica de módulos stdlib que são comumente confundidos
        stdlib_modules = {
            "os",
            "sys",
            "re",
            "json",
            "urllib",
            "http",
            "email",
            "html",
            "xml",
            "csv",
            "sqlite3",
            "threading",
            "multiprocessing",
            "subprocess",
            "shutil",
            "tempfile",
            "pathlib",
            "datetime",
            "time",
            "math",
            "random",
            "collections",
            "itertools",
            "functools",
            "operator",
            "copy",
            "pickle",
            "hashlib",
            "base64",
            "binascii",
            "struct",
            "array",
            "queue",
            "logging",
            "warnings",
            "traceback",
            "inspect",
            "ast",
        }

        return module_name.lower() in stdlib_modules

    def _package_exists_on_pypi(self, package_name: str) -> bool:
        """Verifica se pacote existe no PyPI (simplificado)."""
        try:
            import json
            import urllib.request

            url = f"https://pypi.org/pypi/{package_name}/json"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read())
                return "info" in data

        except Exception:
            # Em caso de erro de rede, assumimos que existe
            # (melhor falso positivo que bloquear pacote válido)
            return True

    def _poetry_is_available(self) -> bool:
        """Verifica se Poetry está disponível."""
        try:
            result = subprocess.run(
                ["poetry", "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _check_project_integrity(self, project_path: Path) -> bool:
        """Verifica integridade básica do projeto."""
        try:
            import tomllib

            pyproject_path = project_path / "pyproject.toml"
            if not pyproject_path.exists():
                return False

            with Path(pyproject_path).open("rb") as f:
                data = tomllib.load(f)

            # Verifica estrutura básica
            return "tool" in data and "poetry" in data["tool"]

        except Exception:
            return False

    def _has_sufficient_disk_space(self, project_path: Path, min_mb: int = 100) -> bool:
        """Verifica se há espaço em disco suficiente."""
        try:
            import shutil

            free_bytes = shutil.disk_usage(project_path).free
            free_mb = free_bytes / (1024 * 1024)
            return free_mb >= min_mb
        except Exception:
            return True  # Assume que há espaço se não conseguir verificar

    def _check_dependency_conflicts(self, project_path: Path) -> list[str]:
        """Verifica conflitos básicos de dependências."""
        # Implementação simplificada - poderia ser mais sofisticada
        conflicts = []

        try:
            result = subprocess.run(
                ["poetry", "check"],
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0 and "conflict" in result.stderr.lower():
                conflicts.append("Poetry detectou conflitos")

        except Exception:
            pass

        return conflicts

    def _validate_project_specific(
        self, project_path: Path, dependencies: dict[str, set[str]],
    ) -> list[str]:
        """Validações específicas do projeto."""
        warnings = []

        # Verifica se está tentando adicionar dependências que já existem
        try:
            import tomllib

            pyproject_path = project_path / "pyproject.toml"
            with Path(pyproject_path).open("rb") as f:
                data = tomllib.load(f)

            existing_deps = set()

            # Coleta dependências existentes
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            existing_deps.update(poetry_deps.keys())

            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_data in groups.values():
                group_deps = group_data.get("dependencies", {})
                existing_deps.update(group_deps.keys())

            # Verifica duplicatas
            for deps in dependencies.values():
                for dep in deps:
                    clean_dep = dep.split("[")[0].strip()
                    if clean_dep in existing_deps:
                        warnings.append(f"Dependência já existe: {clean_dep}")

        except Exception as e:
            warnings.append(f"Erro ao validar projeto: {e}")

        return warnings
