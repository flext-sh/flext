#!/usr/bin/env python3
"""
Utilitário para validação de localização de scripts.

Este módulo fornece funções para validar que scripts estão nas pastas corretas
conforme as regras do workspace.
"""

import subprocess
import sys
from pathlib import Path


def find_workspace_root() -> Path:
    """
    Encontra a raiz do workspace usando git ou marcadores de projeto.

    Returns:
        Path: Caminho para a raiz do workspace
    """
    current = Path.cwd()

    # Tenta usar git para encontrar a raiz
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        pass

    # Fallback: procura por marcadores do workspace
    for parent in [current] + list(current.parents):
        markers = ["pyproject.toml", ".workspace", "Makefile", ".git"]
        if any((parent / marker).exists() for marker in markers):
            return parent

    return current


def validate_script_location(script_file: Path | None = None) -> None:
    """
    Valida se o script está na pasta correta.

    Args:
        script_file: Caminho do script. Se None, usa __file__ do caller

    Raises:
        RuntimeError: Se o script não estiver na pasta correta
    """
    if script_file is None:
        # Obtém o arquivo do script que chamou esta função
        import inspect

        frame = inspect.currentframe().f_back
        script_file = Path(frame.f_globals["__file__"]).resolve()

    workspace_root = find_workspace_root()

    # Define pastas válidas para scripts
    valid_script_patterns = [
        workspace_root / "scripts",
        workspace_root / "*/scripts",
    ]

    # Verifica se está em uma pasta válida
    is_valid = False
    for pattern in valid_script_patterns:
        if str(pattern).endswith("*/scripts"):
            # Para padrões glob, verifica manualmente
            potential_dirs = workspace_root.glob("*/scripts")
            for script_dir in potential_dirs:
                try:
                    script_file.relative_to(script_dir)
                    is_valid = True
                    break
                except ValueError:
                    continue
        else:
            # Para pastas específicas
            try:
                script_file.relative_to(pattern)
                is_valid = True
                break
            except ValueError:
                continue

    if not is_valid:
        error_msg = (
            f"ERRO: Script deve estar em uma pasta 'scripts/'\n"
            f"Localização atual: {script_file}\n"
            f"Localizações válidas:\n"
            f"  - {workspace_root}/scripts/\n"
            f"  - {workspace_root}/<projeto>/scripts/\n"
            f"\nMova o script para uma dessas pastas antes de executar."
        )
        raise RuntimeError(error_msg)


def get_script_category(script_file: Path) -> str:
    """
    Determina a categoria do script baseada em sua localização.

    Args:
        script_file: Caminho do script

    Returns:
        str: Categoria do script (temp, automation, maintenance, etc.)
    """
    workspace_root = find_workspace_root()
    min_parts_for_category = 2  # Constante para evitar magic value

    try:
        relative_path = script_file.relative_to(workspace_root)
        parts = relative_path.parts

        if len(parts) >= min_parts_for_category and parts[-2] in {
            "temp",
            "automation",
            "maintenance",
            "deployment",
            "testing",
            "utils",
        }:
            return parts[-2]
    except ValueError:
        return "unknown"
    else:
        return "general"


def check_all_scripts_location() -> list[Path]:
    """
    Verifica a localização de todos os scripts Python no workspace.

    Returns:
        list[Path]: Lista de scripts em localização incorreta
    """
    workspace_root = find_workspace_root()
    invalid_scripts = []

    # Encontra todos os arquivos Python
    for python_file in workspace_root.rglob("*.py"):
        # Ignora arquivos em pastas especiais
        relative_path = python_file.relative_to(workspace_root)
        parts = relative_path.parts

        # Pula pastas que não devem conter scripts
        skip_dirs = {
            ".venv",
            "venv",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "src",
            "tests",
            "test",
            "node_modules",
            ".git",
        }

        if any(part.startswith(".") or part in skip_dirs for part in parts):
            continue

        # Verifica se está em uma pasta de scripts válida
        try:
            validate_script_location(python_file)
        except RuntimeError:
            invalid_scripts.append(python_file)

    return invalid_scripts


if __name__ == "__main__":
    """Executa verificação de todos os scripts quando executado diretamente."""
    import structlog

    logger = structlog.get_logger(__name__)

    logger.info("Verificando localização de scripts no workspace...")

    invalid_scripts = check_all_scripts_location()

    if invalid_scripts:
        logger.error(
            "Scripts em localização incorreta encontrados", count=len(invalid_scripts)
        )

        for script in invalid_scripts:
            print(f"❌ {script}")

        print("\nMova estes scripts para as pastas apropriadas:")
        print("  - scripts/ (workspace-level)")
        print("  - <projeto>/scripts/ (flx_project-level)")

        sys.exit(1)
    else:
        logger.info("Todos os scripts estão nas pastas corretas! ✅")
        sys.exit(0)
