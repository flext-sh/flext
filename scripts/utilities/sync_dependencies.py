#!/usr/bin/env python3
"""Sincroniza as versões de bibliotecas entre projetos no workspace.

Este script pode funcionar em dois modos:
1. Modo padrão: usa o projeto principal (dc-api-x) como fonte e atualiza os outros projetos
2. Modo consolidação: coleta as versões mais recentes de todos os projetos e atualiza todos

No modo de consolidação, o script encontra a versão mais recente de cada dependência
em todos os projetos e depois atualiza todos os projetos para usar essas versões.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

import packaging.version
import tomli
import tomli_w


def load_toml(file_path: Path) -> dict:
    """Load a TOML file."""
    try:
        with open(file_path, "rb") as f:
            return tomli.load(f)
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        return {}


def save_toml(file_path: Path, data: dict) -> None:
    """Save a dictionary as a TOML file."""
    try:
        with open(file_path, "wb") as f:
            tomli_w.dump(data, f)
        print(f"Arquivo {file_path} atualizado com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar {file_path}: {e}")


def extract_dependencies(toml_data: dict) -> dict[str, str]:
    """Extract dependencies from a pyproject.toml file."""
    dependencies: dict = {}

    # Poetry format
    if "tool" in toml_data and "poetry" in toml_data["tool"]:
        if "dependencies" in toml_data["tool"]["poetry"]:
            for dep, version in toml_data["tool"]["poetry"]["dependencies"].items():
                if dep != "python":
                    if isinstance(version, str):
                        dependencies[dep] = version
                    elif isinstance(version, dict) and "version" in version:
                        dependencies[dep] = version["version"]

        # Dev dependencies
        if "group" in toml_data["tool"]["poetry"]:
            for group_data in toml_data["tool"]["poetry"]["group"].values():
                if "dependencies" in group_data:
                    for dep, version in group_data["dependencies"].items():
                        if dep != "python" and dep not in dependencies:
                            if isinstance(version, str):
                                dependencies[dep] = version
                            elif isinstance(version, dict) and "version" in version:
                                dependencies[dep] = version["version"]

    # PEP 621 format
    elif "flx_project" in toml_data and "dependencies" in toml_data["flx_project"]:
        for dep_spec in toml_data["flx_project"]["dependencies"]:
            match = re.match(r"([a-zA-Z0-9_-]+)([><=~!].+)", dep_spec)
            if match:
                dependencies[match.group(1)] = match.group(2)

    return dependencies


def parse_requirements_txt(file_path: Path) -> dict[str, str]:
    """Analisa um arquivo requirements.txt e retorna um dicionário de dependências."""
    dependencies: dict = {}
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Ignora opções como -e ou -r
                    if line.startswith("-"):
                        continue

                    # Remove comentários inline
                    line = line.split("#")[0].strip()

                    # Extrai nome e versão
                    match = re.match(r"([a-zA-Z0-9_.-]+)([><=~!].+)?", line)
                    if match:
                        name = match.group(1)
                        version = match.group(2) if match.group(2) else ""
                        dependencies[name] = version
    except Exception as e:
        print(f"Erro ao analisar {file_path}: {e}")

    return dependencies


def update_toml_dependencies(
    file_path: Path,
    main_dependencies: dict[str, str],
    force: bool = False,
) -> None:
    """Atualiza as dependências em um arquivo pyproject.toml."""
    toml_data = load_toml(file_path)
    if not toml_data:
        return

    updated = False

    # Poetry format
    if "tool" in toml_data and "poetry" in toml_data["tool"]:
        if "dependencies" in toml_data["tool"]["poetry"]:
            for dep, version in list(
                toml_data["tool"]["poetry"]["dependencies"].items(),
            ):
                if dep in main_dependencies and dep != "python":
                    if isinstance(version, str):
                        if force or version != main_dependencies[dep]:
                            toml_data["tool"]["poetry"]["dependencies"][dep] = (
                                main_dependencies[dep]
                            )
                            print(
                                f"  Atualizando {dep}: {version} -> {main_dependencies[dep]}",
                            )
                            updated = True
                    elif isinstance(version, dict) and "version" in version:
                        if force or version["version"] != main_dependencies[dep]:
                            toml_data["tool"]["poetry"]["dependencies"][dep][
                                "version"
                            ] = main_dependencies[dep]
                            print(
                                f"  Atualizando {dep}: {version['version']} -> {main_dependencies[dep]}",
                            )
                            updated = True

        # Dev dependencies
        if "group" in toml_data["tool"]["poetry"]:
            for group_name, group_data in toml_data["tool"]["poetry"]["group"].items():
                if "dependencies" in group_data:
                    for dep, version in list(group_data["dependencies"].items()):
                        if dep in main_dependencies and dep != "python":
                            if isinstance(version, str):
                                if force or version != main_dependencies[dep]:
                                    toml_data["tool"]["poetry"]["group"][group_name][
                                        "dependencies"
                                    ][dep] = main_dependencies[dep]
                                    print(
                                        f"  Atualizando {dep} (grupo {group_name}): {version} -> {main_dependencies[dep]}",
                                    )
                                    updated = True
                            elif isinstance(version, dict) and "version" in version:
                                if (
                                    force
                                    or version["version"] != main_dependencies[dep]
                                ):
                                    toml_data["tool"]["poetry"]["group"][group_name][
                                        "dependencies"
                                    ][dep]["version"] = main_dependencies[dep]
                                    print(
                                        f"  Atualizando {dep} (grupo {group_name}): {
                                            version['version']
                                        } -> {main_dependencies[dep]}",
                                    )
                                    updated = True

    # PEP 621 format
    elif "flx_project" in toml_data and "dependencies" in toml_data["flx_project"]:
        new_deps: list = []
        for dep_spec in toml_data["flx_project"]["dependencies"]:
            match = re.match(r"([a-zA-Z0-9_-]+)([><=~!].+)", dep_spec)
            if match and match.group(1) in main_dependencies:
                if force or match.group(2) != main_dependencies[match.group(1)]:
                    new_deps.append(
                        f"{match.group(1)}{main_dependencies[match.group(1)]}",
                    )
                    print(
                        f"  Atualizando {match.group(1)}: {match.group(2)} -> {main_dependencies[match.group(1)]}",
                    )
                    updated = True
                    new_deps.append(dep_spec)
                new_deps.append(dep_spec)

        toml_data["flx_project"]["dependencies"] = new_deps

    if updated or force:
        save_toml(file_path, toml_data)
        print(f"Nenhuma dependência atualizada em {file_path}")


def update_requirements_txt(
    file_path: Path,
    main_dependencies: dict[str, str],
    force: bool = False,
) -> None:
    """Atualiza as versões das dependências em um arquivo requirements.txt."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        updated = False
        new_lines: list = []

        for line in lines:
            original_line = line
            line = line.strip()

            if not line or line.startswith(("#", "-")):
                new_lines.append(original_line)
                continue

            # Remove comentários inline
            code_part = line.split("#")[0].strip()
            comment_part = line[len(code_part) :] if len(line) > len(code_part) else ""

            # Extrai nome e versão
            match = re.match(r"([a-zA-Z0-9_.-]+)([><=~!].+)?", code_part)
            if match:
                name = match.group(1)
                current_version = match.group(2) if match.group(2) else ""

                if name in main_dependencies:
                    if force or current_version != main_dependencies[name]:
                        new_line = f"{name}{main_dependencies[name]}{comment_part}\n"
                        new_lines.append(new_line)
                        updated = True
                        print(
                            f"  Atualizando {name}: {current_version} -> {main_dependencies[name]}",
                        )
                        new_lines.append(original_line)
                    new_lines.append(original_line)
                new_lines.append(original_line)

        if updated or force:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"Arquivo {file_path} atualizado com sucesso.")
            print(f"Nenhuma dependência atualizada em {file_path}")

    except Exception as e:
        print(f"Erro ao atualizar {file_path}: {e}")


