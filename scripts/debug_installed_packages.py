#!/usr/bin/env python3
"""Debug para verificar detecção de pacotes instalados."""

import tomllib
from pathlib import Path


def get_project_installed_packages(project: Path) -> set[str]:
    """Obtém lista de pacotes instalados no projeto."""
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

    return installed


def main():
    project = Path("flext-web")
    installed = get_project_installed_packages(project)

    print(f"📦 Pacotes instalados em {project}: {len(installed)}")
    print("\nPacotes:")
    for pkg in sorted(installed):
        print(f"  - {pkg}")

    # Verifica alguns específicos
    print("\n🔍 Verificações específicas:")
    for check in ["django", "redis", "fastapi", "grpcio", "protobuf"]:
        print(f"  {check}: {'✅' if check in installed else '❌'}")


if __name__ == "__main__":
    main()
