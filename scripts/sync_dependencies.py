#!/usr/bin/env python3
"""
Script para sincronizar dependências essenciais (dev, test, typings, security) 
de todos os subprojetos com base no pyproject.toml da raiz do workspace FLEXT.

Usa descoberta automática dinâmica com análise de projetos existentes.
"""

import subprocess
import sys
import tomllib
import time
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional, Set, NamedTuple
from dataclasses import dataclass


# Cores para output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_colored(text: str, color: str) -> None:
    """Imprime texto colorido."""
    print(f"{color}{text}{Colors.END}")


def run_command(cmd: List[str], cwd: Path, timeout: int = 300) -> Tuple[bool, str]:
    """Executa um comando e retorna sucesso e output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Timeout após {timeout}s"
    except Exception as e:
        return False, f"Erro: {str(e)}"


def get_stdlib_modules() -> Set[str]:
    """Descobre módulos da stdlib dinamicamente."""
    try:
        # Tenta descobrir módulos da stdlib usando o próprio Python
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; print('\\n'.join(sys.builtin_module_names))",
            ],
            capture_output=True,
            text=True,
        )

        builtin_modules = (
            set(result.stdout.strip().split("\n")) if result.returncode == 0 else set()
        )

        # Adiciona módulos conhecidos da stdlib que não estão em builtin_module_names
        stdlib_extras = {
            "collections",
            "functools",
            "itertools",
            "pathlib",
            "datetime",
            "json",
            "typing",
            "dataclasses",
            "enum",
            "abc",
            "contextlib",
            "logging",
            "uuid",
            "hashlib",
            "base64",
            "urllib",
            "http",
            "email",
            "html",
            "xml",
            "csv",
            "tempfile",
            "shutil",
            "glob",
            "subprocess",
            "threading",
            "asyncio",
            "sqlite3",
            "argparse",
            "unittest",
            "typing_extensions",
            "importlib",
            "inspect",
            "ast",
            "tokenize",
            "linecache",
            "traceback",
            "warnings",
        }

        return builtin_modules | stdlib_extras

    except Exception:
        # Fallback para lista básica se falhar
        return {
            "os",
            "sys",
            "json",
            "typing",
            "pathlib",
            "datetime",
            "time",
            "collections",
            "functools",
            "itertools",
            "contextlib",
            "logging",
            "uuid",
            "re",
            "math",
            "random",
            "hashlib",
            "base64",
            "urllib",
            "http",
            "email",
            "html",
            "xml",
            "csv",
            "io",
            "tempfile",
            "shutil",
            "glob",
            "subprocess",
            "threading",
            "asyncio",
            "sqlite3",
            "argparse",
            "unittest",
            "typing_extensions",
            "importlib",
            "inspect",
            "ast",
            "tokenize",
            "dataclasses",
            "enum",
            "abc",
        }


def discover_existing_dependencies(projects: List[Path]) -> Dict[str, Set[str]]:
    """Descobre todas as dependências já em uso nos projetos existentes."""
    print_colored("🔍 Descobrindo dependências existentes nos projetos...", Colors.BLUE)

    all_deps = {
        "runtime": set(),
        "dev": set(),
        "test": set(),
        "typings": set(),
        "security": set(),
        "docs": set(),
        "lint": set(),
    }

    for project in projects:
        pyproject_file = project / "pyproject.toml"
        if not pyproject_file.exists():
            continue

        try:
            with open(pyproject_file, "rb") as f:
                data = tomllib.load(f)

            # Dependências principais
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for dep_name in poetry_deps.keys():
                if dep_name != "python":
                    all_deps["runtime"].add(dep_name)

            # Dependências de grupos
            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_name, group_data in groups.items():
                group_deps = group_data.get("dependencies", {})

                # Mapeia grupos para categorias
                if group_name in ["dev", "development"]:
                    category = "dev"
                elif group_name in ["test", "testing", "pytest"]:
                    category = "test"
                elif group_name in ["typing", "types", "mypy"]:
                    category = "typings"
                elif group_name in ["security", "safety", "bandit"]:
                    category = "security"
                elif group_name in ["docs", "documentation", "sphinx"]:
                    category = "docs"
                elif group_name in ["lint", "linting", "quality"]:
                    category = "lint"
                else:
                    category = "dev"  # Default

                if category not in all_deps:
                    all_deps[category] = set()

                for dep_name in group_deps.keys():
                    all_deps[category].add(dep_name)

        except Exception as e:
            print_colored(
                f"  ⚠️  Erro lendo {project.name}: {str(e)[:50]}", Colors.YELLOW
            )
            continue

    # Mostra estatísticas
    for category, deps in all_deps.items():
        if deps:
            print_colored(
                f"  📦 {category}: {len(deps)} dependências únicas", Colors.CYAN
            )

    return all_deps


def analyze_imports_intelligently(
    project: Path, stdlib_modules: Set[str], known_deps: Set[str]
) -> Dict[str, Set[str]]:
    """Analisa imports de forma inteligente usando contexto conhecido."""
    print_colored(f"    🔍 Analisando imports inteligentemente...", Colors.BLUE)

    discovered = {"runtime": set(), "test": set()}

    # Mapeia diretórios para categorias
    dir_mapping = {"src": "runtime", "tests": "test", "test": "test"}

    # Regex mais preciso para capturar imports
    import_patterns = [
        re.compile(r"^import\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.MULTILINE),
        re.compile(r"^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import", re.MULTILINE),
    ]

    for dir_name, category in dir_mapping.items():
        dir_path = project / dir_name
        if not dir_path.exists():
            continue

        py_files = list(dir_path.rglob("*.py"))
        if not py_files:
            continue

        imports_found = set()

        for py_file in py_files:
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                for pattern in import_patterns:
                    matches = pattern.findall(content)
                    for match in matches:
                        module_name = match.strip().split(".")[0]

                        # Filtros inteligentes
                        if (
                            module_name
                            and module_name.isidentifier()
                            and not module_name.startswith("_")
                            and module_name not in stdlib_modules
                            and not module_name.startswith("flext")
                            and len(module_name) > 1
                        ):

                            # Se já conhecemos essa dependência, adiciona
                            if module_name in known_deps:
                                imports_found.add(module_name)
                            # Se parece com dependência válida (heurística)
                            elif (
                                module_name.islower()
                                and not module_name.isdigit()
                                and any(
                                    char in module_name
                                    for char in "abcdefghijklmnopqrstuvwxyz"
                                )
                            ):
                                imports_found.add(module_name)

            except Exception:
                continue

        if imports_found:
            discovered[category].update(imports_found)
            print_colored(
                f"      📁 {dir_name}/: {len(imports_found)} dependências", Colors.CYAN
            )

    return discovered


def get_installed_packages(project: Path) -> Set[str]:
    """Retorna set de pacotes já instalados no projeto via Poetry."""
    try:
        # Usa poetry show para listar pacotes instalados
        result = subprocess.run(
            ["poetry", "show", "--only-root"],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=30,
        )

        installed_packages = set()

        if result.returncode == 0:
            # Processa output do poetry show
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    # Formato: "package-name version description"
                    parts = line.split()
                    if parts:
                        package_name = parts[0].strip()
                        installed_packages.add(package_name)

        # Fallback: tenta com poetry show sem --only-root
        if not installed_packages:
            result = subprocess.run(
                ["poetry", "show"],
                cwd=project,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        parts = line.split()
                        if parts:
                            package_name = parts[0].strip()
                            installed_packages.add(package_name)

        return installed_packages

    except Exception:
        return set()


def check_package_exists(package: str) -> bool:
    """Verifica se um package existe no PyPI usando pip."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return True

        # Se não está instalado, tenta buscar no PyPI
        result = subprocess.run(
            [sys.executable, "-m", "pip", "search", package],
            capture_output=True,
            text=True,
            timeout=10,
        )

        return package.lower() in result.stdout.lower()

    except Exception:
        return False