def find_dependency_files(workspace_path: Path) -> list[tuple[Path, str]]:
    """Encontra todos os arquivos pyproject.toml e requirements.txt no workspace."""
    dependency_files: list = []

    for root, dirs, files in os.walk(workspace_path):
        # Ignora diretórios ocultos e ambientes virtuais
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in {"__pycache__", "venv", ".venv"}
        ]

        for file in files:
            if file == "pyproject.toml":
                dependency_files.append((Path(root) / file, "toml"))
            elif file == "requirements.txt" or file.endswith("-requirements.txt"):
                dependency_files.append((Path(root) / file, "txt"))

    return dependency_files


def detect_projects(workspace_path: Path) -> list[str]:
    """Detecta projetos no workspace usando a mesma lógica do Makefile.
    Exclui diretórios que começam com ".", "reference", "docs", "logs", "scripts".
    """
    exclude_patterns = {"reference", "docs", "logs", "scripts"}
    projects: list = []

    try:
        for item in workspace_path.iterdir():
            if item.is_dir():
                name = item.name
                # Exclui diretórios que começam com "." ou estão na lista de
                # exclusão
                if not name.startswith(".") and name not in exclude_patterns:
                    # Verifica se o diretório contém um pyproject.toml
                    if (item / "pyproject.toml").exists():
                        projects.append(name)
    except Exception as e:
        print(f"Erro ao detectar projetos: {e}")

    return sorted(projects)


