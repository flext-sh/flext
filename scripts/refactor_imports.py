#!/usr/bin/env python3
"""Refatora imports em todos os projetos para usarem apenas o pacote raiz.

Ações executadas:
- Reescreve `from <pkg>.<submod> import X` para `from <pkg> import X` em tests/, examples/ e scripts/
- Garante reexport no `src/<pkg>/__init__.py` para todos os símbolos usados por tests/examples/scripts
- Move imports de `if TYPE_CHECKING:` (terceiros/flext/projeto) para nível de módulo
- Mantém em `if TYPE_CHECKING:` apenas `typing` e `collections.abc` quando existirem
- Remove `sys.path.insert/append` e hacks similares nos arquivos alvo

Sem criação de módulos ou diretórios. Apenas edições em arquivos existentes.
"""

from __future__ import annotations

import ast
import operator
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

# ----------------------------- Descoberta do workspace -----------------------------


@dataclass(frozen=True)
class PackageInfo:
    """Information about a Python package in the workspace."""

    project_dir: Path
    package_name: str
    src_dir: Path
    init_file: Path
    exports: dict[str, set[str]]
    imports: dict[str, set[str]]
    missing_exports: dict[str, set[str]]
    unused_exports: dict[str, set[str]]


def discover_packages(workspace_root: Path) -> list[PackageInfo]:
    """Descobre todos os pacotes com layout src/ no monorepo."""
    results: list[PackageInfo] = []
    for init_path in workspace_root.glob("**/src/*/__init__.py"):
        pkg_dir = init_path.parent
        package_name = pkg_dir.name
        project_dir = pkg_dir.parent.parent
        # Ignorar diretórios ocultos
        if any(part.startswith(".") for part in init_path.parts):
            continue
        results.append(
            PackageInfo(
                project_dir=project_dir,
                package_name=package_name,
                src_dir=pkg_dir,
                init_file=init_path,
                exports={},
                imports={},
                missing_exports={},
                unused_exports={},
            ),
        )
    return results


def iter_target_files(project_dir: Path) -> Iterable[Path]:
    """Itera arquivos Python em tests/, examples/ e scripts/ do projeto."""
    for pattern in ("tests/**/*.py", "examples/**/*.py", "scripts/**/*.py"):
        yield from project_dir.glob(pattern)


# ----------------------------- Coleta de reexports -----------------------------


@dataclass
class ExportRequest:
    """Request to export specific names from a package."""

    submodule: str  # caminho relativo dentro do pacote (ex.: "utils.config")
    names: set[str]
    package: str
    project_dir: Path


