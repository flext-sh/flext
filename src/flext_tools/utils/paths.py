"""Utilitários para manipulação de caminhos."""

from pathlib import Path

# Diretórios que devem ser ignorados na análise
IGNORE_DIRS: set[str] = {
    # Arquivos e backups
    "archive",
    ".archive",
    "backup",
    "old",
    "deprecated",
    "legacy",
    "temp",
    "tmp",
    # Controle de versão
    ".git",
    ".svn",
    ".hg",
    ".bzr",
    # Python
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".coverage",
    "htmlcov",
    ".hypothesis",
    # Build e distribuição
    "build",
    "dist",
    "*.egg-info",
    "_build",
    "wheelhouse",
    # Node.js
    "node_modules",
    ".npm",
    ".yarn",
    # IDEs
    ".idea",
    ".vscode",
    ".vs",
    "*.swp",
    "*.swo",
    # Outros
    "venv",
    ".venv",
    "env",
    ".env",
    "virtualenv",
}


def should_ignore_path(path: Path) -> bool:
    """Verifica se um caminho deve ser ignorado na análise."""
    parts = path.parts
    return any(ignore_dir in parts for ignore_dir in IGNORE_DIRS)
