#!/usr/bin/env python3
"""Analisador Simples de Violações Arquiteturais - FLEXT Workspace.

Identifica imports problemáticos e módulos em camadas incorretas.
"""

import ast
import os
import re
from pathlib import Path

from flext_core import get_logger

logger = get_logger(__name__)


def analyze_flext_core_violations() -> list[dict[str, str]]:
    """Analisa violações específicas em flext-core."""
    print("🔍 Analisando violações em flext-core...")

    flext_core_path = Path("flext-core/src")
    if not flext_core_path.exists():
        print("❌ Diretório flext-core/src não encontrado")
        return []

    violations: list[dict[str, str]] = []
    specific_patterns = [
        r"meltano",
        r"oracle",
        r"ldap",
        r"singer",
        r"algar",
        r"gruponos",
    ]

    for py_file in flext_core_path.rglob("*.py"):
        if py_file.name == "__init__.py" or py_file.name.endswith(".bak"):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            # Usar word boundaries para evitar matches dentro de outras palavras
            violations.extend({
                            "file": str(py_file),
                            "pattern": pattern,
                            "action": f"Renomear {py_file.name} para {py_file.name}.bak",
                        } for pattern in specific_patterns if re.search(r"\b" + pattern + r"\b", content, re.IGNORECASE))

            # Analisar imports AST
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_name = alias.name.split(".")[0]
                            if any(
                                p in import_name.lower()
                                for p in ["meltano", "oracle", "algar", "gruponos"]
                            ):
                                violations.append(
                                    {
                                        "file": str(py_file),
                                        "pattern": f"import {import_name}",
                                        "action": f"Remover import violador em {py_file.name}",
                                    },
                                )
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        import_name = node.module.split(".")[0]
                        if any(
                            p in import_name.lower()
                            for p in ["meltano", "oracle", "algar", "gruponos"]
                        ):
                            violations.append(
                                {
                                    "file": str(py_file),
                                    "pattern": f"from {node.module}",
                                    "action": f"Remover import violador em {py_file.name}",
                                },
                            )
            except SyntaxError:
                print(f"⚠️  Erro de sintaxe em {py_file}")

        except (OSError, ValueError, TypeError) as e:
            print(f"⚠️  Erro ao analisar {py_file}: {e}")

    return violations


def analyze_ignore_comments() -> list[Path]:
    """Encontra todos os comentários # ignore nos arquivos Python."""
    print("🔍 Procurando comentários # ignore...")

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
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        if "# ignore" in content.lower():
                            ignore_files.append(file_path)
                except (OSError, ValueError, TypeError) as e:
                    logger.exception(f"Error processing file {file_path}: {e}")
                    continue

    return ignore_files


def generate_fix_commands(
    violations: list[dict[str, str]],
    ignore_files: list[Path],
) -> None:
    """Gera comandos para correção das violações."""
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO DE VIOLAÇÕES ENCONTRADAS")
    print("=" * 60)

    if violations:
        print(f"\n🚨 VIOLAÇÕES EM FLEXT-CORE ({len(violations)} encontradas):")

        files_to_backup: set[str] = set()
        for violation in violations:
            print(f"  📁 {violation['file']}")
            print(f"     Padrão: {violation['pattern']}")
            print(f"     Ação: {violation['action']}")
            if "Renomear" in violation["action"]:
                files_to_backup.add(violation["file"])

        print("\n💾 COMANDOS PARA BACKUP DE ARQUIVOS PROBLEMÁTICOS:")
        for file_path in files_to_backup:
            print(f"mv {file_path} {file_path}.bak")

    if ignore_files:
        print(f"\n📝 ARQUIVOS COM # IGNORE ({len(ignore_files)} encontrados):")
        for ignore_file in ignore_files:
            print(f"  {ignore_file}")

    # Gerar script de correção
    script_path = Path("scripts/architecture/fix_violations.sh")
    script_path.parent.mkdir(parents=True, exist_ok=True)

    with open(script_path, "w", encoding="utf-8") as f:
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
    print(f"\n💾 Script de correção gerado: {script_path}")

    # Estatísticas finais
    total_issues: int = len(violations) + len(ignore_files)
    if total_issues == 0:
        print("\n✅ Nenhuma violação arquitetural crítica encontrada!")
    else:
        print(f"\n📊 RESUMO: {total_issues} problemas encontrados")
        print(f"  - {len(violations)} violações em flext-core")
        print(f"  - {len(ignore_files)} arquivos com # ignore")


def main() -> None:
    """Função principal."""
    print("🏗️  ANALISADOR SIMPLES DE VIOLAÇÕES ARQUITETURAIS")
    print(f"📁 Diretório: {Path.cwd()}")

    # Verificar se estamos no workspace correto
    if not Path("flext-core").exists():
        print("❌ Este script deve ser executado na raiz do workspace FLEXT")
        return

    # Executar análises
    violations: list[dict[str, str]] = analyze_flext_core_violations()
    ignore_files: list[Path] = analyze_ignore_comments()

    # Gerar relatório e comandos de correção
    generate_fix_commands(violations, ignore_files)

    print("\n✅ Análise concluída!")


if __name__ == "__main__":
    main()