def is_valid_pypi_package(package_name: str) -> bool:
    """Validação INTELIGENTE para verificar se um package é válido para instalação."""

    if not package_name or not isinstance(package_name, str):
        return False

    package_clean = package_name.strip().lower()

    # 1. LISTA EXPANDIDA DE STDLIB - Não devem ser instalados NUNCA
    stdlib_modules_expanded = {
        # Core builtins
        "sys",
        "os",
        "io",
        "re",
        "json",
        "time",
        "datetime",
        "math",
        "random",
        "collections",
        "functools",
        "itertools",
        "typing",
        "pathlib",
        "operator",
        "subprocess",
        "threading",
        "asyncio",
        "unittest",
        "logging",
        "uuid",
        "hashlib",
        "base64",
        "urllib",
        "http",
        "email",
        "html",
        "xml",
        "csv",
        "tempfile",
        "shutil",
        "glob",
        "sqlite3",
        "argparse",
        "importlib",
        "inspect",
        "ast",
        "tokenize",
        "dataclasses",
        "enum",
        "abc",
        "contextlib",
        # Adicionais que frequentemente aparecem como falsos positivos
        "getpass",
        "fnmatch",
        "secrets",
        "platform",
        "contextvars",
        "warnings",
        "traceback",
        "linecache",
        "textwrap",
        "string",
        "keyword",
        "copy",
        "pickle",
        "struct",
        "zlib",
        "gzip",
        "tarfile",
        "zipfile",
        "mmap",
        "signal",
        "socket",
        "ssl",
        "select",
        "fcntl",
        "termios",
        "tty",
        "pty",
        "pwd",
        "spwd",
        "grp",
        "resource",
        "syslog",
        "locale",
    }

    if package_clean in stdlib_modules_expanded:
        return False

    # 2. PROJETOS LOCAIS FLEXT - Nunca instalar
    flext_projects = {
        "flext",
        "flext-core",
        "flext-api",
        "flext-auth",
        "flext-cli",
        "flext-db-oracle",
        "flext-ldap",
        "flext-grpc",
        "flext-web",
        "flext-observability",
        "flext-plugin",
        "flext-quality",
        "flext-meltano",
        "flext-tap-ldap",
        "flext-tap-oracle-oic",
        "flext-tap-oracle-wms",
        "flext-target-ldap",
        "flext-target-oracle",
        "flext-target-oracle-oic",
        "flext-target-oracle-wms",
        "flext-oracle-oic-ext",
        "flext-dbt-ldap",
        "algar-oud-mig",
        "algar_oud_mig",
        "gruponos-meltano-native",
        "gruponos_meltano_native",
        "flexcore",
    }

    if package_clean.replace("_", "-") in flext_projects or package_clean.startswith(
        "flext"
    ):
        return False

    # 3. PYTEST PLUGINS - São válidos e devem ser aceitos
    pytest_plugins = {
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "pytest-xdist",
        "pytest-timeout",
        "pytest-env",
        "pytest-sugar",
        "pytest-clarity",
        "pytest-httpx",
        "pytest-randomly",
        "pytest-benchmark",
        "pytest-deadfixtures",
        "pytest-postgresql",
        "pytest-redis",
        "pytest-django",
        "pytest-flask",
        "pytest-html",
        "pytest-json-report",
        "pytest-rerunfailures",
    }

    if package_clean in pytest_plugins:
        return True

    # 4. PACKAGES CONHECIDOS VÁLIDOS
    known_valid_packages = {
        # Core packages
        "requests",
        "click",
        "pydantic",
        "fastapi",
        "sqlalchemy",
        "redis",
        "pytest",
        "psycopg2",
        "psycopg2-binary",
        "psutil",
        "pyyaml",
        "toml",
        "boto3",
        "celery",
        "django",
        "flask",
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "seaborn",
        "pillow",
        "opencv-python",
        "tensorflow",
        "torch",
        "scikit-learn",
        "jupyter",
        "ipython",
        "notebook",
        "jupyterlab",
        "aiohttp",
        "httpx",
        "urllib3",
        "certifi",
        "chardet",
        "idna",
        "six",
        "setuptools",
        "wheel",
        "pip",
        "poetry-core",
        "black",
        "isort",
        "flake8",
        "mypy",
        "coverage",
        "tox",
        "pre-commit",
        "bandit",
        "safety",
        "rich",
        "typer",
        "loguru",
        "structlog",
        "prometheus-client",
        "elasticsearch",
        "sentry-sdk",
        "alembic",
        "marshmallow",
        "apispec",
        "jinja2",
        "mako",
        "bcrypt",
        "passlib",
        "cryptography",
        "pyjwt",
        "python-jose",
        "python-ldap",
        "oracledb",
        "pymongo",
        "motor",
        "asyncpg",
        "databases",
        "gino",
        "tortoise-orm",
        "peewee",
        "meltano",
        "dbt-core",
        "apache-airflow",
        "prefect",
        "dagster",
        "luigi",
        "kedro",
        "mlflow",
        "wandb",
        "tensorboard",
        "optuna",
        "hyperopt",
        "ray",
        "dask",
        "modin",
        "vaex",
        "streamlit",
        "dash",
        "plotly",
        "bokeh",
        "altair",
        "folium",
        "geopandas",
        # Packages específicos que aparecem nos projetos
        "lato",
        "tenacity",
        "faker",
        "factory-boy",
        "hypothesis",
        "responses",
        "freezegun",
        "mock",
        "uuid6",
        "dynaconf",
        "halo",
        "questionary",
        "tabulate",
        "prettytable",
        "prompt-toolkit",
        "keyring",
        "paramiko",
        "watchdog",
        "tqdm",
        "pathlib2",
        "python-dotenv",
        "email-validator",
        "python-multipart",
        "slowapi",
        "gunicorn",
        "uvicorn",
        "itsdangerous",
        "argon2",
        "grpcio",
        "grpcio-tools",
        "grpcio-reflection",
        "grpcio-status",
        "grpcio-health-checking",
        "protobuf",
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-instrumentation-fastapi",
        "opentelemetry-instrumentation-grpc",
        "aiopg",
        "sqlparse",
        "docker",
        "typing-extensions",
        "python-dateutil",
        "aiosqlite",
        "asyncio-mqtt",
        "ldap3",
        "orjson",
        "pydantic-settings",
        "prometheus_client",
        "aiogrpc",
        # Adiciona mais packages comuns que podem ser descobertos
        "meltano",
        "singer-python",
        "pipelinewise-singer-python",
        "target-jsonl",
        "target-csv",
        "target-postgres",
        "tap-csv",
        "tap-spreadsheets-anywhere",
        "smart-open",
        "backoff",
        "pytz",
        "pendulum",
        "arrow",
        "colorama",
        "termcolor",
        "poetry",
        "setuptools-scm",
        "build",
        "twine",
        "invoke",
        "nox",
        "hatch",
        "flit",
        "pdm",
        "pipenv",
        "virtualenv",
        "tox",
        "pytest-runner",
        "pytest-django",
        "pytest-flask",
        "pytest-aiohttp",
        "pytest-tornasync",
        "pytest-twisted",
        "twisted",
        "tornado",
        "gevent",
        "eventlet",
        "greenlet",
        "msgpack",
        "ujson",
        "simplejson",
        "rapidjson",
        "cython",
        "numba",
        "joblib",
        "cloudpickle",
        "dill",
        "pathos",
        "multiprocess",
        "billiard",
        "kombu",
        "amqp",
        "vine",
        "flower",
        "django-celery-beat",
        "django-celery-results",
        "redis-py-cluster",
        "hiredis",
        "aioredis",
        "aiocache",
        "diskcache",
        "cachetools",
        "dogpile.cache",
        "beaker",
        "pylibmc",
        "python-memcached",
        "pymemcache",
        "kazoo",
        "pyzk",
        "consul",
        "etcd3",
        "hvac",
        "kubernetes",
        "docker-compose",
        "podman-py",
        "ansible",
        "fabric",
        "pyinfra",
        "supervisor",
        "circus",
        "honcho",
        "huey",
        "rq",
        "mrq",
        "dramatiq",
        "apscheduler",
        "schedule",
        "croniter",
        "python-crontab",
        "django-cron",
        "django-extensions",
        "django-debug-toolbar",
        "django-silk",
        "django-cors-headers",
        "django-filter",
        "django-guardian",
        "django-mptt",
        "django-treebeard",
        "django-taggit",
        "django-haystack",
        "whoosh",
        "xapian",
        "pysolr",
        "elasticsearch-dsl",
        "django-elasticsearch-dsl",
        "scout",
        "meilisearch",
        "typesense",
        "qdrant-client",
        "weaviate-client",
        "pinecone-client",
        "chromadb",
        "langchain",
        "llama-index",
        "sentence-transformers",
        "transformers",
        "datasets",
        "tokenizers",
        "accelerate",
        "bitsandbytes",
        "peft",
        "trl",
        "einops",
        "timm",
        "albumentations",
        "imgaug",
        "scikit-image",
        "imageio",
        "opencv-contrib-python",
        "pytesseract",
        "pdf2image",
        "pypdf",
        "pypdf2",
        "pdfplumber",
        "camelot-py",
        "tabula-py",
        "xlrd",
        "xlwt",
        "xlsxwriter",
        "openpyxl",
        "pyexcel",
        "pandas-profiling",
        "ydata-profiling",
        "sweetviz",
        "dtale",
        "bamboolib",
        "pandasql",
        "duckdb",
        "polars",
        "pyarrow",
        "fastparquet",
        "h5py",
        "tables",
        "netcdf4",
        "xarray",
        "zarr",
        "numexpr",
        "bottleneck",
        "datashader",
        "holoviews",
        "hvplot",
        "panel",
        "voila",
        "solara",
        "nicegui",
        "reflex",
        "anvil",
        "pynecone",
    }

    if package_clean in known_valid_packages:
        return True

    # 5. TYPES PACKAGES - Sempre válidos
    if package_clean.startswith("types-"):
        return True

    # 6. VALIDAÇÃO POR PADRÕES
    # Aceita packages com padrões válidos do PyPI
    valid_patterns = [
        r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$",  # kebab-case (ex: python-jose)
        r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$",  # snake_case (ex: pydantic_settings)
        r"^py[a-z][a-z0-9-]*$",  # py prefixed (ex: pyjwt)
        r"^python-[a-z][a-z0-9-]*$",  # python- prefixed
        r"^[a-z][a-z0-9]*[a-z0-9]$",  # simples sem separadores (ex: uvicorn)
    ]

    # 7. FILTROS RESTRITIVOS FINAIS
    if (
        not package_clean
        or len(package_clean) < 2
        or len(package_clean) > 50
        or package_clean.startswith("test")
        and not package_clean.startswith("testcontainers")
        or package_clean.startswith("src")
        or package_clean
        in {
            "main",
            "app",
            "api",
            "web",
            "cli",
            "ui",
            "config",
            "utils",
            "common",
            "shared",
            "internal",
            "core",
            "data",
        }
        or not package_clean.replace("-", "").replace("_", "").isalnum()
        or any(char.isspace() for char in package_clean)
        or ".." in package_clean
    ):
        return False

    # 8. VALIDA CONTRA PADRÕES
    for pattern in valid_patterns:
        if re.match(pattern, package_clean):
            return True

    return False


def discover_typings_automatically(project: Path, runtime_libs: Set[str]) -> Set[str]:
    """Descobre packages de typings usando APENAS análise do mypy."""
    print_colored(
        f"      🔍 Descobrindo typings com mypy (única fonte confiável)...", Colors.BLUE
    )

    typings_discovered: Set[str] = set()

    # Verifica se mypy está disponível
    success, _ = run_command(["python", "-c", "import mypy"], project, timeout=5)
    if not success:
        print_colored(
            f"      ⚠️  MyPy não disponível - pulando descoberta de typings",
            Colors.YELLOW,
        )
        return typings_discovered

    # Executa mypy em diferentes diretórios do projeto
    directories_to_check = []
    for dir_name in ["src", "tests", "test", "."]:
        dir_path = project / dir_name
        if dir_path.exists() and any(dir_path.rglob("*.py")):
            directories_to_check.append(dir_name)

    if not directories_to_check:
        print_colored(
            f"      ➖ Nenhum diretório Python encontrado para análise", Colors.YELLOW
        )
        return typings_discovered

    print_colored(
        f"      📁 Analisando {len(directories_to_check)} diretórios com mypy...",
        Colors.BLUE,
    )

    # Padrões regex para detectar stubs faltantes na saída do mypy
    mypy_patterns = [
        # Padrão mais comum: Library stubs not installed
        r'Library stubs not installed for "([^"]+)"',
        r'Skipping analyzing "([^"]+)": module is installed, but missing library stubs',
        # Padrão direto de sugestão do mypy
        r'python -m pip install (types-[^\s"]+)',
        r'Try installing (types-[^\s"]+)',
        # Padrão para imports sem stubs
        r'Cannot find implementation or library stub for module named "([^"]+)"',
        r'Module has no attribute.*Consider using.*install (types-[^\s"]+)',
    ]

    for directory in directories_to_check:
        print_colored(f"        🔍 Analisando {directory}/...", Colors.BLUE)

        # Comando mypy otimizado para detectar stubs faltantes
        mypy_cmd = [
            "python",
            "-m",
            "mypy",
            "--no-error-summary",
            "--show-error-codes",
            "--ignore-missing-imports",  # Não queremos erros de imports não tipados
            "--warn-unused-ignores",
            directory,
        ]

        success, output = run_command(mypy_cmd, project, timeout=60)

        if not success and "No module named 'mypy'" in output:
            continue

        # Analisa a saída do mypy linha por linha
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Aplica os padrões regex para encontrar stubs faltantes
            for pattern in mypy_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    if match.startswith("types-"):
                        # É uma sugestão direta do mypy
                        typings_discovered.add(match)
                        print_colored(
                            f"          ✅ {match} (sugestão direta do mypy)",
                            Colors.GREEN,
                        )
                    else:
                        # É um módulo sem stub - gera o nome do package
                        module_name = match.replace("_", "-")
                        typing_package = f"types-{module_name}"
                        typings_discovered.add(typing_package)
                        print_colored(
                            f"          📦 {typing_package} (para módulo {match})",
                            Colors.CYAN,
                        )

    # Validação adicional: verifica se os packages de typing realmente existem
    if typings_discovered:
        print_colored(
            f"      🔍 Validando {len(typings_discovered)} packages de typing...",
            Colors.BLUE,
        )

        validated_typings = set()
        for typing_pkg in typings_discovered:
            # Verifica se o package existe tentando obter informações
            success, _ = run_command(
                ["python", "-m", "pip", "show", typing_pkg], project, timeout=10
            )

            if success:
                validated_typings.add(typing_pkg)
                print_colored(f"          ✅ {typing_pkg} (já instalado)", Colors.GREEN)
            else:
                # Verifica se existe no PyPI (busca simplificada)
                success, search_output = run_command(
                    [
                        "python",
                        "-c",
                        f"import urllib.request; print(urllib.request.urlopen('https://pypi.org/project/{typing_pkg}/').getcode())",
                    ],
                    project,
                    timeout=15,
                )

                if success and "200" in search_output:
                    validated_typings.add(typing_pkg)
                    print_colored(
                        f"          📦 {typing_pkg} (disponível no PyPI)", Colors.CYAN
                    )
                else:
                    print_colored(
                        f"          ❌ {typing_pkg} (não encontrado)", Colors.RED
                    )

        typings_discovered = validated_typings

    if typings_discovered:
        print_colored(
            f"      ✅ MyPy identificou {len(typings_discovered)} typings necessários",
            Colors.GREEN,
        )
        print_colored(
            f"         📋 {', '.join(sorted(typings_discovered))}", Colors.CYAN
        )
    else:
        print_colored(f"      ✅ MyPy não identificou typings faltantes", Colors.GREEN)

    return typings_discovered


