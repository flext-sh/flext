#!/usr/bin/env python3
"""Detecta duplicações de código entre projetos FLEXT.
Foca em imports, classes e funções comuns.
"""

import ast
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


def get_python_files(project_path: Path) -> list[Path]:
    """Retorna todos arquivos Python em um projeto."""
    src_dir = project_path / "src"
    if not src_dir.exists():
        return []
    return list(src_dir.rglob("*.py"))


def extract_imports(file_path: Path) -> set[str]:
    """Extrai imports de um arquivo Python."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.update(f"{node.module}.{alias.name}" for alias in node.names)

        return imports
    except Exception:
        return set()


def extract_class_names(file_path: Path) -> set[str]:
    """Extrai nomes de classes de um arquivo Python."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        classes = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.add(node.name)

        return classes
    except Exception:
        return set()


def extract_function_names(file_path: Path) -> set[str]:
    """Extrai nomes de funções de um arquivo Python."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        functions = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.add(node.name)

        return functions
    except Exception:
        return set()


def get_file_hash(file_path: Path) -> str:
    """Calcula hash do conteúdo de um arquivo."""
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        return hashlib.md5(content).hexdigest()
    except Exception:
        return ""


def analyze_duplications() -> None:
    """Analisa duplicações entre projetos FLEXT."""
    workspace_path = Path("/home/marlonsc/flext")

    # Encontra todos os projetos flext-*
    flext_projects = [
        p for p in workspace_path.iterdir()
        if p.is_dir() and p.name.startswith("flext-")
    ]

    # Estruturas para armazenar dados
    project_imports = {}
    project_classes = {}
    project_functions = {}
    file_hashes = defaultdict(list)
    common_imports = Counter()
    common_classes = Counter()
    common_functions = Counter()

    # Analisa cada projeto
    for project_path in flext_projects:
        project_name = project_path.name
        python_files = get_python_files(project_path)

        # Coleta dados do projeto
        all_imports = set()
        all_classes = set()
        all_functions = set()

        for py_file in python_files:
            # Imports
            file_imports = extract_imports(py_file)
            all_imports.update(file_imports)

            # Classes
            file_classes = extract_class_names(py_file)
            all_classes.update(file_classes)

            # Funções
            file_functions = extract_function_names(py_file)
            all_functions.update(file_functions)

            # Hash de arquivos similares
            file_hash = get_file_hash(py_file)
            if file_hash:
                relative_path = py_file.relative_to(project_path)
                file_hashes[file_hash].append((project_name, str(relative_path)))

        project_imports[project_name] = all_imports
        project_classes[project_name] = all_classes
        project_functions[project_name] = all_functions

        # Conta frequência global
        for imp in all_imports:
            common_imports[imp] += 1
        for cls in all_classes:
            common_classes[cls] += 1
        for func in all_functions:
            common_functions[func] += 1

    # Relatório de duplicações
    for import_name, count in common_imports.most_common(20):
        if count > 1:
            [name for name, imports in project_imports.items() if import_name in imports]

    duplicated_classes = [(name, count) for name, count in common_classes.most_common() if count > 1]

    if duplicated_classes:
        for class_name, count in duplicated_classes[:15]:
            [name for name, classes in project_classes.items() if class_name in classes]

    duplicated_functions = [(name, count) for name, count in common_functions.most_common() if count > 1 and not name.startswith("_")]

    if duplicated_functions:
        for func_name, count in duplicated_functions[:15]:
            [name for name, funcs in project_functions.items() if func_name in funcs]

    identical_files = [(hash_val, files) for hash_val, files in file_hashes.items() if len(files) > 1]

    if identical_files:
        for file_hash, files in identical_files[:10]:
            for _project, _file_path in files:
                pass

    # Analisa dependências entre projetos

    project_dependencies = defaultdict(list)

    for project_name, imports in project_imports.items():
        for import_name in imports:
            # Verifica se import é de outro projeto FLEXT
            for other_project in flext_projects:
                other_name = other_project.name
                if other_name != project_name and other_name.replace("-", "_") in import_name:
                    project_dependencies[project_name].append(other_name)

    for deps in project_dependencies.values():
        if deps:
            pass

    if not project_dependencies:
        pass

    # Estatísticas finais

    sum(len(imports) for imports in project_imports.values())
    len(set().union(*project_imports.values()))

    sum(len(classes) for classes in project_classes.values())
    len(set().union(*project_classes.values()))

    sum(len(functions) for functions in project_functions.values())
    len(set().union(*project_functions.values()))


if __name__ == "__main__":
    analyze_duplications()
