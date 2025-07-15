#!/usr/bin/env python3
"""Script para testar filtragem correta de dependências descobertas."""

import tomllib
from pathlib import Path


def get_installed_packages(project: Path) -> set[str]:
    """Obtém pacotes já instalados/declarados no projeto."""
    installed = set()

    pyproject_path = project / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            # Dependências principais
            deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            installed.update(deps.keys())

            # Dependências de grupos
            groups = data.get("tool", {}).get("poetry", {}).get("group", {})
            for group_data in groups.values():
                group_deps = group_data.get("dependencies", {})
                installed.update(group_deps.keys())

        except Exception as e:
            print(f"Erro: {e}")

    # Remove 'python' que não é um pacote
    installed.discard("python")

    return installed


def filter_discovered_dependencies(
    discovered: dict[str, set[str]], installed: set[str]
) -> dict[str, set[str]]:
    """Filtra apenas dependências realmente faltantes."""
    filtered = {}

    # Mapeamento de pacotes que cobrem múltiplos imports
    package_covers = {
        "protobuf": {"google", "google.protobuf"},
        "grpcio": {"grpc", "grpc.aio"},
        "psycopg2-binary": {"psycopg2"},
        "pydantic-settings": {"pydantic_settings"},
    }

    # Cria conjunto de todos os imports cobertos
    covered_imports = installed.copy()
    for package, imports in package_covers.items():
        if package in installed:
            covered_imports.update(imports)

    # Filtra cada categoria
    for category, deps in discovered.items():
        filtered_deps = set()

        for dep in deps:
            # Normaliza para lowercase para comparação
            dep_lower = dep.lower()

            # Pula se já está instalado (case insensitive)
            if dep_lower in {pkg.lower() for pkg in covered_imports}:
                continue

            # Pula módulos da stdlib conhecidos
            if dep in {
                "copy",
                "operator",
                "os",
                "sys",
                "re",
                "json",
                "time",
                "datetime",
            }:
                continue

            # Pula duplicatas com case diferente
            if dep == "Django" and "django" in covered_imports:
                continue

            filtered_deps.add(dep)

        if filtered_deps:
            filtered[category] = filtered_deps

    return filtered


def main():
    # Simula descoberta do sync_dependencies.py
    discovered = {
        "runtime": {
            "Django",
            "Pillow",
            "celery",
            "click",
            "copy",
            "crispy-bootstrap5",
            "dj-database-url",
            "django",
            "django-cors-headers",
            "django-crispy-forms",
            "django-csp",
            "django-environ",
            "django-extensions",
            "django-filter",
            "django-prometheus",
            "django-redis",
            "django-security",
            "djangorestframework",
            "fastapi",
            "flext-core",
            "flext-observability",
            "grpcio",
            "grpcio-tools",
            "gunicorn",
            "httpx",
            "opentelemetry-api",
            "opentelemetry-instrumentation-django",
            "opentelemetry-sdk",
            "operator",
            "protobuf",
            "psycopg-binary",
            "psycopg2-binary",
            "pydantic",
            "pydantic-settings",
            "redis",
            "rich",
            "uvicorn",
            "whitenoise",
            "google",
            "grpc",
        },
        "test": {"django", "pytest"},
    }

    project = Path("flext-web")
    installed = get_installed_packages(project)

    print(f"📦 Pacotes instalados: {len(installed)}")
    print(
        f"🔍 Dependências descobertas: {sum(len(deps) for deps in discovered.values())}"
    )

    # Filtra
    filtered = filter_discovered_dependencies(discovered, installed)

    print(
        f"\n✅ Dependências REALMENTE faltantes: {sum(len(deps) for deps in filtered.values())}"
    )
    for category, deps in filtered.items():
        if deps:
            print(f"\n[{category}]:")
            for dep in sorted(deps):
                print(f"  - {dep}")


if __name__ == "__main__":
    main()