def extract_essential_dependencies() -> Dict[str, List[str]]:
    """Extrai dependências essenciais do pyproject.toml da raiz."""
    root_pyproject = Path("pyproject.toml")

    if not root_pyproject.exists():
        print_colored("❌ pyproject.toml da raiz não encontrado!", Colors.RED)
        sys.exit(1)

    try:
        with open(root_pyproject, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        print_colored(f"❌ Erro ao ler pyproject.toml: {e}", Colors.RED)
        sys.exit(1)

    poetry_groups = data.get("tool", {}).get("poetry", {}).get("group", {})

    # Grupos essenciais em ordem de prioridade (typings será preenchido dinamicamente)
    essential_groups = ["dev", "test", "security"]

    dependencies = {}
    total_deps = 0

    print_colored("🔍 Extraindo dependências essenciais...", Colors.BLUE)

    for group in essential_groups:
        if group in poetry_groups:
            group_deps = poetry_groups[group].get("dependencies", {})
            if group_deps:
                # Converte para lista de strings "package@version"
                dep_list = []
                for package, version in group_deps.items():
                    if isinstance(version, dict):
                        if "version" in version:
                            clean_version = (
                                str(version["version"]).strip().strip('"').strip("'")
                            )
                            dep_list.append(f"{package}@{clean_version}")
                    else:
                        clean_version = str(version).strip().strip('"').strip("'")
                        dep_list.append(f"{package}@{clean_version}")

                if dep_list:
                    dependencies[group] = dep_list
                    total_deps += len(dep_list)
                    print_colored(
                        f"  ✅ {group:<8} → {len(dep_list):>2} dependências",
                        Colors.GREEN,
                    )
                else:
                    print_colored(f"  ➖ {group:<8} → vazio", Colors.YELLOW)
            else:
                print_colored(f"  ➖ {group:<8} → vazio", Colors.YELLOW)
        else:
            print_colored(f"  ❌ {group:<8} → não encontrado", Colors.RED)

    print_colored(
        f"  🔍 typings    → descobertos dinamicamente por projeto", Colors.CYAN
    )

    print_colored(
        f"\n📦 Total: {total_deps} dependências base + typings dinâmicos", Colors.CYAN
    )
    return dependencies


def find_flext_projects() -> List[Path]:
    """Encontra projetos FLEXT com pyproject.toml."""
    projects = []

    # Descobre projetos dinamicamente
    for item in Path(".").iterdir():
        if item.is_dir() and not item.name.startswith("."):
            pyproject_file = item / "pyproject.toml"

            # Inclui se tem pyproject.toml e parece ser projeto Python
            if pyproject_file.exists():
                try:
                    with open(pyproject_file, "rb") as f:
                        data = tomllib.load(f)

                    # Verifica se é projeto Poetry
                    if "tool" in data and "poetry" in data["tool"]:
                        projects.append(item)
                        print_colored(f"  📁 {item.name}", Colors.CYAN)

                except Exception:
                    continue

    return sorted(projects)


def check_poetry_lock_status(project: Path) -> Tuple[bool, str]:
    """Verifica se o poetry.lock está atualizado com o pyproject.toml."""
    poetry_lock = project / "poetry.lock"
    pyproject_file = project / "pyproject.toml"

    if not poetry_lock.exists():
        return False, "poetry.lock não existe"

    if not pyproject_file.exists():
        return False, "pyproject.toml não existe"

    # Verifica se poetry.lock é mais antigo que pyproject.toml
    if poetry_lock.stat().st_mtime < pyproject_file.stat().st_mtime:
        return False, "poetry.lock desatualizado"

    # Usa poetry check para verificar consistência
    success, output = run_command(["poetry", "check"], project, timeout=30)
    if not success:
        return False, f"poetry check falhou: {output[:50]}..."

    return True, "poetry.lock está atualizado"


def ensure_poetry_lock(project: Path) -> bool:
    """Garante que o projeto tenha um poetry.lock válido."""
    is_valid, reason = check_poetry_lock_status(project)

    if is_valid:
        print_colored(f"    ✅ poetry.lock válido", Colors.GREEN)
        return True

    print_colored(f"    ⚠️  {reason} - RECRIANDO...", Colors.YELLOW)

    # Remove poetry.lock antigo se existir
    poetry_lock = project / "poetry.lock"
    if poetry_lock.exists():
        poetry_lock.unlink()

    # Gera novo poetry.lock
    success, output = run_command(["poetry", "lock"], project, timeout=300)

    if success:
        print_colored(f"    ✅ poetry.lock recriado", Colors.GREEN)
        return True
    else:
        print_colored(f"    ❌ Falha ao recriar poetry.lock", Colors.RED)
        if "not found" in output.lower():
            print_colored(f"        💡 Poetry não encontrado", Colors.YELLOW)
        elif "pyproject.toml" in output.lower():
            print_colored(f"        💡 Problema no pyproject.toml", Colors.YELLOW)
        elif "dependency" in output.lower():
            print_colored(f"        💡 Problema com dependências", Colors.YELLOW)
        else:
            print_colored(f"        🔍 {output[:80]}...", Colors.RED)
        return False


def sync_project_group(
    project: Path, group: str, dependencies: List[str]
) -> Tuple[bool, str]:
    """Sincroniza um grupo de dependências de uma vez só."""
    if not dependencies:
        return True, "Nenhuma dependência"

    print_colored(f"    📦 {group:<8} → {len(dependencies):>2} deps", Colors.MAGENTA)

    # Obtém lista de pacotes já instalados
    installed_packages = get_installed_packages(project)

    # Filtra dependências que já estão instaladas
    packages_to_install = []
    already_installed = []

    for dep in dependencies:
        package_name = (
            dep.split("@")[0]
            .split("==")[0]
            .split(">=")[0]
            .split("<=")[0]
            .split("~=")[0]
        )
        if package_name in installed_packages:
            already_installed.append(package_name)
        else:
            packages_to_install.append(dep)

    # Se todos os pacotes já estão instalados
    if not packages_to_install:
        elapsed = 0.1  # Processo muito rápido
        print(f"      ✅ {len(already_installed)} já instalados ({elapsed:.1f}s)")
        return True, f"{len(already_installed)} pacotes já instalados"

    # Constrói comando para instalar apenas as dependências que ainda não estão instaladas
    cmd = ["poetry", "add"] + packages_to_install + ["--group", group]

    print(
        f"      🔄 Instalando {len(packages_to_install)} packages...",
        end="",
        flush=True,
    )
    start_time = time.time()

    success, output = run_command(cmd, project, timeout=600)  # 10 minutos
    elapsed = time.time() - start_time

    if success:
        # Conta quantos foram realmente atualizados
        updated_count = output.lower().count("updating") + output.lower().count(
            "installing"
        )
        if updated_count > 0:
            msg = f" ✅ {updated_count} novos"
            if already_installed:
                msg += f" + {len(already_installed)} já instalados"
            print(f"{msg} ({elapsed:.1f}s)")
        else:
            print(f" ➖ já sincronizado ({elapsed:.1f}s)")
        return True, f"{updated_count} atualizados"
    else:
        print(f" ❌ FALHA ({elapsed:.1f}s)")
        # Mostra apenas erros relevantes
        if "not found" in output.lower():
            print_colored(f"        💡 Alguns packages não encontrados", Colors.YELLOW)
        elif "timeout" in output.lower():
            print_colored(f"        ⏱️  Timeout - tente novamente", Colors.YELLOW)
        elif len(output.strip()) > 0:
            # Mostra apenas as primeiras linhas do erro
            error_lines = output.split("\n")[:3]
            for line in error_lines:
                if line.strip():
                    print_colored(f"        🔍 {line[:70]}...", Colors.RED)
        return False, "Falha na instalação"


# Estruturas para tracking de versões
@dataclass
class VersionChange:
    package: str
    old_version: str
    new_version: str
    change_type: str  # 'upgrade', 'downgrade', 'install', 'remove'
    reason: str
    project: str


class DependencyAnalyzer:
    """Classe para análise avançada de dependências."""

    def __init__(self, stdlib_modules: Set[str]):
        self.stdlib_modules = stdlib_modules
        self.known_package_patterns = {
            # Padrões de imports que indicam packages específicos
            r"from\s+django": "django",
            r"import\s+django": "django",
            r"from\s+flask": "flask",
            r"import\s+flask": "flask",
            r"from\s+fastapi": "fastapi",
            r"import\s+fastapi": "fastapi",
            r"from\s+sqlalchemy": "sqlalchemy",
            r"import\s+sqlalchemy": "sqlalchemy",
            r"from\s+pydantic": "pydantic",
            r"import\s+pydantic": "pydantic",
            r"from\s+requests": "requests",
            r"import\s+requests": "requests",
            r"from\s+click": "click",
            r"import\s+click": "click",
            r"from\s+pytest": "pytest",
            r"import\s+pytest": "pytest",
            r"from\s+redis": "redis",
            r"import\s+redis": "redis",
            r"psycopg2": "psycopg2-binary",
            r"oracledb": "oracledb",
            r"from\s+ldap": "python-ldap",
            r"import\s+ldap": "python-ldap",
            r"from\s+yaml": "pyyaml",
            r"import\s+yaml": "pyyaml",
            r"from\s+toml": "toml",
            r"import\s+toml": "toml",
            r"from\s+boto3": "boto3",
            r"import\s+boto3": "boto3",
            r"from\s+celery": "celery",
            r"import\s+celery": "celery",
            r"from\s+aiohttp": "aiohttp",
            r"import\s+aiohttp": "aiohttp",
            r"from\s+httpx": "httpx",
            r"import\s+httpx": "httpx",
        }

        # Padrões de strings que indicam dependências
        self.string_patterns = {
            r"pip\s+install\s+([a-zA-Z0-9\-_]+)": "pip_install",
            r"poetry\s+add\s+([a-zA-Z0-9\-_]+)": "poetry_add",
            r"requirements\.txt": "requirements_file",
            r"setup\.py": "setup_file",
            r"pyproject\.toml": "pyproject_file",
        }

    def analyze_deep_dependencies(self, project: Path) -> Dict[str, Set[str]]:
        """Análise profunda e robusta de dependências."""
        print_colored(f"    🔍 Análise PROFUNDA de dependências...", Colors.BLUE)

        dependencies = {"runtime": set(), "test": set(), "dev": set()}

        # 1. Analisa arquivos Python
        python_deps = self._analyze_python_files(project)
        dependencies["runtime"].update(python_deps.get("runtime", set()))
        dependencies["test"].update(python_deps.get("test", set()))

        # 2. Analisa arquivos de configuração
        config_deps = self._analyze_config_files(project)
        for category, deps in config_deps.items():
            dependencies[category].update(deps)

        # 3. Analisa requirements.txt se existir
        requirements_deps = self._analyze_requirements_files(project)
        dependencies["runtime"].update(requirements_deps)

        # 4. Analisa setup.py se existir
        setup_deps = self._analyze_setup_py(project)
        dependencies["runtime"].update(setup_deps)

        # 5. Analisa strings e comentários
        string_deps = self._analyze_strings_and_comments(project)
        dependencies["runtime"].update(string_deps)

        return dependencies

    def _analyze_python_files(self, project: Path) -> Dict[str, Set[str]]:
        """Análise avançada de arquivos Python com detecção melhorada."""
        dependencies = {"runtime": set(), "test": set()}

        for py_file in project.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Determina categoria baseado no caminho
                category = (
                    "test"
                    if any(test_dir in str(py_file) for test_dir in ["test", "tests"])
                    else "runtime"
                )

                # Análise com regex patterns
                for pattern, package in self.known_package_patterns.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        dependencies[category].add(package)

                # Análise de imports padrão
                import_patterns = [
                    re.compile(r"^import\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.MULTILINE),
                    re.compile(
                        r"^from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import", re.MULTILINE
                    ),
                ]

                # Análise de imports dinâmicos e condicionais
                dynamic_patterns = [
                    # importlib imports
                    re.compile(r"importlib\.import_module\s*\(\s*['\"]([^'\"]+)['\"]"),
                    # __import__ calls
                    re.compile(r"__import__\s*\(\s*['\"]([^'\"]+)['\"]"),
                    # try/except imports
                    re.compile(r"try:\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)"),
                    re.compile(r"try:\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import"),
                    # Optional imports in comments
                    re.compile(r"#\s*requires?\s*:\s*([a-zA-Z_][a-zA-Z0-9_-]*)"),
                    re.compile(r"#\s*pip\s+install\s+([a-zA-Z_][a-zA-Z0-9_-]+)"),
                ]

                all_patterns = import_patterns + dynamic_patterns

                for pattern in all_patterns:
                    matches = pattern.findall(content)
                    for match in matches:
                        module_name = match.strip().split(".")[0]
                        if self._is_valid_external_package(module_name):
                            dependencies[category].add(module_name)

                # Análise de strings que podem indicar dependências
                string_dependency_patterns = [
                    # Django apps
                    re.compile(r"INSTALLED_APPS\s*=.*?['\"]([a-zA-Z_][a-zA-Z0-9_\.]*)['\"]", re.DOTALL),
                    # FastAPI/Flask extensions
                    re.compile(r"app\.include_router.*?['\"]([a-zA-Z_][a-zA-Z0-9_]*)['\"]"),
                    # Plugin systems
                    re.compile(r"load_plugin.*?['\"]([a-zA-Z_][a-zA-Z0-9_]*)['\"]"),
                    # Entry points
                    re.compile(r"entry_points.*?['\"]([a-zA-Z_][a-zA-Z0-9_]*)['\"]"),
                ]

                for pattern in string_dependency_patterns:
                    matches = pattern.findall(content)
                    for match in matches:
                        module_name = match.strip().split(".")[0]
                        if self._is_valid_external_package(module_name):
                            dependencies[category].add(module_name)

            except Exception as e:
                print_colored(
                    f"      ⚠️  Erro analisando {py_file.name}: {str(e)[:30]}",
                    Colors.YELLOW,
                )

        return dependencies

    def _analyze_config_files(self, project: Path) -> Dict[str, Set[str]]:
        """Analisa arquivos de configuração de forma abrangente."""
        dependencies = {"runtime": set(), "test": set(), "dev": set()}

        # Analisa pyproject.toml
        pyproject_file = project / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, "rb") as f:
                    data = tomllib.load(f)

                # Dependências principais
                poetry_deps = (
                    data.get("tool", {}).get("poetry", {}).get("dependencies", {})
                )
                for dep_name in poetry_deps.keys():
                    if dep_name != "python":
                        dependencies["runtime"].add(dep_name)

                # Dependências de grupos
                groups = data.get("tool", {}).get("poetry", {}).get("group", {})
                for group_name, group_data in groups.items():
                    group_deps = group_data.get("dependencies", {})
                    category = "test" if group_name in ["test", "testing"] else "dev"
                    for dep_name in group_deps.keys():
                        dependencies[category].add(dep_name)

                # Analisa configurações de outras ferramentas
                # pytest
                pytest_config = data.get("tool", {}).get("pytest", {})
                if "ini_options" in pytest_config:
                    plugins = pytest_config["ini_options"].get("plugins", [])
                    for plugin in plugins:
                        if isinstance(plugin, str):
                            dependencies["test"].add(plugin)

                # mypy
                mypy_config = data.get("tool", {}).get("mypy", {})
                if "plugins" in mypy_config:
                    for plugin in mypy_config["plugins"]:
                        if isinstance(plugin, str):
                            dependencies["dev"].add(plugin)

                # black, isort, ruff
                for tool in ["black", "isort", "ruff", "flake8", "bandit"]:
                    if tool in data.get("tool", {}):
                        dependencies["dev"].add(tool)

            except Exception:
                pass

        # Analisa tox.ini
        tox_file = project / "tox.ini"
        if tox_file.exists():
            try:
                with open(tox_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Procura por deps em tox
                    deps_pattern = re.compile(r"deps\s*=\s*([^\n]+(?:\n\s+[^\n]+)*)")
                    matches = deps_pattern.findall(content)
                    for match in matches:
                        for line in match.split("\n"):
                            line = line.strip()
                            if line and not line.startswith("#"):
                                pkg = re.split(r"[>=<!=]", line)[0].strip()
                                if pkg:
                                    dependencies["test"].add(pkg)
            except Exception:
                pass

        # Analisa .pre-commit-config.yaml
        precommit_file = project / ".pre-commit-config.yaml"
        if precommit_file.exists():
            try:
                import yaml
                with open(precommit_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "repos" in data:
                        for repo in data["repos"]:
                            if "hooks" in repo:
                                for hook in repo["hooks"]:
                                    if "id" in hook:
                                        hook_id = hook["id"]
                                        # Mapeia hooks conhecidos para packages
                                        hook_to_package = {
                                            "black": "black",
                                            "isort": "isort",
                                            "flake8": "flake8",
                                            "mypy": "mypy",
                                            "ruff": "ruff",
                                            "bandit": "bandit",
                                            "pytest": "pytest",
                                        }
                                        if hook_id in hook_to_package:
                                            dependencies["dev"].add(hook_to_package[hook_id])
            except Exception:
                pass

        # Analisa Dockerfile
        dockerfile = project / "Dockerfile"
        if dockerfile.exists():
            try:
                with open(dockerfile, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Procura por pip install em Dockerfile
                    pip_pattern = re.compile(r"pip\s+install\s+([^\s&|;]+)")
                    matches = pip_pattern.findall(content)
                    for match in matches:
                        pkg = match.strip()
                        if pkg and not pkg.startswith("-"):
                            dependencies["runtime"].add(pkg)
            except Exception:
                pass

        # Analisa docker-compose.yml
        compose_files = list(project.glob("docker-compose*.yml")) + list(project.glob("docker-compose*.yaml"))
        for compose_file in compose_files:
            try:
                import yaml
                with open(compose_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "services" in data:
                        for service_name, service_config in data["services"].items():
                            if isinstance(service_config, dict):
                                # Procura por imagens que indicam dependências
                                image = service_config.get("image", "")
                                if "python" in image:
                                    # Analisa environment vars que podem indicar packages
                                    env_vars = service_config.get("environment", {})
                                    for var, value in env_vars.items():
                                        if "PACKAGE" in var or "MODULE" in var:
                                            if isinstance(value, str) and value:
                                                dependencies["runtime"].add(value)
            except Exception:
                pass

        return dependencies

    def _analyze_requirements_files(self, project: Path) -> Set[str]:
        """Analisa arquivos requirements.txt."""
        dependencies = set()

        for req_file in project.rglob("requirements*.txt"):
            try:
                with open(req_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            # Extrai nome do package (remove versão)
                            package_name = re.split(r"[>=<==!]", line)[0].strip()
                            if package_name:
                                dependencies.add(package_name)
            except Exception:
                pass

        return dependencies

    def _analyze_setup_py(self, project: Path) -> Set[str]:
        """Analisa setup.py."""
        dependencies = set()

        setup_file = project / "setup.py"
        if setup_file.exists():
            try:
                with open(setup_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Procura por install_requires
                install_requires_pattern = r"install_requires\s*=\s*\[(.*?)\]"
                matches = re.search(install_requires_pattern, content, re.DOTALL)
                if matches:
                    requirements_text = matches.group(1)
                    # Extrai packages individuais
                    for line in requirements_text.split(","):
                        line = line.strip().strip("\"'")
                        if line:
                            package_name = re.split(r"[>=<==!]", line)[0].strip()
                            if package_name:
                                dependencies.add(package_name)

            except Exception:
                pass

        return dependencies

    def _analyze_strings_and_comments(self, project: Path) -> Set[str]:
        """Analisa strings e comentários em busca de dependências."""
        dependencies = set()

        for py_file in project.rglob("*.py"):
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Procura por padrões em strings
                for pattern, pattern_type in self.string_patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, str) and self._is_valid_external_package(
                            match
                        ):
                            dependencies.add(match)

            except Exception:
                pass

        return dependencies

    def _is_valid_external_package(self, package_name: str) -> bool:
        """Verifica se é um package externo válido."""

        # Lista expandida de pacotes que não devem ser instalados
        forbidden_packages = {
            # Módulos da stdlib (alguns extras que podem não estar na lista principal)
            "builtins",
            "sys",
            "os",
            "path",
            "io",
            "re",
            "json",
            "time",
            "datetime",
            "collections",
            "functools",
            "itertools",
            "typing",
            "pathlib",
            "subprocess",
            "threading",
            "asyncio",
            "unittest",
            "test",
            "tests",
            "logging",
            "uuid",
            "hashlib",
            "base64",
            "urllib",
            "http",
            "email",
            "html",
            "xml",
            "csv",
            "tempfile",
            "shutil",
            "glob",
            "sqlite3",
            "argparse",
            "importlib",
            "inspect",
            "ast",
            "tokenize",
            "dataclasses",
            "enum",
            "abc",
            "contextlib",
            # Projetos FLEXT (todas as variações)
            "flext",
            "flext_core",
            "flext_api",
            "flext_auth",
            "flext_cli",
            "flext_db_oracle",
            "flext_ldap",
            "flext_grpc",
            "flext_web",
            "flext_observability",
            "flext_plugin",
            "flext_quality",
            "flext_meltano",
            "flext_tap_ldap",
            "flext_tap_oracle_oic",
            "flext_tap_oracle_wms",
            "flext_target_ldap",
            "flext_target_oracle",
            "flext_target_oracle_oic",
            "flext_target_oracle_wms",
            "flext_oracle_oic_ext",
            "flext_dbt_ldap",
            "algar_oud_mig",
            "gruponos_meltano_native",
            "flexcore",
            # Pacotes internos comuns
            "src",
            "tests",
            "test",
            "docs",
            "examples",
            "scripts",
            "config",
            "configs",
            "utils",
            "common",
            "shared",
            "internal",
            "core",
            # Palavras que não são packages válidos
            "main",
            "app",
            "application",
            "service",
            "client",
            "server",
            "api",
            "web",
            "cli",
            "gui",
            "ui",
            "db",
            "database",
            "model",
            "models",
            "view",
            "views",
            "controller",
            "controllers",
            "handler",
            "handlers",
            "middleware",
            "auth",
            "authentication",
            "authorization",
            "session",
            "cache",
            "queue",
            "task",
            "tasks",
            "job",
            "jobs",
            "worker",
            "workers",
            # Arquivos/extensões
            "py",
            "txt",
            "md",
            "yml",
            "yaml",
            "json",
            "xml",
            "csv",
            "sql",
            "html",
            "css",
            "js",
            "ts",
            "jsx",
            "tsx",
            "vue",
            "svelte",
            # Palavras muito genéricas
            "data",
            "file",
            "files",
            "directory",
            "dir",
            "folder",
            "path",
            "string",
            "str",
            "int",
            "float",
            "bool",
            "list",
            "dict",
            "set",
            "tuple",
            "none",
            "true",
            "false",
            "null",
            "undefined",
        }

        return (
            package_name
            and isinstance(package_name, str)
            and package_name.strip()  # Não vazio após strip
            and package_name.isidentifier()
            and not package_name.startswith("_")
            and package_name not in self.stdlib_modules
            and package_name.lower() not in forbidden_packages
            and not package_name.startswith("flext")
            and not package_name.startswith("test")
            and not package_name.startswith("src")
            and not package_name.endswith("_test")
            and not package_name.endswith("_tests")
            and len(package_name) > 1
            and len(package_name) < 50  # Pacotes muito longos são suspeitos
            and package_name.islower()
            and not package_name.isdigit()
            and not all(c in "._-" for c in package_name)  # Não só pontuação
            and package_name.count("_") < 5  # Muitos underscores são suspeitos
            and "."
            not in package_name  # Não deve ter pontos (são módulos, não packages)
            and not any(char.isspace() for char in package_name)  # Sem espaços
        )


class VersionTracker:
    """Classe para rastrear mudanças de versão."""

    def __init__(self):
        self.version_changes: List[VersionChange] = []
        self.project_versions: Dict[str, Dict[str, str]] = {}

    def capture_initial_versions(self, project: Path) -> Dict[str, str]:
        """Captura versões iniciais das dependências."""
        versions = {}

        success, output = run_command(
            ["poetry", "show", "--no-ansi"], project, timeout=30
        )
        if success:
            for line in output.split("\n"):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        pkg_name = parts[0]
                        version = parts[1]
                        versions[pkg_name] = version

        self.project_versions[project.name] = versions
        return versions

    def capture_final_versions(self, project: Path) -> Dict[str, str]:
        """Captura versões finais e detecta mudanças."""
        initial_versions = self.project_versions.get(project.name, {})

        final_versions = {}
        success, output = run_command(
            ["poetry", "show", "--no-ansi"], project, timeout=30
        )
        if success:
            for line in output.split("\n"):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        pkg_name = parts[0]
                        version = parts[1]
                        final_versions[pkg_name] = version

        # Detecta mudanças
        self._detect_changes(project.name, initial_versions, final_versions)

        return final_versions

    def _detect_changes(
        self, project_name: str, initial: Dict[str, str], final: Dict[str, str]
    ):
        """Detecta e registra mudanças de versão."""

        # Packages removidos
        for pkg in initial:
            if pkg not in final:
                self.version_changes.append(
                    VersionChange(
                        package=pkg,
                        old_version=initial[pkg],
                        new_version="REMOVED",
                        change_type="remove",
                        reason="Package removido durante sincronização",
                        project=project_name,
                    )
                )

        # Packages adicionados
        for pkg in final:
            if pkg not in initial:
                self.version_changes.append(
                    VersionChange(
                        package=pkg,
                        old_version="NEW",
                        new_version=final[pkg],
                        change_type="install",
                        reason="Package instalado durante descoberta automática",
                        project=project_name,
                    )
                )

        # Packages modificados
        for pkg in initial:
            if pkg in final and initial[pkg] != final[pkg]:
                old_version = initial[pkg]
                new_version = final[pkg]

                # Determina se é upgrade ou downgrade
                change_type = self._compare_versions(old_version, new_version)
                reason = self._determine_change_reason(change_type, pkg)

                self.version_changes.append(
                    VersionChange(
                        package=pkg,
                        old_version=old_version,
                        new_version=new_version,
                        change_type=change_type,
                        reason=reason,
                        project=project_name,
                    )
                )

    def _compare_versions(self, old_version: str, new_version: str) -> str:
        """Compara versões para determinar se é upgrade ou downgrade."""
        try:
            # Simplificado: compara apenas números principais
            old_parts = [int(x) for x in old_version.split(".") if x.isdigit()]
            new_parts = [int(x) for x in new_version.split(".") if x.isdigit()]

            # Iguala tamanhos
            max_len = max(len(old_parts), len(new_parts))
            old_parts.extend([0] * (max_len - len(old_parts)))
            new_parts.extend([0] * (max_len - len(new_parts)))

            if new_parts > old_parts:
                return "upgrade"
            elif new_parts < old_parts:
                return "downgrade"
            else:
                return "change"
        except:
            return "change"

    def _determine_change_reason(self, change_type: str, package: str) -> str:
        """Determina o motivo da mudança."""
        if change_type == "downgrade":
            return f"Downgrade devido a conflito de dependências ou restrições de compatibilidade"
        elif change_type == "upgrade":
            return f"Upgrade para versão mais recente disponível"
        else:
            return f"Mudança de versão para resolver compatibilidade"

    def get_downgrades(self) -> List[VersionChange]:
        """Retorna apenas os downgrades."""
        return [
            change
            for change in self.version_changes
            if change.change_type == "downgrade"
        ]

    def get_changes_by_project(self, project_name: str) -> List[VersionChange]:
        """Retorna mudanças para um projeto específico."""
        return [
            change for change in self.version_changes if change.project == project_name
        ]

    def generate_report(self) -> str:
        """Gera relatório detalhado das mudanças."""
        report = []
        report.append("=" * 80)
        report.append("📊 RELATÓRIO DETALHADO DE MUDANÇAS DE VERSÃO")
        report.append("=" * 80)

        # Estatísticas gerais
        total_changes = len(self.version_changes)
        downgrades = self.get_downgrades()
        upgrades = [c for c in self.version_changes if c.change_type == "upgrade"]
        installs = [c for c in self.version_changes if c.change_type == "install"]

        report.append(f"\n📈 ESTATÍSTICAS GERAIS:")
        report.append(f"  Total de mudanças: {total_changes}")
        report.append(f"  Instalações: {len(installs)}")
        report.append(f"  Upgrades: {len(upgrades)}")
        report.append(f"  Downgrades: {len(downgrades)}")

        # Relatório de downgrades (mais importante)
        if downgrades:
            report.append(f"\n🔻 DOWNGRADES DETECTADOS ({len(downgrades)}):")
            report.append("=" * 50)
            for change in downgrades:
                report.append(f"  📦 {change.package}")
                report.append(f"     Projeto: {change.project}")
                report.append(
                    f"     Versão: {change.old_version} → {change.new_version}"
                )
                report.append(f"     Motivo: {change.reason}")
                report.append("")

        # Relatório por projeto
        projects = set(change.project for change in self.version_changes)
        for project in sorted(projects):
            project_changes = self.get_changes_by_project(project)
            if project_changes:
                report.append(f"\n📁 PROJETO: {project}")
                report.append(f"   Mudanças: {len(project_changes)}")

                for change in project_changes:
                    icon = (
                        "🔻"
                        if change.change_type == "downgrade"
                        else "🆕" if change.change_type == "install" else "🔺"
                    )
                    report.append(
                        f"   {icon} {change.package}: {change.old_version} → {change.new_version}"
                    )

        return "\n".join(report)


# Instâncias globais
version_tracker = VersionTracker()
dependency_analyzer = None


def discover_project_dependencies(
    project: Path, stdlib_modules: Set[str], known_deps: Set[str]
) -> Dict[str, Set[str]]:
    """PILAR CENTRAL: Descobre dependências com análise SUPER ROBUSTA."""
    global dependency_analyzer

    if dependency_analyzer is None:
        dependency_analyzer = DependencyAnalyzer(stdlib_modules)

    print_colored(f"    🔍 DESCOBERTA AUTOMÁTICA SUPER ROBUSTA", Colors.BOLD)

    # Captura versões iniciais
    initial_versions = version_tracker.capture_initial_versions(project)
    print_colored(
        f"    📋 Versões iniciais capturadas: {len(initial_versions)}", Colors.BLUE
    )

    # Análise profunda
    discovered_deps = dependency_analyzer.analyze_deep_dependencies(project)

    # Combina com dependências conhecidas
    final_deps = {"runtime": set(), "test": set(), "typings": set()}

    for category in ["runtime", "test"]:
        if category in discovered_deps:
            final_deps[category].update(discovered_deps[category])

        # Gera typings automaticamente usando APENAS mypy
    if final_deps["runtime"]:
        auto_typings = discover_typings_automatically(project, final_deps["runtime"])
        final_deps["typings"].update(auto_typings)

        if auto_typings:
            print_colored(
                f"      🔤 typings: {len(auto_typings)} gerados automaticamente via mypy",
                Colors.CYAN,
            )

    # Mostra resumo da descoberta
    total_discovered = sum(len(deps) for deps in final_deps.values())
    print_colored(
        f"    ✅ DESCOBERTA COMPLETA: {total_discovered} dependências", Colors.GREEN
    )

    for category, deps in final_deps.items():
        if deps:
            print_colored(f"      📦 {category}: {len(deps)} dependências", Colors.CYAN)

    return final_deps


def sync_project(
    project: Path,
    base_dependencies: Dict[str, List[str]],
    stdlib_modules: Set[str],
    known_deps: Set[str],
) -> Dict[str, int]:
    """Sincroniza dependências com descoberta automática SUPER ROBUSTA."""
    print_colored(f"\n🔄 {project.name}", Colors.BOLD)

    stats = {"success": 0, "failures": 0, "updated": 0, "discovered": 0, "conflicts": 0}

    if not ensure_poetry_lock(project):
        stats["failures"] += 1
        return stats

    # PILAR CENTRAL: Descoberta automática SUPER ROBUSTA
    print_colored(f"    🔍 DESCOBERTA AUTOMÁTICA SUPER ROBUSTA", Colors.BOLD)
    discovered_deps = discover_project_dependencies(project, stdlib_modules, known_deps)

    # Instala dependências descobertas automaticamente
    if any(deps for deps in discovered_deps.values()):
        discovery_stats = install_discovered_dependencies(project, discovered_deps)
        stats["discovered"] = discovery_stats["installed"]
        stats["conflicts"] = discovery_stats["conflicts"]

        if discovery_stats["failures"] > 0:
            stats["failures"] += discovery_stats["failures"]
    else:
        print_colored(
            f"    ➖ Nenhuma dependência descoberta para instalar", Colors.YELLOW
        )

    # Sincroniza dependências base do workspace (complementar)
    print_colored(
        f"    🔗 Sincronizando dependências base do workspace...", Colors.CYAN
    )
    for group, dependencies in base_dependencies.items():
        success, result = sync_project_group(project, group, dependencies)

        if success:
            stats["success"] += 1
            if "atualizados" in result:
                try:
                    count = int(result.split()[0])
                    stats["updated"] += count
                except (ValueError, IndexError):
                    pass
        else:
            stats["failures"] += 1

    # Atualiza poetry.lock final se houve mudanças
    total_changes = stats["updated"] + stats["discovered"]
    if total_changes > 0:
        print(f"    🔐 lock      → ", end="", flush=True)
        success, _ = run_command(["poetry", "lock"], project, timeout=120)

        if success:
            print_colored("✅ atualizado", Colors.GREEN)
        else:
            print_colored("❌ falha", Colors.RED)
            stats["failures"] += 1

    # Captura versões finais e detecta mudanças
    final_versions = version_tracker.capture_final_versions(project)
    project_changes = version_tracker.get_changes_by_project(project.name)

    # Mostra mudanças detectadas
    if project_changes:
        downgrades = [c for c in project_changes if c.change_type == "downgrade"]
        if downgrades:
            print_colored(
                f"    🔻 DOWNGRADES DETECTADOS: {len(downgrades)}", Colors.RED
            )
            for downgrade in downgrades:
                print_colored(
                    f"      📦 {downgrade.package}: {downgrade.old_version} → {downgrade.new_version}",
                    Colors.YELLOW,
                )

    # Resultado do projeto
    if stats["failures"] == 0:
        print_colored(
            f"    ✅ {project.name} → {stats['updated']} sync + {stats['discovered']} descobertos",
            Colors.GREEN,
        )
        if stats["conflicts"] > 0:
            print_colored(
                f"    ⚡ {stats['conflicts']} conflitos resolvidos", Colors.YELLOW
            )
    else:
        print_colored(
            f"    ⚠️  {project.name} → {stats['failures']} falhas", Colors.YELLOW
        )

    return stats


def analyze_and_fix_missing_imports(project: Path) -> Dict[str, Set[str]]:
    """Analisa erros de import e sugere packages para instalar."""
    print_colored(f"    🔍 Analisando erros de import no projeto...", Colors.BLUE)
    
    missing_deps = {"runtime": set(), "test": set()}
    
    # Tenta executar os testes para identificar imports faltantes
    test_dirs = ["tests", "test"]
    for test_dir in test_dirs:
        test_path = project / test_dir
        if test_path.exists():
            # Executa pytest com dry-run para capturar erros de import
            cmd = ["python", "-m", "pytest", "--collect-only", "-q", str(test_path)]
            success, output = run_command(cmd, project, timeout=30)
            
            if not success and "ModuleNotFoundError" in output:
                # Analisa erros de ModuleNotFoundError
                import_error_pattern = re.compile(r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]")
                matches = import_error_pattern.findall(output)
                
                for module in matches:
                    # Converte nome do módulo para package name
                    package_name = module.split(".")[0].replace("_", "-")
                    
                    # Mapeia módulos conhecidos para seus packages
                    module_to_package = {
                        "yaml": "pyyaml",
                        "cv2": "opencv-python",
                        "sklearn": "scikit-learn",
                        "skimage": "scikit-image",
                        "PIL": "pillow",
                        "psycopg2": "psycopg2-binary",
                        "MySQLdb": "mysqlclient",
                        "ldap": "python-ldap",
                        "magic": "python-magic",
                        "dotenv": "python-dotenv",
                        "jose": "python-jose",
                        "multipart": "python-multipart",
                        "slowapi": "slowapi",
                        "bs4": "beautifulsoup4",
                        "lxml": "lxml",
                        "dateutil": "python-dateutil",
                        "tz": "pytz",
                        "crypto": "pycryptodome",
                        "Crypto": "pycryptodome",
                        "git": "gitpython",
                        "github": "pygithub",
                        "gitlab": "python-gitlab",
                        "jira": "jira",
                        "slack": "slack-sdk",
                        "telegram": "python-telegram-bot",
                        "discord": "discord.py",
                        "tweepy": "tweepy",
                        "stripe": "stripe",
                        "paypal": "paypalrestsdk",
                        "braintree": "braintree",
                        "twilio": "twilio",
                        "sendgrid": "sendgrid",
                        "mailgun": "mailgun",
                        "mandrill": "mandrill",
                        "boto": "boto3",
                        "azure": "azure-storage-blob",
                        "google": "google-cloud-storage",
                        "kubernetes": "kubernetes",
                        "docker": "docker",
                        "vagrant": "python-vagrant",
                        "ansible": "ansible",
                        "fabric": "fabric",
                        "paramiko": "paramiko",
                        "pysftp": "pysftp",
                        "ftplib": "ftplib",
                        "smbprotocol": "smbprotocol",
                        "win32com": "pywin32",
                        "pywintypes": "pywin32",
                        "pythoncom": "pywin32",
                        "wmi": "wmi",
                        "ldap3": "ldap3",
                        "saml2": "python-saml",
                        "oauth2": "python-oauth2",
                        "oidc": "python-openid",
                        "jwt": "pyjwt",
                        "passlib": "passlib",
                        "argon2": "argon2-cffi",
                        "bcrypt": "bcrypt",
                        "scrypt": "scrypt",
                    }
                    
                    if module in module_to_package:
                        package_name = module_to_package[module]
                    
                    if is_valid_pypi_package(package_name):
                        missing_deps["test"].add(package_name)
                        print_colored(
                            f"      📦 Detectado import faltante: {module} → {package_name}",
                            Colors.YELLOW
                        )
    
    # Analisa código runtime para imports faltantes
    src_dirs = ["src", "app", "."]
    for src_dir in src_dirs[:1]:  # Analisa apenas o primeiro diretório encontrado
        src_path = project / src_dir
        if src_path.exists() and src_path.is_dir():
            # Tenta executar um import check básico
            py_files = list(src_path.rglob("*.py"))[:10]  # Limita a 10 arquivos para não demorar muito
            
            for py_file in py_files:
                cmd = ["python", "-c", f"import ast; ast.parse(open('{py_file}').read())"]
                success, output = run_command(cmd, project, timeout=5)
                
                if not success and "ModuleNotFoundError" in output:
                    import_error_pattern = re.compile(r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]")
                    matches = import_error_pattern.findall(output)
                    
                    for module in matches:
                        package_name = module.split(".")[0].replace("_", "-")
                        if is_valid_pypi_package(package_name):
                            missing_deps["runtime"].add(package_name)
    
    return missing_deps


def install_discovered_dependencies(
    project: Path, discovered_deps: Dict[str, Set[str]]
) -> Dict[str, int]:
    """Instala dependências descobertas automaticamente."""
    stats = {"installed": 0, "skipped": 0, "conflicts": 0, "failures": 0}

    # Mapeia categorias para grupos Poetry
    category_groups = {
        "runtime": "main",  # Dependências principais (sem --group)
        "test": "test",
        "typings": "typings",
    }

    # Obtém lista de pacotes já instalados
    installed_packages = get_installed_packages(project)
    print_colored(
        f"    📋 Pacotes já instalados: {len(installed_packages)}", Colors.BLUE
    )
    
    # Analisa e adiciona dependências de imports faltantes
    missing_import_deps = analyze_and_fix_missing_imports(project)
    for category, deps in missing_import_deps.items():
        if category in discovered_deps:
            discovered_deps[category].update(deps)
        else:
            discovered_deps[category] = deps

    for category, packages in discovered_deps.items():
        if not packages:
            continue

        group = category_groups.get(category, category)
        print_colored(
            f"    📦 Processando {category} dependencies descobertas...", Colors.MAGENTA
        )

        # VALIDAÇÃO FINAL: Remove packages inválidos e já instalados
        valid_packages = set()
        already_installed = set()

        for package in packages:
            if not is_valid_pypi_package(package):
                stats["skipped"] += 1
                continue

            # Verifica se já está instalado
            if package in installed_packages:
                already_installed.add(package)
                stats["skipped"] += 1
                continue

            valid_packages.add(package)

        # Mostra estatísticas
        if already_installed:
            print_colored(
                f"      ✅ {len(already_installed)} packages já instalados (pulados)",
                Colors.GREEN,
            )

        if not valid_packages:
            print_colored(
                f"      ➖ Nenhum package novo para instalar em {category}",
                Colors.YELLOW,
            )
            continue

        print_colored(
            f"      📦 {len(valid_packages)} packages novos para instalar", Colors.CYAN
        )

        # ESTRATÉGIAS DE VERSÃO INTELIGENTES
        packages_to_install = []
        problematic_packages = {
            # Packages que frequentemente causam conflitos
            "lato": "1.0.0",  # Versão específica que funciona
            "tenacity": "8.2.0",
            "grpcio": "1.56.0",
            "protobuf": "4.21.0",
            "uvicorn": "0.23.0",
            "fastapi": "0.100.0",
            "sqlalchemy": "2.0.0",
            "pydantic": "2.0.0",
        }

        for package in sorted(valid_packages):
            if package.lower() in problematic_packages:
                version = problematic_packages[package.lower()]
                packages_to_install.append(f"{package}@{version}")
                print_colored(
                    f"      🔧 {package}@{version} (versão controlada)", Colors.YELLOW
                )
            else:
                packages_to_install.append(f"{package}")
                # Não mostra cada package individual para reduzir verbosidade

        if packages_to_install:
            # Constrói comando apropriado
            if group == "main":
                cmd = ["poetry", "add"] + packages_to_install
            else:
                cmd = ["poetry", "add"] + packages_to_install + ["--group", group]

            print_colored(
                f"      🔄 Instalando {len(packages_to_install)} packages {category}...",
                Colors.BLUE,
            )

            success, output = run_command(cmd, project, timeout=600)

            if success:
                # Conta instalações reais
                installed_count = output.lower().count(
                    "installing"
                ) + output.lower().count("updating")
                stats["installed"] += installed_count
                print_colored(
                    f"        ✅ {installed_count} packages descobertos instalados",
                    Colors.GREEN,
                )

                # Detecta possíveis conflitos resolvidos
                if "downgrading" in output.lower() or "upgrading" in output.lower():
                    stats["conflicts"] += 1
                    print_colored(
                        f"        ⚡ Conflitos de versão resolvidos automaticamente",
                        Colors.YELLOW,
                    )

            else:
                stats["failures"] += 1
                print_colored(f"        ❌ Falha na instalação em lote", Colors.RED)

                # Tenta instalar packages individualmente (estratégia de fallback)
                print_colored(
                    f"        🔄 Tentando instalação individual dos packages descobertos...",
                    Colors.YELLOW,
                )

                for pkg_spec in packages_to_install:
                    package_name = pkg_spec.split("@")[0]
                    if group == "main":
                        individual_cmd = ["poetry", "add", package_name]
                    else:
                        individual_cmd = [
                            "poetry",
                            "add",
                            package_name,
                            "--group",
                            group,
                        ]

                    success, _ = run_command(individual_cmd, project, timeout=60)
                    if success:
                        stats["installed"] += 1
                        print_colored(f"          ✅ {package_name}", Colors.GREEN)
                    else:
                        print_colored(f"          ❌ {package_name}", Colors.RED)

        else:
            print_colored(
                f"      ➖ Nenhum package descoberto para instalar", Colors.YELLOW
            )

    return stats


class PackageVersionAnalyzer:
    """Analisa versões de packages e identifica problemas."""
    
    def __init__(self):
        self.package_versions = {}  # {package: {project: version}}
        self.latest_versions = {}   # {package: latest_version}
        self.version_constraints = {}  # {package: {project: parsed_constraint}}
        
    def parse_version_constraint(self, constraint: str) -> Dict[str, str]:
        """Parse version constraints como ^1.2.3, >=1.0.0, etc."""
        import re
        
        constraint = constraint.strip()
        
        # Patterns para diferentes tipos de constraints
        patterns = {
            'caret': r'^\^(.+)$',         # ^1.2.3
            'tilde': r'^~(.+)$',          # ~1.2.3
            'gte': r'^>=(.+)$',           # >=1.2.3
            'gt': r'^>(.+)$',             # >1.2.3
            'lte': r'^<=(.+)$',           # <=1.2.3
            'lt': r'^<(.+)$',             # <1.2.3
            'exact': r'^==(.+)$',         # ==1.2.3
            'compatible': r'^~=(.+)$',    # ~=1.2.3
            'wildcard': r'^\*$',          # *
            'range': r'^(.+),(.+)$',      # >=1.0,<2.0
        }
        
        for constraint_type, pattern in patterns.items():
            match = re.match(pattern, constraint)
            if match:
                if constraint_type == 'range':
                    return {
                        'type': 'range',
                        'min': match.group(1),
                        'max': match.group(2)
                    }
                elif constraint_type == 'wildcard':
                    return {'type': 'wildcard', 'version': '*'}
                else:
                    return {
                        'type': constraint_type,
                        'version': match.group(1)
                    }
        
        # Se não matchou nenhum pattern, assume versão exata
        return {'type': 'exact', 'version': constraint}
    
    def get_latest_available_version(self, package: str) -> Optional[str]:
        """Obtém a versão mais recente disponível no PyPI."""
        try:
            import urllib.request
            import json
            
            url = f"https://pypi.org/pypi/{package}/json"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read())
                return data.get("info", {}).get("version")
        except:
            return None
    
    def analyze_version_pinning(self, projects: List[Path]) -> Dict[str, Any]:
        """Analisa quem está segurando atualizações."""
        print_colored("\n🔍 Analisando version pinning e atualizações bloqueadas...", Colors.BLUE)
        
        # Coleta todas as versões
        for project in projects:
            pyproject_file = project / "pyproject.toml"
            if not pyproject_file.exists():
                continue
                
            try:
                with open(pyproject_file, "rb") as f:
                    data = tomllib.load(f)
                
                # Analisa todas as dependências
                all_deps = {}
                
                # Dependências principais
                poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
                all_deps.update(poetry_deps)
                
                # Dependências de grupos
                groups = data.get("tool", {}).get("poetry", {}).get("group", {})
                for group_data in groups.values():
                    group_deps = group_data.get("dependencies", {})
                    all_deps.update(group_deps)
                
                # Registra versões e constraints
                for package, version_spec in all_deps.items():
                    if package == "python":
                        continue
                        
                    if package not in self.package_versions:
                        self.package_versions[package] = {}
                        self.version_constraints[package] = {}
                    
                    # Normaliza versão
                    if isinstance(version_spec, dict):
                        version = version_spec.get("version", "*")
                    else:
                        version = str(version_spec)
                    
                    self.package_versions[package][project.name] = version
                    self.version_constraints[package][project.name] = self.parse_version_constraint(version)
                    
            except Exception:
                continue
        
        # Analisa pinning problems
        pinning_issues = {}
        
        for package, project_versions in self.package_versions.items():
            # Pega versão mais recente do PyPI
            if package not in self.latest_versions:
                latest = self.get_latest_available_version(package)
                if latest:
                    self.latest_versions[package] = latest
            
            # Identifica projetos com versões muito restritivas
            restrictive_projects = []
            
            for project, version in project_versions.items():
                constraint = self.version_constraints[package][project]
                
                # Considera restritivo se usa exact version (==) ou caret muito específico
                if constraint['type'] in ['exact', 'caret']:
                    restrictive_projects.append({
                        'project': project,
                        'version': version,
                        'constraint_type': constraint['type']
                    })
            
            if restrictive_projects and len(set(v['version'] for v in restrictive_projects)) > 1:
                pinning_issues[package] = {
                    'projects': restrictive_projects,
                    'latest_available': self.latest_versions.get(package, 'Unknown')
                }
        
        return pinning_issues
    
    def suggest_version_standardization(self) -> Dict[str, str]:
        """Sugere versões padronizadas para cada package."""
        suggestions = {}
        
        for package, project_versions in self.package_versions.items():
            versions = list(project_versions.values())
            
            # Se todos usam a mesma versão, mantém
            if len(set(versions)) == 1:
                suggestions[package] = versions[0]
                continue
            
            # Analisa constraints para sugerir a melhor versão
            constraints = self.version_constraints.get(package, {})
            
            # Prioriza versões com >= sobre ^
            gte_versions = []
            caret_versions = []
            exact_versions = []
            
            for project, constraint in constraints.items():
                version = project_versions[project]
                if constraint['type'] == 'gte':
                    gte_versions.append(version)
                elif constraint['type'] == 'caret':
                    caret_versions.append(version)
                elif constraint['type'] == 'exact':
                    exact_versions.append(version)
            
            # Sugere a versão mais flexível possível
            if gte_versions:
                # Pega a versão mínima dos >=
                suggestions[package] = min(gte_versions)
            elif caret_versions:
                # Pega a versão mais recente dos ^
                suggestions[package] = max(caret_versions)
            else:
                # Pega a versão mais comum
                from collections import Counter
                version_counts = Counter(versions)
                suggestions[package] = version_counts.most_common(1)[0][0]
        
        return suggestions


def check_version_compatibility_across_projects(projects: List[Path]) -> Tuple[Dict[str, List[str]], PackageVersionAnalyzer]:
    """Verifica conflitos de versão entre projetos do workspace."""
    analyzer = PackageVersionAnalyzer()
    
    print_colored("\n🔍 Verificando compatibilidade de versões entre projetos...", Colors.BLUE)
    
    # Analisa version pinning
    pinning_issues = analyzer.analyze_version_pinning(projects)
    
    # Coleta todas as versões de cada package em cada projeto
    package_versions = {}  # {package: {project: version}}
    
    for project in projects:
        pyproject_file = project / "pyproject.toml"
        if not pyproject_file.exists():
            continue
            
        try:
            with open(pyproject_file, "rb") as f:
                data = tomllib.load(f)
            
            # Analisa todas as dependências
            all_deps = {}
            
            # Dependências principais
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            all_deps.update(poetry_deps)
            
            # Dependências de grupos
            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_data in groups.values():
                group_deps = group_data.get("dependencies", {})
                all_deps.update(group_deps)
            
            # Registra versões
            for package, version_spec in all_deps.items():
                if package == "python":
                    continue
                    
                if package not in package_versions:
                    package_versions[package] = {}
                
                # Normaliza versão
                if isinstance(version_spec, dict):
                    version = version_spec.get("version", "*")
                else:
                    version = str(version_spec)
                
                package_versions[package][project.name] = version
                
        except Exception:
            continue
    
    # Identifica conflitos usando o analyzer
    conflicts = {}
    
    for package, project_versions in analyzer.package_versions.items():
        unique_versions = set(project_versions.values())
        
        # Se há mais de uma versão diferente, é um conflito potencial
        if len(unique_versions) > 1:
            conflicts[package] = []
            for project, version in project_versions.items():
                conflicts[package].append(f"{project}: {version}")
    
    # Mostra conflitos encontrados
    if conflicts:
        print_colored(f"\n⚠️  Conflitos de versão detectados:", Colors.YELLOW)
        for package, versions in sorted(conflicts.items()):
            print_colored(f"  📦 {package}:", Colors.RED)
            for version_info in versions:
                print_colored(f"    - {version_info}", Colors.YELLOW)
    else:
        print_colored("✅ Nenhum conflito de versão detectado!", Colors.GREEN)
    
    # Mostra quem está segurando atualizações
    if pinning_issues:
        print_colored(f"\n🔒 Projetos segurando atualizações:", Colors.YELLOW)
        for package, info in sorted(pinning_issues.items()):
            print_colored(f"  📦 {package} (última versão: {info['latest_available']})", Colors.CYAN)
            for proj_info in info['projects']:
                print_colored(
                    f"    - {proj_info['project']}: {proj_info['version']} "
                    f"({proj_info['constraint_type']})",
                    Colors.YELLOW
                )
    
    return conflicts, analyzer


def apply_version_standardization(projects: List[Path], suggestions: Dict[str, str], analyzer: PackageVersionAnalyzer) -> int:
    """Aplica as sugestões de padronização nos pyproject.toml."""
    print_colored("\n🔧 APLICANDO PADRONIZAÇÃO DE VERSÕES", Colors.BOLD)
    
    changes_applied = 0
    
    for project in projects:
        pyproject_file = project / "pyproject.toml"
        if not pyproject_file.exists():
            continue
        
        project_changes = 0
        
        try:
            # Lê o arquivo
            with open(pyproject_file, "rb") as f:
                data = tomllib.load(f)
            
            # Backup do arquivo original
            import shutil
            backup_file = pyproject_file.with_suffix(".toml.bak")
            shutil.copy2(pyproject_file, backup_file)
            
            # Atualiza versões
            changed = False
            
            # Dependências principais
            if "tool" in data and "poetry" in data["tool"] and "dependencies" in data["tool"]["poetry"]:
                for package, version_spec in data["tool"]["poetry"]["dependencies"].items():
                    if package in suggestions and package != "python":
                        current_version = version_spec
                        if isinstance(version_spec, dict):
                            current_version = version_spec.get("version", "*")
                        
                        suggested = suggestions[package]
                        if str(current_version) != suggested:
                            if isinstance(version_spec, dict):
                                data["tool"]["poetry"]["dependencies"][package]["version"] = suggested
                            else:
                                data["tool"]["poetry"]["dependencies"][package] = suggested
                            changed = True
                            project_changes += 1
                            print_colored(
                                f"  {project.name}: {package} {current_version} → {suggested}",
                                Colors.GREEN
                            )
            
            # Dependências de grupos
            if "tool" in data and "poetry" in data["tool"] and "group" in data["tool"]["poetry"]:
                for group_name, group_data in data["tool"]["poetry"]["group"].items():
                    if "dependencies" in group_data:
                        for package, version_spec in group_data["dependencies"].items():
                            if package in suggestions:
                                current_version = version_spec
                                if isinstance(version_spec, dict):
                                    current_version = version_spec.get("version", "*")
                                
                                suggested = suggestions[package]
                                if str(current_version) != suggested:
                                    if isinstance(version_spec, dict):
                                        data["tool"]["poetry"]["group"][group_name]["dependencies"][package]["version"] = suggested
                                    else:
                                        data["tool"]["poetry"]["group"][group_name]["dependencies"][package] = suggested
                                    changed = True
                                    project_changes += 1
                                    print_colored(
                                        f"  {project.name} ({group_name}): {package} {current_version} → {suggested}",
                                        Colors.GREEN
                                    )
            
            # Salva o arquivo se houve mudanças
            if changed:
                import tomlkit
                
                # Recarrega com tomlkit para preservar formatação
                with open(pyproject_file, "r") as f:
                    doc = tomlkit.load(f)
                
                # Aplica mudanças no documento tomlkit
                if "dependencies" in doc.get("tool", {}).get("poetry", {}):
                    for package in doc["tool"]["poetry"]["dependencies"]:
                        if package in suggestions and package != "python":
                            doc["tool"]["poetry"]["dependencies"][package] = suggestions[package]
                
                if "group" in doc.get("tool", {}).get("poetry", {}):
                    for group_name in doc["tool"]["poetry"]["group"]:
                        if "dependencies" in doc["tool"]["poetry"]["group"][group_name]:
                            for package in doc["tool"]["poetry"]["group"][group_name]["dependencies"]:
                                if package in suggestions:
                                    doc["tool"]["poetry"]["group"][group_name]["dependencies"][package] = suggestions[package]
                
                # Salva com formatação preservada
                with open(pyproject_file, "w") as f:
                    f.write(tomlkit.dumps(doc))
                
                changes_applied += project_changes
                print_colored(
                    f"  ✅ {project.name}: {project_changes} mudanças aplicadas",
                    Colors.GREEN
                )
            
        except Exception as e:
            print_colored(
                f"  ❌ {project.name}: Erro ao aplicar mudanças - {str(e)}",
                Colors.RED
            )
            # Restaura backup em caso de erro
            if backup_file.exists():
                shutil.copy2(backup_file, pyproject_file)
    
    return changes_applied


def main() -> None:
    """Função principal com descoberta automática SUPER ROBUSTA."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FLEXT Dependencies Sync - Descoberta e padronização automática de dependências"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as sugestões de padronização automaticamente"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o que seria feito sem aplicar mudanças"
    )
    parser.add_argument(
        "--projects",
        nargs="+",
        help="Lista específica de projetos para processar"
    )
    
    args = parser.parse_args()
    
    print_colored("=" * 60, Colors.CYAN)
    print_colored("🚀 FLEXT Dependencies Sync - DESCOBERTA SUPER ROBUSTA", Colors.BOLD)
    print_colored("=" * 60, Colors.CYAN)

    # Descobre módulos da stdlib dinamicamente
    stdlib_modules = get_stdlib_modules()
    print_colored(
        f"📚 Descobertos {len(stdlib_modules)} módulos da stdlib", Colors.BLUE
    )

    # Extrai dependências essenciais base
    print_colored("\n📖 Lendo pyproject.toml da raiz...", Colors.BLUE)
    base_dependencies = extract_essential_dependencies()

    if not base_dependencies:
        print_colored("❌ Nenhuma dependência encontrada!", Colors.RED)
        sys.exit(1)

    # Encontra projetos
    print_colored("\n🔍 Encontrando projetos Python...", Colors.BLUE)
    projects = find_flext_projects()

    if not projects:
        print_colored("❌ Nenhum projeto encontrado!", Colors.RED)
        sys.exit(1)

    print_colored(f"📁 Encontrados {len(projects)} projetos", Colors.GREEN)

    # PILAR CENTRAL: Descobre dependências existentes para base de conhecimento
    print_colored("\n🧠 CONSTRUINDO BASE DE CONHECIMENTO AUTOMÁTICA", Colors.BOLD)
    existing_deps = discover_existing_dependencies(projects)
    all_known_deps = set()
    for deps in existing_deps.values():
        all_known_deps.update(deps)

    print_colored(
        f"🔍 Base de conhecimento automática: {len(all_known_deps)} dependências",
        Colors.CYAN,
    )
    
    # Verifica compatibilidade de versões entre projetos
    version_conflicts, version_analyzer = check_version_compatibility_across_projects(projects)

    # Estatísticas
    global_stats = {
        "total_projects": len(projects),
        "success_projects": 0,
        "total_updated": 0,
        "total_discovered": 0,
        "total_conflicts": 0,
        "total_failures": 0,
        "version_conflicts": len(version_conflicts),
    }

    # Processa projetos com descoberta automática SUPER ROBUSTA
    print_colored(f"\n🔄 PROCESSANDO COM DESCOBERTA SUPER ROBUSTA", Colors.BOLD)
    print_colored(f"Projetos: {len(projects)} | Descoberta: SUPER ATIVA", Colors.CYAN)
    start_time = time.time()

    for i, project in enumerate(projects, 1):
        print_colored(f"\n[{i:>2}/{len(projects)}] {project.name}", Colors.CYAN)

        try:
            stats = sync_project(
                project, base_dependencies, stdlib_modules, all_known_deps
            )

            if stats["failures"] == 0:
                global_stats["success_projects"] += 1

            global_stats["total_updated"] += stats["updated"]
            global_stats["total_discovered"] += stats["discovered"]
            global_stats["total_conflicts"] += stats["conflicts"]
            global_stats["total_failures"] += stats["failures"]

        except KeyboardInterrupt:
            print_colored("\n❌ Interrompido pelo usuário", Colors.RED)
            break
        except Exception as e:
            print_colored(f"❌ Erro em {project.name}: {str(e)}", Colors.RED)
            global_stats["total_failures"] += 1

    # Relatório final
    total_time = time.time() - start_time

    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored("📊 RELATÓRIO FINAL - DESCOBERTA SUPER ROBUSTA", Colors.BOLD)
    print_colored("=" * 60, Colors.CYAN)

    print_colored(f"⏱️  Tempo total: {total_time:.1f}s", Colors.BLUE)
    print_colored(
        f"📁 Projetos: {global_stats['success_projects']}/{global_stats['total_projects']} sucessos",
        Colors.GREEN,
    )
    print_colored(f"📦 Sincronizações: {global_stats['total_updated']}", Colors.GREEN)
    print_colored(
        f"🔍 DESCOBERTAS AUTOMÁTICAS: {global_stats['total_discovered']} dependências",
        Colors.BOLD,
    )

    if global_stats["total_conflicts"] > 0:
        print_colored(
            f"⚡ Conflitos resolvidos automaticamente: {global_stats['total_conflicts']}",
            Colors.YELLOW,
        )
    
    if global_stats["version_conflicts"] > 0:
        print_colored(
            f"⚠️  Conflitos de versão entre projetos: {global_stats['version_conflicts']}",
            Colors.YELLOW,
        )

    if global_stats["total_failures"] > 0:
        print_colored(f"❌ Falhas: {global_stats['total_failures']}", Colors.RED)

    # RELATÓRIO DETALHADO DE MUDANÇAS DE VERSÃO
    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored("📋 RELATÓRIO DETALHADO DE MUDANÇAS DE VERSÃO", Colors.BOLD)
    print_colored("=" * 60, Colors.CYAN)

    detailed_report = version_tracker.generate_report()
    print(detailed_report)

    # Salva relatório em arquivo
    report_file = Path("version_changes_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(detailed_report)

    print_colored(f"\n💾 Relatório salvo em: {report_file}", Colors.CYAN)
    
    # NOVO: Relatório de sugestões de padronização
    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored("🎯 SUGESTÕES DE PADRONIZAÇÃO DE VERSÕES", Colors.BOLD)
    print_colored("=" * 60, Colors.CYAN)
    
    version_suggestions = version_analyzer.suggest_version_standardization()
    
    # Agrupa por tipo de mudança sugerida
    suggestions_by_type = {
        'conflicts': [],
        'updates': [],
        'standardize': []
    }
    
    for package, suggested_version in version_suggestions.items():
        current_versions = version_analyzer.package_versions.get(package, {})
        unique_versions = set(current_versions.values())
        
        if len(unique_versions) > 1:
            # Conflito de versão
            suggestions_by_type['conflicts'].append({
                'package': package,
                'suggested': suggested_version,
                'current': current_versions,
                'latest': version_analyzer.latest_versions.get(package)
            })
        elif package in version_analyzer.latest_versions:
            latest = version_analyzer.latest_versions[package]
            current = list(unique_versions)[0] if unique_versions else None
            
            if current and current != latest and suggested_version != current:
                # Atualização disponível
                suggestions_by_type['updates'].append({
                    'package': package,
                    'current': current,
                    'latest': latest,
                    'suggested': suggested_version
                })
    
    # Mostra sugestões de conflitos
    if suggestions_by_type['conflicts']:
        print_colored("\n📦 CONFLITOS A RESOLVER:", Colors.RED)
        for item in suggestions_by_type['conflicts']:
            print_colored(f"\n  {item['package']}:", Colors.YELLOW)
            print_colored(f"    Sugestão: {item['suggested']}", Colors.GREEN)
            if item['latest']:
                print_colored(f"    Última versão disponível: {item['latest']}", Colors.CYAN)
            print_colored("    Versões atuais:", Colors.YELLOW)
            for proj, ver in sorted(item['current'].items()):
                print_colored(f"      - {proj}: {ver}", Colors.WHITE)
    
    # Mostra packages desatualizados
    if suggestions_by_type['updates']:
        print_colored("\n📈 ATUALIZAÇÕES DISPONÍVEIS:", Colors.CYAN)
        for item in sorted(suggestions_by_type['updates'], key=lambda x: x['package']):
            print_colored(
                f"  {item['package']}: {item['current']} → {item['latest']}", 
                Colors.YELLOW
            )
    
    # NOVO: Identifica projetos que mais seguram atualizações
    print_colored("\n" + "=" * 60, Colors.CYAN)
    print_colored("🚧 PROJETOS QUE MAIS SEGURAM ATUALIZAÇÕES", Colors.BOLD)
    print_colored("=" * 60, Colors.CYAN)
    
    project_restrictions = {}
    for package, constraints in version_analyzer.version_constraints.items():
        for project, constraint in constraints.items():
            if constraint['type'] in ['exact', 'caret']:
                if project not in project_restrictions:
                    project_restrictions[project] = 0
                project_restrictions[project] += 1
    
    # Ordena projetos por número de restrições
    sorted_restrictions = sorted(
        project_restrictions.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    if sorted_restrictions:
        for project, count in sorted_restrictions[:10]:  # Top 10
            print_colored(
                f"  {project}: {count} packages com versões restritivas", 
                Colors.YELLOW
            )
    else:
        print_colored("  ✅ Nenhum projeto com versões excessivamente restritivas!", Colors.GREEN)

    # Status final
    downgrades = version_tracker.get_downgrades()
    if downgrades:
        print_colored(
            f"\n🔻 ATENÇÃO: {len(downgrades)} DOWNGRADES DETECTADOS!", Colors.RED
        )
        print_colored(
            "   Verifique o relatório detalhado para mais informações.", Colors.YELLOW
        )

    if global_stats["total_failures"] == 0:
        print_colored(
            "\n🎉 DESCOBERTA SUPER ROBUSTA CONCLUÍDA COM SUCESSO!", Colors.GREEN
        )
        print_colored(
            "✨ Todas as dependências foram descobertas e sincronizadas com análise profunda",
            Colors.GREEN,
        )
    else:
        print_colored(
            f"\n⚠️  DESCOBERTA SUPER ROBUSTA CONCLUÍDA COM {global_stats['total_failures']} FALHAS",
            Colors.YELLOW,
        )
        print_colored(
            "🔄 Execute novamente para tentar resolver falhas restantes", Colors.CYAN
        )

    print_colored("=" * 60, Colors.CYAN)


if __name__ == "__main__":
    main()
