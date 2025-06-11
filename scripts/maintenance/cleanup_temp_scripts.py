#!/usr/bin/env python3
"""
Script de limpeza automática de scripts temporários.

Este script remove automaticamente scripts temporários antigos das pastas temp/
em todo o workspace.
"""

import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Adiciona o path do utils para importar validação
sys.path.append(str(Path(__file__).parent.parent / "utils"))
import structlog
from script_validation import find_workspace_root, validate_script_location

# Validação obrigatória de localização
validate_script_location()

logger = structlog.get_logger(__name__)


def find_temp_scripts(workspace_root: Path, max_age_days: int = 30) -> list[Path]:
    """
    Encontra scripts temporários que excedem a idade máxima.

    Args:
        workspace_root: Raiz do workspace
        max_age_days: Idade máxima em dias

    Returns:
        List[Path]: Lista de scripts para remoção
    """
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    old_scripts = []

    # Procura em todas as pastas temp
    temp_dirs = [
        workspace_root / "scripts" / "temp",
        *workspace_root.glob("*/scripts/temp"),
    ]

    for temp_dir in temp_dirs:
        if not temp_dir.exists():
            continue

        logger.info(f"Verificando pasta: {temp_dir}")

        for script_file in temp_dir.glob("*.py"):
            # Verifica idade do arquivo
            file_age = datetime.fromtimestamp(script_file.stat().st_mtime)

            if file_age < cutoff_date:
                old_scripts.append(script_file)

    return old_scripts


def analyze_script_content(script_file: Path) -> dict:
    """
    Analisa o conteúdo do script para extrair metadados.

    Args:
        script_file: Caminho do script

    Returns:
        dict: Metadados extraídos
    """
    try:
        content = script_file.read_text(encoding="utf-8")

        # Procura por padrões de data de limpeza
        cleanup_pattern = r"LIMPEZA AGENDADA:\s*(\d{4}-\d{2}-\d{2})"
        cleanup_match = re.search(cleanup_pattern, content)

        # Procura por objetivo/propósito
        purpose_pattern = r"Objetivo:\s*(.+)"
        purpose_match = re.search(purpose_pattern, content)

        return {
            "cleanup_date": cleanup_match.group(1) if cleanup_match else None,
            "purpose": purpose_match.group(1).strip() if purpose_match else None,
            "is_temp_template": "SCRIPT TEMPORÁRIO" in content,
        }
    except Exception as e:
        logger.warning(f"Erro ao analisar script {script_file}: {e}")
        return {}


def cleanup_temp_scripts(max_age_days: int = 30, dry_run: bool = False) -> None:
    """
    Remove scripts temporários antigos.

    Args:
        max_age_days: Idade máxima em dias para manter scripts
        dry_run: Se True, apenas mostra o que seria removido
    """
    workspace_root = find_workspace_root()

    logger.info(
        "Iniciando limpeza de scripts temporários",
        max_age_days=max_age_days,
        dry_run=dry_run,
        workspace_root=str(workspace_root),
    )

    old_scripts = find_temp_scripts(workspace_root, max_age_days)

    if not old_scripts:
        logger.info("Nenhum script temporário antigo encontrado")
        return

    logger.info(f"Encontrados {len(old_scripts)} scripts para limpeza")

    removed_count = 0
    for script_file in old_scripts:
        try:
            # Analisa conteúdo para logs mais informativos
            metadata = analyze_script_content(script_file)

            file_age = datetime.fromtimestamp(script_file.stat().st_mtime)
            age_days = (datetime.now() - file_age).days

            logger.info(
                "Script encontrado para remoção",
                file=str(script_file),
                age_days=age_days,
                purpose=metadata.get("purpose", "Não especificado"),
            )

            if not dry_run:
                script_file.unlink()
                logger.info(f"Script removido: {script_file}")
                removed_count += 1
            else:
                logger.info(f"[DRY RUN] Removeria: {script_file}")

        except Exception as e:
            logger.exception(f"Erro ao remover script {script_file}: {e}")

    if dry_run:
        logger.info(f"[DRY RUN] {len(old_scripts)} scripts seriam removidos")
    else:
        logger.info(f"Limpeza concluída: {removed_count} scripts removidos")


def main():
    """Função principal com interface CLI básica."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Limpa scripts temporários antigos do workspace"
    )
    parser.add_argument(
        "--max-age", type=int, default=30, help="Idade máxima em dias (padrão: 30)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas mostra o que seria removido, sem remover",
    )

    args = parser.parse_args()

    try:
        cleanup_temp_scripts(max_age_days=args.max_age, dry_run=args.dry_run)
    except Exception as e:
        logger.exception("Erro durante limpeza", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
