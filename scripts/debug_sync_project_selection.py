#!/usr/bin/env python3
"""Debug script para entender seleção de projetos no sync_dependencies.py"""

import tomllib
from pathlib import Path


def find_flext_projects():
    """Mesma função do sync_dependencies.py"""
    projects = []
    for item in Path().iterdir():
        if item.is_dir() and not item.name.startswith("."):
            pyproject_file = item / "pyproject.toml"
            if pyproject_file.exists():
                try:
                    with Path(pyproject_file).open("rb") as f:
                        data = tomllib.load(f)
                    if "tool" in data and "poetry" in data["tool"]:
                        projects.append(item)
                except Exception:
                    continue
    return sorted(projects)


def main():
    # Descobre projetos
    all_projects = find_flext_projects()
    print(f"Total projetos encontrados: {len(all_projects)}")

    # Simula argumento --projects flext-web
    target = "flext-web"

    projects = [proj for proj in all_projects if proj.name == target]

    print(f"\nProjetos filtrados para '{target}': {len(projects)}")
    if projects:
        for p in projects:
            print(f"  - {p.name} (path: {p})")

    # Verifica se flext-grpc está na lista
    print("\nVerificando se flext-grpc está na lista filtrada:")
    for p in projects:
        if p.name == "flext-grpc":
            print("  ❌ ERRO: flext-grpc está na lista!")
        else:
            print(f"  ✅ OK: {p.name}")


if __name__ == "__main__":
    main()