def filter_dependency_files_by_projects(
    dependency_files: list[tuple[Path, str]],
    projects: list[str],
    workspace_path: Path,
) -> list[tuple[Path, str]]:
    """Filtra arquivos de dependências para incluir apenas os projetos especificados."""
    if not projects:
        return dependency_files

    filtered_files: list = []
    project_paths = {workspace_path / flx_project for flx_project in projects}

    for file_path, file_type in dependency_files:
        # Verifica se o arquivo está dentro de algum dos projetos especificados
        for project_path in project_paths:
            try:
                file_path.relative_to(project_path)
                filtered_files.append((file_path, file_type))
                break
            except ValueError:
                continue

    return filtered_files


def is_version_newer(version1: str, version2: str) -> bool:
    """Compara duas strings de versão e retorna True se version1 for mais recente que version2.
    Lida com formatos comuns de versão como ^1.2.3, ~1.2.3, >=1.2.3, etc.
    """

    # Extrai o número da versão sem os prefixos
    def extract_version(version_str) -> Any:
        # Remove prefixos comuns
        match = re.search(r"[0-9]+(\.[0-9]+)*", version_str)
        if match:
            return match.group(0)
        return "0.0.0"  # Versão padrão se não conseguir extrair

    try:
        # Extrai os números de versão
        v1 = extract_version(version1)
        v2 = extract_version(version2)

        # Compara as versões
        return packaging.version.parse(v1) > packaging.version.parse(v2)
    except Exception:
        # Em caso de erro, retorna False (mantém a versão atual)
        return False


def collect_latest_versions(
    dependency_files: list[tuple[Path, str]],
) -> dict[str, tuple[str, str]]:
    """Coleta as versões mais recentes de todas as dependências em todos os projetos.
    Retorna um dicionário com o nome da dependência e uma tupla (versão, origem).
    """
    all_dependencies: dict = {}

    for file_path, file_type in dependency_files:
        print(f"Coletando dependências de {file_path}...")

        if file_type == "toml":
            toml_data = load_toml(file_path)
            deps = extract_dependencies(toml_data)
        else:  # txt
            deps = parse_requirements_txt(file_path)

        # Atualiza o dicionário com as versões mais recentes
        for dep_name, dep_version in deps.items():
            if dep_name == "python":
                continue

            if dep_name not in all_dependencies:
                all_dependencies[dep_name] = (dep_version, str(file_path))
                current_version, _current_origin = all_dependencies[dep_name]
                if is_version_newer(dep_version, current_version):
                    all_dependencies[dep_name] = (dep_version, str(file_path))

    return all_dependencies


