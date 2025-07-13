#!/usr/bin/env python3
"""
Script SIMPLES para descobrir e adicionar dependências faltantes.
Foca em FUNCIONAR, não em ser perfeito.
"""

import ast
import re
import subprocess
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any


def find_python_files(project: Path) -> list[Path]:
    """Encontra todos os arquivos Python no projeto."""
    return list(project.rglob("*.py"))


def extract_imports(file_path: Path) -> set[str]:
    """Extrai todos os imports de um arquivo Python."""
    imports: set[str] = set()

    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])

    except Exception as e:
        print(f"⚠️  Erro ao analisar {file_path}: {e}")

    return imports


def get_stdlib_modules() -> set[str]:
    """Lista básica de módulos da stdlib Python."""
    # Lista conservadora dos mais comuns
    return {
        "abc",
        "argparse",
        "ast",
        "asyncio",
        "base64",
        "collections",
        "contextlib",
        "copy",
        "csv",
        "dataclasses",
        "datetime",
        "decimal",
        "email",
        "enum",
        "functools",
        "glob",
        "hashlib",
        "html",
        "http",
        "importlib",
        "inspect",
        "io",
        "itertools",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "pickle",
        "platform",
        "pprint",
        "queue",
        "re",
        "shutil",
        "socket",
        "sqlite3",
        "string",
        "subprocess",
        "sys",
        "tempfile",
        "threading",
        "time",
        "typing",
        "unittest",
        "urllib",
        "uuid",
        "warnings",
        "xml",
        "zipfile",
        # Builtins e especiais
        "builtins",
        "gc",
        "signal",
        "traceback",
        "weakref",
        "__future__",
        "types",
        "operator",
        "random",
        "secrets",
        "statistics",
        # Mais stdlib
        "fnmatch",
        "getpass",
        "ipaddress",
        "struct",
        "array",
        "bisect",
        "calendar",
        "cmath",
        "codecs",
        "configparser",
        "difflib",
        "filecmp",
        "fileinput",
        "fractions",
        "gzip",
        "heapq",
        "hmac",
    }


def get_project_dependencies(project: Path) -> set[str]:
    """Lê dependências já declaradas no pyproject.toml."""
    pyproject_path = project / "pyproject.toml"

    if not pyproject_path.exists():
        return set()

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        deps = set()

        # Dependências principais
        poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        deps.update(poetry_deps.keys())

        # Dependências de grupos
        groups = data.get("tool", {}).get("poetry", {}).get("group", {})
        for group_data in groups.values():
            group_deps = group_data.get("dependencies", {})
            deps.update(group_deps.keys())

        # Remove python e outros meta-packages
        deps.discard("python")

        # Normaliza nomes (pydantic-settings -> pydantic_settings)
        normalized = set()
        for dep in deps:
            normalized.add(dep)
            normalized.add(dep.replace("-", "_"))
            normalized.add(dep.replace("_", "-"))

        return normalized

    except Exception as e:
        print(f"⚠️  Erro ao ler pyproject.toml: {e}")
        return set()