def collect_needed_exports(file_path: Path, package_name: str) -> list[ExportRequest]:
    """Coleta símbolos importados de submódulos do pacote a partir do arquivo."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception:
        return []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    needed: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mod = node.module
            pkg_prefix = f"{package_name}."
            if mod.startswith(pkg_prefix):
                submodule = mod[len(pkg_prefix) :]
                if not submodule:
                    continue
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    needed.setdefault(submodule, set()).add(alias.asname or alias.name)

    return [
        ExportRequest(
            submodule=sub, names=names, package=package_name, project_dir=Path.cwd()
        )
        for sub, names in needed.items()
    ]


def ensure_reexports(
    init_file: Path,
    package_name: str,
    requests: list[ExportRequest],
) -> bool:
    """Garante que `__init__.py` reexporte os símbolos solicitados.

    Retorna True se o arquivo foi modificado.
    """
    if not requests:
        return False

    try:
        content = init_file.read_text(encoding="utf-8")
    except Exception:
        return False

    original = content

    lines_to_add: list[str] = []
    for req in requests:
        for name in sorted(req.names):
            import_line = f"from {package_name}.{req.submodule} import {name}"
            if import_line not in content:
                lines_to_add.append(import_line)

    if not lines_to_add:
        return False

    insert_block = "\n" + "\n".join(lines_to_add) + "\n"

    last_import_pos = max(content.rfind("\nimport "), content.rfind("\nfrom "))
    if last_import_pos == -1:
        content = insert_block + content
    else:
        next_newline = content.find("\n", last_import_pos + 1)
        if next_newline == -1:
            content += insert_block
        else:
            content = (
                content[: next_newline + 1] + insert_block + content[next_newline + 1 :]
            )

    if content != original:
        init_file.write_text(content, encoding="utf-8")
        return True
    return False


# ----------------------------- Reescrita de arquivos alvo -----------------------------


_ALLOWED_TYPE_CHECKING_MODULES = ("typing", "collections.abc")


def _promote_type_checking_imports(updated: str) -> tuple[str, bool]:
    """Move imports de TYPE_CHECKING para topo, mantendo apenas stdlib (typing/collections.abc) no bloco."""
    changed = False
    try:
        tree = ast.parse(updated)
    except SyntaxError:
        return updated, changed

    lines = updated.splitlines(keepends=True)
    promoted_imports: list[str] = []
    keep_tc_blocks: list[tuple[int, int, str]] = []  # (start, end, text)

    for node in tree.body:
        if (
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "TYPE_CHECKING"
        ):
            start = getattr(node, "lineno", None)
            end = getattr(node, "end_lineno", None)
            if start is None or end is None:
                continue
            block_text = "".join(lines[start - 1 : end])

            try:
                tc_tree = ast.parse(block_text)
            except SyntaxError:
                continue

            kept_lines: list[str] = []
            for tc_node in tc_tree.body:
                if isinstance(tc_node, ast.Import):
                    for alias in tc_node.names:
                        name = alias.name
                        line = f"import {name}{' as ' + alias.asname if alias.asname else ''}"
                        if name.startswith(_ALLOWED_TYPE_CHECKING_MODULES):
                            kept_lines.append(line)
                        else:
                            promoted_imports.append(line)
                elif isinstance(tc_node, ast.ImportFrom):
                    mod = tc_node.module or ""
                    names = ", ".join(
                        f"{a.name}{' as ' + a.asname if a.asname else ''}"
                        for a in tc_node.names
                    )
                    # Allow None when module is empty; use a distinct variable name
                    importfrom_line: str | None = (
                        f"from {mod} import {names}" if mod else None
                    )
                    if not importfrom_line:
                        continue
                    if mod.startswith(_ALLOWED_TYPE_CHECKING_MODULES):
                        kept_lines.append(importfrom_line)
                    else:
                        promoted_imports.append(importfrom_line)

            kept_text = "\n".join(kept_lines).rstrip()
            if kept_text:
                new_block = (
                    "from typing import TYPE_CHECKING\n"
                    "if TYPE_CHECKING:\n    " + "\n    ".join(kept_lines) + "\n"
                )
                keep_tc_blocks.append((start, end, new_block))
            else:
                keep_tc_blocks.append((start, end, ""))

    if keep_tc_blocks or promoted_imports:
        header_insertion_index = 0
        if updated.startswith(("#!/", "# -*- coding:")):
            header_insertion_index = updated.find("\n") + 1

        promoted_text = (
            ("\n".join(dict.fromkeys(promoted_imports)) + "\n")
            if promoted_imports
            else ""
        )

        for start, end, new_block in sorted(
            keep_tc_blocks,
            key=operator.itemgetter(0),
            reverse=True,
        ):
            block_slice = "".join(lines[start - 1 : end])
            updated = updated.replace(block_slice, new_block, 1)

        if promoted_text:
            updated = (
                updated[:header_insertion_index]
                + promoted_text
                + updated[header_insertion_index:]
            )

        changed = True

    return updated, changed


def rewrite_file_imports(file_path: Path, package_name: str) -> bool:
    """Reescreve imports e limpa TYPE_CHECKING/sys.path hacks no arquivo alvo."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception:
        return False

    changed = False
    updated = source

    # 1) Remover sys.path hacks
    sys_path_pattern = re.compile(
        r"^\s*sys\.path\.(insert|append)\(.*\)\s*$",
        re.MULTILINE,
    )
    if sys_path_pattern.search(updated):
        updated = sys_path_pattern.sub("", updated)
        changed = True

    # 2) Reescrever from <pkg>.<sub> import X -> from <pkg> import X
    from_sub_pattern = re.compile(
        rf"^\s*from\s+{re.escape(package_name)}\.(?P<sub>[A-Za-z0-9_\.]+)\s+import\s+(?P<names>[^\n]+)$",
        re.MULTILINE,
    )

    def _replace_from_sub(m: re.Match[str]) -> str:
        nonlocal changed
        names = m.group("names").strip()
        changed = True
        return f"from {package_name} import {names}"

    updated = from_sub_pattern.sub(_replace_from_sub, updated)

    # 3) Promover imports de TYPE_CHECKING no próprio arquivo
    updated, tc_changed = _promote_type_checking_imports(updated)
    changed = changed or tc_changed

    if changed and updated != source:
        file_path.write_text(updated, encoding="utf-8")
        return True

    return False