def parse_args() -> Any:
    """Analisa os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Sincroniza versões de dependências entre projetos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s                           # Detecta projetos automaticamente e usa modo consolidação
  %(prog)s --projects flx dc-oracle-wms  # Sincroniza apenas projetos específicos
  %(prog)s --source flx              # Usa 'flx' como projeto fonte
  %(prog)s --consolidate             # Força modo consolidação (versões mais recentes)
  %(prog)s --dry-run                 # Simula as mudanças sem aplicá-las
        """,
    )

    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Força a atualização mesmo quando as versões são iguais",
    )

    parser.add_argument(
        "--flx_project",
        "-p",
        help="Especifica um projeto específico para atualizar (nome do diretório)",
    )

    parser.add_argument(
        "--projects",
        nargs="+",
        metavar="PROJECT",
        help="Lista de projetos específicos para sincronizar",
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Executa em modo de simulação, sem fazer alterações",
    )

    parser.add_argument(
        "--consolidate",
        "-c",
        action="store_true",
        help="Modo de consolidação: coleta as versões mais recentes de todos os projetos",
    )

    parser.add_argument(
        "--source",
        "-s",
        help="Projeto fonte para as versões (detectado automaticamente se não especificado)",
    )

    parser.add_argument(
        "--list-projects",
        action="store_true",
        help="Lista os projetos detectados e sai",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace_path = Path.cwd()

    # Detecta projetos automaticamente
    detected_projects = detect_projects(workspace_path)

    if args.list_projects:
        print("Projetos detectados no workspace:")
        for flx_project in detected_projects:
            print(f"  - {flx_project}")
        return

    if not detected_projects:
        print("Nenhum projeto com pyproject.toml encontrado no workspace.")
        sys.exit(1)

    print(f"Projetos detectados: {', '.join(detected_projects)}")

    # Determina quais projetos processar
    target_projects: list = []
    if args.projects:
        target_projects = args.projects
        # Verifica se os projetos especificados existem
        invalid_projects = [p for p in target_projects if p not in detected_projects]
        if invalid_projects:
            print(f"Projetos não encontrados: {', '.join(invalid_projects)}")
            print(f"Projetos disponíveis: {', '.join(detected_projects)}")
            sys.exit(1)
    elif args.flx_project:
        target_projects = [args.flx_project]
        if args.flx_project not in detected_projects:
            print(f"Projeto '{args.flx_project}' não encontrado.")
            print(f"Projetos disponíveis: {', '.join(detected_projects)}")
            sys.exit(1)
        target_projects = detected_projects

    print(f"Processando projetos: {', '.join(target_projects)}")

    # Encontra todos os arquivos de dependências
    dependency_files = find_dependency_files(workspace_path)

    # Filtra por projetos específicos
    dependency_files = filter_dependency_files_by_projects(
        dependency_files,
        target_projects,
        workspace_path,
    )

    print(
        f"Encontrados {
            len(dependency_files)
        } arquivos de dependências nos projetos selecionados.",
    )

    if not dependency_files:
        print("Nenhum arquivo de dependências encontrado nos projetos especificados.")
        sys.exit(1)

    # Determina o modo de operação
    use_consolidation = args.consolidate
    source_project = args.source

    # Se não há projeto fonte especificado e não é modo consolidação, tenta
    # detectar automaticamente
    if not use_consolidation and not source_project:
        if len(target_projects) == 1:
            source_project = target_projects[0]
            print(
                f"Usando '{source_project}' como projeto fonte (único projeto especificado).",
            )
            # Se há múltiplos projetos, usa modo consolidação por padrão
            use_consolidation = True
            print(
                "Múltiplos projetos detectados. Usando modo consolidação automaticamente.",
            )

    # Verifica se o projeto fonte existe
    if source_project and source_project not in detected_projects:
        print(f"Projeto fonte '{source_project}' não encontrado.")
        print(f"Projetos disponíveis: {', '.join(detected_projects)}")
        print("Alternativa: use --consolidate para modo de consolidação.")
        sys.exit(1)

    # Modo de consolidação: coleta as versões mais recentes de todos os
    # projetos
    if use_consolidation:
        print(
            "\nModo de consolidação: coletando versões mais recentes de todos os projetos...",
        )
        latest_versions = collect_latest_versions(dependency_files)

        print(f"\nEncontradas {len(latest_versions)} dependências únicas:")
        for dep_name, (dep_version, origin) in sorted(latest_versions.items()):
            origin_name = Path(origin).parent.name
            print(f"  {dep_name}: {dep_version} (de {origin_name})")

        # Converte para o formato esperado pelas funções de atualização
        main_dependencies = {
            name: version for name, (version, _) in latest_versions.items()
        }

        # Modo padrão: usa o projeto fonte como referência
        main_toml_path = workspace_path / source_project / "pyproject.toml"

        if not main_toml_path.exists():
            print(f"Arquivo pyproject.toml não encontrado em: {main_toml_path}")
            sys.exit(1)

        print(f"\nUsando projeto fonte: {source_project}")
        main_toml_data = load_toml(main_toml_path)
        main_dependencies = extract_dependencies(main_toml_data)

        print(f"Encontradas {len(main_dependencies)} dependências no projeto fonte:")
        for dep, version in sorted(main_dependencies.items()):
            print(f"  {dep}: {version}")

    if args.dry_run:
        print("\n" + "=" * 60)
        print("MODO DE SIMULAÇÃO - Nenhuma alteração será feita")
        print("=" * 60)

    print(f"\nAtualizando {len(dependency_files)} arquivos de dependências...")

    updated_count = 0
    for file_path, file_type in dependency_files:
        # No modo de consolidação, processa todos os arquivos
        # No modo padrão, ignora o arquivo fonte
        if not use_consolidation and source_project:
            main_toml_path = workspace_path / source_project / "pyproject.toml"
            if file_path == main_toml_path:
                print(f"\nIgnorando arquivo fonte: {file_path}")
                continue

        project_name = file_path.parent.name
        print(f"\nProcessando {project_name}/{file_path.name}...")

        if args.dry_run:
            print(f"  [SIMULAÇÃO] Atualizaria {file_path}")
            continue

        try:
            if file_type == "toml":
                update_toml_dependencies(file_path, main_dependencies, force=args.force)
            elif file_type == "txt":
                update_requirements_txt(file_path, main_dependencies, force=args.force)
            updated_count += 1
        except Exception as e:
            print(f"  Erro ao processar {file_path}: {e}")

    if not args.dry_run:
        print(f"\nProcessamento concluído. {updated_count} arquivos processados.")
        print(
            f"\nSimulação concluída. {
                len(dependency_files)
            } arquivos seriam processados.",
        )


if __name__ == "__main__":
    main()