def check_import_exists(module: str) -> bool:
    """Verifica se um módulo pode ser importado."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            check=False,
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except:
        return False


def discover_missing_imports(project: Path) -> set[str]:
    """Descobre imports que não estão no pyproject.toml."""
    print(f"\n📁 Analisando projeto: {project.name}")

    # 1. Encontra todos os imports
    all_imports = set()
    py_files = find_python_files(project)

    print(f"   📄 Analisando {len(py_files)} arquivos Python...")

    for py_file in py_files:
        # Pula arquivos de teste e setup
        if any(
            part in py_file.parts
            for part in ["tests", "test", "setup.py", "__pycache__"]
        ):
            continue

        imports = extract_imports(py_file)
        all_imports.update(imports)

    # 2. Remove stdlib
    stdlib = get_stdlib_modules()
    third_party = all_imports - stdlib

    # 3. Remove já declarados
    declared = get_project_dependencies(project)
    missing = third_party - declared

    # 4. Remove imports internos do projeto e workspace
    project_name = project.name.replace("-", "_")
    missing.discard(project_name)

    # Remove outros projetos FLEXT
    flext_projects = {
        "flext",
        "flext_core",
        "flext_auth",
        "flext_cli",
        "flext_api",
        "flext_grpc",
        "flext_web",
        "flext_plugin",
        "flext_meltano",
        "flext_observability",
        "flext_ldap",
        "flext_quality",
        "flext_db_oracle",
        "flext_tap_ldap",
        "flext_tap_oracle_oic",
        "flext_tap_oracle_wms",
        "flext_target_ldap",
        "flext_target_oracle",
        "flext_target_oracle_oic",
        "flext_target_oracle_wms",
        "flext_dbt_ldap",
        "flext_oracle_oic_ext",
    }
    missing -= flext_projects

    # Remove falsos positivos comuns
    false_positives = {
        "src",
        "tests",
        "test",
        "setup",
        "__main__",
        "models",
        "views",
        "urls",
        "admin",
        "apps",
        "forms",  # Django apps comuns
        "config",
        "settings",
        "utils",
        "helpers",
        "constants",  # Módulos internos comuns
        "serializers",
        "migrations",
        "management",
        "commands",  # Django específico
        "core",
        "domain",
        "infrastructure",
        "application",  # DDD/Clean Architecture
        "services",
        "repositories",
        "entities",
        "schemas",  # Padrões arquiteturais
    }
    missing -= false_positives

    if missing:
        print(f"   ❌ Encontrados {len(missing)} imports não declarados:")
        for imp in sorted(missing):
            print(f"      - {imp}")
    else:
        print("   ✅ Todos os imports estão declarados!")

    return missing


def parse_version_constraint(constraint: str) -> dict[str, str]:
    """Analisa constraint de versão e retorna tipo e versão."""
    constraint = constraint.strip()

    # Padrões comuns
    patterns = [
        (r"^==(.+)$", "exact"),  # ==1.2.3
        (r"^~=(.+)$", "compatible"),  # ~=1.2.3
        (r"^>=(.+),<(.+)$", "range"),  # >=1.0,<2.0
        (r"^>=(.+)$", "minimum"),  # >=1.0
        (r"^\^(.+)$", "caret"),  # ^1.2.3 (Poetry)
        (r"^~(.+)$", "tilde"),  # ~1.2.3 (Poetry)
    ]

    for pattern, constraint_type in patterns:
        match = re.match(pattern, constraint)
        if match:
            return {
                "type": constraint_type,
                "version": match.group(1),
                "raw": constraint,
            }

    return {"type": "unknown", "version": constraint, "raw": constraint}


def get_package_versions_in_workspace(
    workspace_root: Path, package: str
) -> dict[str, str]:
    """Coleta todas as versões de um pacote no workspace."""
    versions = {}

    for pyproject in workspace_root.rglob("pyproject.toml"):
        # Pula backups e diretórios temporários
        if any(
            part in pyproject.parts
            for part in [".venv", "backup", "tmp", "__pycache__"]
        ):
            continue

        try:
            with open(pyproject, "rb") as f:
                data = tomllib.load(f)

            project_name = pyproject.parent.name

            # Procura em dependencies
            deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            if package in deps:
                versions[project_name] = str(deps[package])

            # Procura em grupos
            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_name, group_data in groups.items():
                group_deps = group_data.get("dependencies", {})
                if package in group_deps:
                    versions[f"{project_name}[{group_name}]"] = str(group_deps[package])

        except Exception:
            continue

    return versions


def analyze_version_restrictions(versions: dict[str, str]) -> dict[str, list[str]]:
    """Analisa restrições de versão e identifica projetos restritivos."""
    analysis: dict[str, list[str]] = {
        "exact_pins": [],  # Projetos com versão exata (==)
        "upper_bounds": [],  # Projetos com limite superior
        "restrictive": [],  # Projetos mais restritivos
        "flexible": [],  # Projetos mais flexíveis
    }

    for project, version in versions.items():
        parsed = parse_version_constraint(version)

        if parsed["type"] == "exact":
            analysis["exact_pins"].append(f"{project}: {version}")
            analysis["restrictive"].append(project)
        elif parsed["type"] in {"range", "compatible"}:
            analysis["upper_bounds"].append(f"{project}: {version}")
            analysis["restrictive"].append(project)
        elif parsed["type"] in {"minimum", "caret", "tilde"}:
            analysis["flexible"].append(f"{project}: {version}")

    return analysis


def add_dependency(project: Path, package: str, dry_run: bool = True) -> bool:
    """Adiciona dependência usando poetry."""
    # Mapeamento de nomes de import para pacotes PyPI
    package_name_mapping = {
        "pydantic_settings": "pydantic-settings",
        "psycopg2": "psycopg2-binary",
        "yaml": "pyyaml",
        "ldap": "python-ldap",
        "google": "protobuf",  # google.protobuf vem do pacote protobuf
        "grpc": "grpcio",  # import grpc vem do pacote grpcio
    }

    # Aplica mapeamento se necessário
    pypi_package = package_name_mapping.get(package, package)

    # Faz backup do pyproject.toml antes de modificar
    if not dry_run:
        pyproject = project / "pyproject.toml"
        backup = project / "pyproject.toml.bak"

        try:
            import shutil

            shutil.copy2(pyproject, backup)
            print(f"   📋 Backup criado: {backup.name}")
        except Exception as e:
            print(f"   ⚠️  Não foi possível criar backup: {e}")

    cmd = ["poetry", "add", pypi_package]
    if dry_run:
        cmd.append("--dry-run")

    try:
        print(f"   🔧 {'Simulando' if dry_run else 'Executando'}: {' '.join(cmd)}")

        result = subprocess.run(
            cmd, check=False, cwd=project, capture_output=True, text=True, timeout=60
        )

        if result.returncode == 0:
            print(
                f"   ✅ {'Seria adicionado' if dry_run else 'Adicionado'}: {pypi_package} (import: {package})"
            )
            return True
        print(f"   ❌ Erro ao adicionar {pypi_package} (import: {package}):")
        print(f"      {result.stderr}")
        return False

    except subprocess.TimeoutExpired:
        print(f"   ❌ Timeout ao adicionar {pypi_package}")
        return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False


def main() -> int:
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Descobre e adiciona dependências Python faltantes"
    )
    parser.add_argument(
        "projects", nargs="+", help="Diretórios dos projetos para analisar"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica as mudanças (sem esta flag, apenas simula)",
    )
    parser.add_argument(
        "--check-import",
        action="store_true",
        help="Verifica se o import realmente não existe antes de adicionar",
    )
    parser.add_argument(
        "--analyze-versions",
        action="store_true",
        help="Analisa versões e mostra quem segura atualizações",
    )
    parser.add_argument("--save-report", help="Salva relatório completo em arquivo")

    args = parser.parse_args()

    print("🔍 DESCOBERTA DE DEPENDÊNCIAS FALTANTES")
    print("=" * 50)

    total_missing = 0
    total_added = 0
    all_missing_deps = set()  # Para análise de versões
    project_reports: list[Any] = []  # Para relatório

    for project_path in args.projects:
        project = Path(project_path)

        if not project.exists():
            print(f"\n❌ Projeto não encontrado: {project}")
            continue

        if not (project / "pyproject.toml").exists():
            print(f"\n⚠️  Pulando {project} - não tem pyproject.toml")
            continue

        # Descobre imports faltantes
        missing = discover_missing_imports(project)
        total_missing += len(missing)
        all_missing_deps.update(missing)

        # Guarda para relatório
        project_reports.append(
            {"project": project.name, "missing": list(missing), "added": []}
        )

        if missing and args.apply:
            print("\n   🚀 Adicionando dependências faltantes...")

            for package in sorted(missing):
                # Opcionalmente verifica se realmente não importa
                if args.check_import and check_import_exists(package):
                    print(f"   ⏭️  {package} já pode ser importado, pulando...")
                    continue

                if add_dependency(project, package, dry_run=False):
                    total_added += 1
                    project_reports[-1]["added"].append(package)

        elif missing and not args.apply:
            print("\n   💡 Use --apply para adicionar estas dependências")

    # Análise de versões se solicitada
    if args.analyze_versions and all_missing_deps:
        print("\n" + "=" * 50)
        print("📊 ANÁLISE DE VERSÕES - QUEM SEGURA ATUALIZAÇÕES")
        print("=" * 50)

        workspace_root = Path.cwd()

        for package in sorted(all_missing_deps):
            versions = get_package_versions_in_workspace(workspace_root, package)

            if versions:
                print(f"\n📦 {package}:")
                analysis = analyze_version_restrictions(versions)

                if analysis["exact_pins"]:
                    print("   ⚠️  Versões exatas (mais restritivas):")
                    for item in analysis["exact_pins"]:
                        print(f"      - {item}")

                if analysis["upper_bounds"]:
                    print("   ⚠️  Com limite superior:")
                    for item in analysis["upper_bounds"]:
                        print(f"      - {item}")

                if analysis["flexible"]:
                    print("   ✅ Versões flexíveis:")
                    for item in analysis["flexible"]:
                        print(f"      - {item}")

                # Identifica o mais restritivo
                if analysis["restrictive"]:
                    print(
                        f"   🚫 Projetos segurando atualizações: {', '.join(set(analysis['restrictive']))}"
                    )

    # Salva relatório se solicitado
    if args.save_report:
        report_path = Path(args.save_report)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("RELATÓRIO DE DEPENDÊNCIAS FALTANTES\n")
            f.write(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")

            for report in project_reports:
                f.write(f"Projeto: {report['project']}\n")
                if report["missing"]:
                    f.write(
                        f"  Dependências faltantes: {', '.join(report['missing'])}\n"
                    )
                if report["added"]:
                    f.write(
                        f"  Dependências adicionadas: {', '.join(report['added'])}\n"
                    )
                f.write("\n")

            f.write("-" * 60 + "\n")
            f.write(f"Total de imports faltantes: {total_missing}\n")
            f.write(f"Total de dependências adicionadas: {total_added}\n")

            if args.analyze_versions and all_missing_deps:
                f.write("\n" + "=" * 60 + "\n")
                f.write("ANÁLISE DE VERSÕES\n")
                f.write("=" * 60 + "\n")

                for package in sorted(all_missing_deps):
                    versions = get_package_versions_in_workspace(
                        workspace_root, package
                    )
                    if versions:
                        f.write(f"\n{package}:\n")
                        f.writelines(
                            f"  {proj}: {ver}\n"
                            for proj, ver in sorted(versions.items())
                        )

        print(f"\n💾 Relatório salvo em: {report_path}")

    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO:")
    print(f"   Total de imports faltantes: {total_missing}")

    if args.apply:
        print(f"   Total de dependências adicionadas: {total_added}")
    else:
        print("   💡 Execute com --apply para adicionar as dependências")

    return 0 if total_missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