def rewrite_type_checking_only(file_path: Path) -> bool:
    """Apenas promove imports de TYPE_CHECKING no arquivo (global)."""
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception:
        return False

    updated, tc_changed = _promote_type_checking_imports(source)
    if tc_changed and updated != source:
        file_path.write_text(updated, encoding="utf-8")
        return True
    return False


# ----------------------------- Execução -----------------------------


def main() -> None:
    """Main function to refactor imports across the FLEXT workspace."""
    workspace = Path.cwd()
    packages = discover_packages(workspace)

    total_files = 0
    total_changed = 0
    total_init_changed = 0

    for pkg in packages:
        target_files = list(iter_target_files(pkg.project_dir))
        if not target_files:
            continue

        print(f"\n🔧 Refatorando {pkg.project_dir.name} ({pkg.package_name})...")

        # 1) Coletar reexports necessários
        export_requests: dict[str, ExportRequest] = {}
        for py_file in target_files:
            for req in collect_needed_exports(py_file, pkg.package_name):
                entry = export_requests.setdefault(
                    req.submodule,
                    ExportRequest(
                        req.submodule, set(), pkg.package_name, pkg.project_dir
                    ),
                )
                entry.names.update(req.names)

        # 2) Atualizar __init__.py com reexports
        if ensure_reexports(
            pkg.init_file,
            pkg.package_name,
            list(export_requests.values()),
        ):
            total_init_changed += 1
            print(
                f"  🧩 Atualizado reexports em {pkg.init_file.relative_to(workspace)}",
            )

        # 3) Reescrever arquivos alvo
        project_changed = 0
        for py_file in target_files:
            total_files += 1
            if rewrite_file_imports(py_file, pkg.package_name):
                total_changed += 1
                project_changed += 1
                print(f"  ✅ {py_file.relative_to(workspace)}")

        print(f"  📊 Arquivos alterados: {project_changed}/{len(target_files)}")

    # 4) Passada global para TYPE_CHECKING em TODOS os .py
    print("\n🧹 Promovendo imports de TYPE_CHECKING em todos os arquivos Python...")
    all_py_files = [
        p
        for p in workspace.glob("**/*.py")
        if ".venv" not in p.parts
        and ".mypy_cache" not in p.parts
        and ".ruff_cache" not in p.parts
        and "node_modules" not in p.parts
        and ".git" not in p.parts
    ]
    global_changed = 0
    for py_file in all_py_files:
        if rewrite_type_checking_only(py_file):
            global_changed += 1

    print("\n🎉 REFATORAÇÃO COMPLETA!")
    print(f"📦 __init__ atualizados: {total_init_changed}")
    print(
        f"📊 Arquivos refatorados (imports/tests/examples/scripts): {total_changed}/{total_files}",
    )
    print(f"🧩 Arquivos com TYPE_CHECKING promovido (global): {global_changed}")


if __name__ == "__main__":
    main()
