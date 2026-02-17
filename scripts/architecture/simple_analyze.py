#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-architecture/SKILL.md
"""Análise simples de violações arquiteturais no flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path

from flext_core import FlextLogger

logger = FlextLogger(__name__)


def analyze_flext_core_violations() -> list[dict[str, str]]:
    """Analisa violações arquiteturais no flext-core."""
    flext_core_path = Path("flext-core/src/flext_core")
    if not flext_core_path.exists():
        return []

    # Padrões específicos que violam a arquitetura
    specific_patterns = [
        "meltano",
        "oracle",
        "ldap",
        "singer",
        "client-a",
        "client-b",
    ]

    violations: list[dict[str, str]] = []

    for py_file in flext_core_path.rglob("*.py"):
        if py_file.name == "__init__.py" or py_file.name.endswith(".bak"):
            continue

        violations.extend(_process_file(py_file, specific_patterns))

    return violations


def _process_file(py_file: Path, specific_patterns: list[str]) -> list[dict[str, str]]:
    """Process a single file for violations."""
    violations: list[dict[str, str]] = []

    try:
        content = Path(py_file).read_text(encoding="utf-8")
    except (OSError, ValueError, TypeError):
        return violations

    # Check for specific patterns
    violations.extend(_check_patterns(py_file, content, specific_patterns))

    # Check for import violations
    violations.extend(_check_imports(py_file, content))

    return violations


def _check_patterns(
    py_file: Path,
    content: str,
    specific_patterns: list[str],
) -> list[dict[str, str]]:
    """Check content for specific violation patterns."""
    return [
        {
            "file": str(py_file),
            "pattern": pattern,
            "action": f"Renomear {py_file.name} para {py_file.name}.bak",
        }
        for pattern in specific_patterns
        if re.search(r"\b" + pattern + r"\b", content, re.IGNORECASE)
    ]


def _check_imports(py_file: Path, content: str) -> list[dict[str, str]]:
    """Check content for import violations."""
    violations: list[dict[str, str]] = []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_name = alias.name.split(".")[0]
                if _is_violation_import(import_name):
                    violations.append({
                        "file": str(py_file),
                        "pattern": f"import {import_name}",
                        "action": f"Remover import violador em {py_file.name}",
                    })
        elif isinstance(node, ast.ImportFrom) and node.module:
            import_name = node.module.split(".")[0]
            if _is_violation_import(import_name):
                violations.append({
                    "file": str(py_file),
                    "pattern": f"from {node.module}",
                    "action": f"Remover import violador em {py_file.name}",
                })

    return violations


def _is_violation_import(import_name: str) -> bool:
    """Check if import is a violation."""
    return any(
        p in import_name.lower() for p in ["meltano", "oracle", "client-a", "client-b"]
    )


def analyze_ignore_comments() -> list[Path]:
    """Encontra todos os comentários # ignore nos arquivos Python."""
    ignore_files: list[Path] = []
    for root, dirs, files in os.walk("."):
        # Pular diretórios desnecessários
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d not in {"__pycache__", "node_modules"}
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    content = Path(file_path).read_text(encoding="utf-8")
                    if "# ignore" in content.lower():
                        ignore_files.append(file_path)
                except (OSError, ValueError, TypeError):
                    logger.exception("Error processing file %s", file_path)
                    continue

    return ignore_files


def generate_fix_commands(
    violations: list[dict[str, str]],
    ignore_files: list[Path],
) -> None:
    """Gera comandos para correção das violações."""
    if violations:
        files_to_backup: set[str] = set()
        for violation in violations:
            if "Renomear" in violation["action"]:
                files_to_backup.add(violation["file"])

        for _file_path in files_to_backup:
            pass

    if ignore_files:
        for _ignore_file in ignore_files:
            pass

    # Gerar script de correção
    script_path = Path("scripts/architecture/fix_violations.sh")
    script_path.parent.mkdir(parents=True, exist_ok=True)

    with Path(script_path).open("w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write("# Script gerado automaticamente para correção de violações\n\n")
        f.write("echo '🚀 Iniciando correção de violações arquiteturais...'\n\n")

        if violations:
            f.write("# Backup de arquivos com violações em flext-core\n")
            for violation in violations:
                if "Renomear" in violation["action"]:
                    files_to_backup.add(violation["file"])

            for file_path in files_to_backup:
                f.write(f"echo 'Fazendo backup de {file_path}'\n")
                f.write(f"mv {file_path} {file_path}.bak\n\n")

        f.write("echo '✅ Violações corrigidas! Revise os arquivos .bak criados.'\n")

    script_path.chmod(0o755)

    # Estatísticas finais
    total_issues: int = len(violations) + len(ignore_files)
    if total_issues == 0:
        pass


def main() -> None:
    """Função principal."""
    # Verificar se estamos no workspace correto
    if not Path("flext-core").exists():
        return

    # Executar análises
    violations: list[dict[str, str]] = analyze_flext_core_violations()
    ignore_files: list[Path] = analyze_ignore_comments()

    # Gerar relatório e comandos de correção
    generate_fix_commands(violations, ignore_files)


if __name__ == "__main__":
    main()
