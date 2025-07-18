"""Descoberta de dependências através de imports Python"""

import ast
import re
from pathlib import Path

from flext_tools.utils import Colors, print_colored, should_ignore_path


class PythonImportDiscovery:
    """Descobre dependências analisando imports Python."""

    def __init__(self, stdlib_modules: set[str]):
        self.stdlib_modules = stdlib_modules

        # Mapeamento de nomes de import para pacotes PyPI
        self.package_mapping = {
            # Mapeamentos básicos
            "cv2": "opencv-python",
            "PIL": "Pillow",
            "yaml": "pyyaml",
            "ldap": "python-ldap",
            "dotenv": "python-dotenv",
            "jose": "python-jose",
            "multipart": "python-multipart",
            "dateutil": "python-dateutil",
            "sklearn": "scikit-learn",
            "bs4": "beautifulsoup4",
            "OpenSSL": "pyOpenSSL",
            "Crypto": "pycryptodome",
            # Mapeamentos de submódulos
            "google": "protobuf",
            "grpc": "grpcio",
            "grpcio_tools": "grpcio-tools",
            # Django apps
            "rest_framework": "djangorestframework",
            "django_filters": "django-filter",
            "django_extensions": "django-extensions",
            "django_redis": "django-redis",
            "django_cors_headers": "django-cors-headers",
            "crispy_forms": "django-crispy-forms",
            "crispy_bootstrap5": "crispy-bootstrap5",
            # Casos especiais
            "psycopg2": "psycopg2-binary",
            "psycopg": "psycopg-binary",
        }

        # CORREÇÃO CRÍTICA: Submódulos que NÃO são pacotes separados
        self.submodules_mapping = {
            # Pydantic submódulos (MAIOR FALSO POSITIVO)
            "pydantic_settings": "pydantic",
            "pydantic.settings": "pydantic",
            "pydantic_core": "pydantic",
            # SQLAlchemy submódulos
            "sqlalchemy.orm": "sqlalchemy",
            "sqlalchemy.ext": "sqlalchemy",
            "sqlalchemy.dialects": "sqlalchemy",
            # Outros submódulos comuns
            "pathlib2": None,  # É stdlib, não pacote externo
        }

    def discover(self, project_path: Path, installed: set[str]) -> dict[str, set[str]]:
        """Descobre dependências analisando arquivos Python."""
        dependencies = {"runtime": set(), "test": set()}

        for py_file in project_path.rglob("*.py"):
            if should_ignore_path(py_file):
                continue

            # Determina categoria baseado no caminho
            category = (
                "test"
                if any(t in str(py_file) for t in ["test", "tests"])
                else "runtime"
            )

            # Analisa imports do arquivo
            imports = self._extract_imports(py_file)

            for import_name in imports:
                # Pula se é da stdlib
                if import_name in self.stdlib_modules:
                    continue

                # CORREÇÃO CRÍTICA: Verifica submódulos primeiro
                if import_name in self.submodules_mapping:
                    parent_package = self.submodules_mapping[import_name]
                    if parent_package is None:
                        continue  # É stdlib ou deve ser ignorado
                    # Verifica se o pacote pai está instalado
                    if self._is_installed(parent_package, installed):
                        continue  # Pacote pai já está instalado
                    import_name = parent_package  # Usa o pacote pai

                # Pula se é um módulo interno do projeto
                if self._is_internal_module(import_name, project_path):
                    continue

                # CORREÇÃO: Detecta pacotes com extras [asyncio], [s3,gcs]
                if "[" in import_name and "]" in import_name:
                    # Extrai nome base do pacote (antes do [)
                    base_package = import_name.split("[")[0]
                    # Verifica se pacote base está instalado
                    if self._is_installed(base_package, installed):
                        continue
                    import_name = base_package

                # Mapeia para nome do pacote PyPI
                package_name = self.package_mapping.get(import_name, import_name)

                # CORREÇÃO: Filtra padrões suspeitos
                if self._is_suspicious_pattern(package_name):
                    continue

                # Adiciona se não está instalado
                if not self._is_installed(package_name, installed):
                    dependencies[category].add(package_name)

        return dependencies

    def _extract_imports(self, py_file: Path) -> set[str]:
        """Extrai todos os imports de um arquivo Python."""
        imports = set()

        try:
            with Path(py_file).open(encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Tenta usar AST primeiro
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split(".")[0])
            except:
                # Se AST falhar, usa regex
                import_patterns = [
                    re.compile(r"^import\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.MULTILINE),
                    re.compile(
                        r"^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import", re.MULTILINE,
                    ),
                ]
                for pattern in import_patterns:
                    matches = pattern.findall(content)
                    imports.update(matches)

        except Exception as e:
            print_colored(
                f"    ⚠️ Erro ao analisar {py_file.name}: {str(e)[:50]}", Colors.YELLOW,
            )

        return imports

    def _is_internal_module(self, module_name: str, project_path: Path) -> bool:
        """Verifica se é um módulo interno do projeto."""
        # Lista de prefixos que indicam módulos internos
        internal_prefixes = [
            "src",
            "tests",
            "test",
            "lib",
            "app",
            "apps",
            "config",
            "utils",
            "common",
            "core",
            "domain",
            "services",
            "models",
            "views",
            "controllers",
            project_path.name,  # Nome do próprio projeto
            project_path.name.replace("-", "_"),  # Variação com underscore
        ]

        # CRÍTICO: Adiciona detecção de módulos flext_* como internos
        if module_name.startswith(("flext_", "flext-")):
            return True

        # CORREÇÃO: Detecta módulos específicos como internos baseado na auditoria
        internal_modules = {
            "analyzer",
            "code_analyzer_web",
            "dashboard",
            "dc_code_analyzer",  # flext-quality
            "generate_config",  # flext-target-oracle-oic
            "connection",  # flext-db-oracle (precisa verificação)
            "tap_oic",
            "target_oracle_wms",
            "dbt_ldap",  # Módulos internos dos taps/targets
        }

        if module_name in internal_modules:
            return True

        # Verifica se é um módulo de outro projeto flext no workspace
        workspace_path = project_path.parent
        for workspace_project in workspace_path.iterdir():
            if workspace_project.is_dir() and workspace_project.name.startswith(
                "flext-",
            ):
                project_module = workspace_project.name.replace("-", "_")
                if module_name.startswith(project_module):
                    return True

        # CORREÇÃO: Verifica se existe arquivo local correspondente
        possible_paths = [
            project_path / "src" / f"{module_name}.py",
            project_path / "src" / module_name / "__init__.py",
            project_path / f"{module_name}.py",
            project_path / module_name / "__init__.py",
            project_path
            / "src"
            / project_path.name.replace("-", "_")
            / f"{module_name}.py",
        ]

        for path in possible_paths:
            if path.exists():
                return True

        return any(module_name.startswith(prefix) for prefix in internal_prefixes)

    def _is_suspicious_pattern(self, package_name: str) -> bool:
        """Detecta padrões suspeitos que são provavelmente falsos positivos."""

        # CORREÇÃO CRÍTICA: Padrões identificados na auditoria
        suspicious_patterns = [
            # Muito curtos (geralmente aliases)
            len(package_name) <= 2,
            # Contém múltiplos separadores
            package_name.count("-") > 2 or package_name.count("_") > 2,
            # Pacotes com cloud providers (geralmente extras)
            any(
                cloud in package_name.lower()
                for cloud in ["azure", "aws", "google-cloud", "boto3"]
            ),
            # Extensões de frameworks específicos (airflow, etc)
            any(
                fw in package_name.lower()
                for fw in ["apache-airflow", "meltano[", "airflow-"]
            ),
            # Conversões PDF/HTML suspeitas
            any(conv in package_name.lower() for conv in ["xhtml2pdf", "weasyprint"]),
            # Pacotes que começam com números
            package_name[0].isdigit() if package_name else False,
        ]

        return any(suspicious_patterns)

    def _is_installed(self, package: str, installed: set[str]) -> bool:
        """Verifica se um pacote já está instalado."""
        variations = {
            package,
            package.lower(),
            package.replace("_", "-"),
            package.replace("-", "_"),
        }
        return any(var in installed for var in variations)
