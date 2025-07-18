#!/usr/bin/env python3
"""Sistema de cache para análise de dependências."""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

CACHE_DIR = Path.home() / ".cache" / "flext_deps"
CACHE_FILE = CACHE_DIR / "dependency_cache.json"
CACHE_TTL = timedelta(hours=24)  # Cache válido por 24 horas


def ensure_cache_dir() -> None:
    """Garante que o diretório de cache existe."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_project_hash(project: Path) -> str:
    """Gera hash único para o estado do projeto."""
    # Hash baseado em pyproject.toml e arquivos Python
    hasher = hashlib.md5()

    # Hash do pyproject.toml
    pyproject = project / "pyproject.toml"
    if pyproject.exists():
        hasher.update(pyproject.read_bytes())

    # Hash dos arquivos Python (apenas modificação time para performance)
    for py_file in project.rglob("*.py"):
        if ".venv" not in str(py_file) and "__pycache__" not in str(py_file):
            stat = py_file.stat()
            hasher.update(f"{py_file}:{stat.st_mtime}".encode())

    return hasher.hexdigest()


def load_cache() -> dict[str, Any]:
    """Carrega cache do disco."""
    if not CACHE_FILE.exists():
        return {}

    try:
        with Path(CACHE_FILE).open(encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(cache: dict[str, Any]) -> None:
    """Salva cache no disco."""
    ensure_cache_dir()

    with Path(CACHE_FILE).open("w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, default=str)


def get_cache() -> "DependencyCache":
    """Retorna instância do cache."""
    return DependencyCache()


def clear_cache() -> None:
    """Limpa todo o cache."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    print(f"✅ Cache limpo: {CACHE_FILE}")


def cache_stats() -> None:
    """Mostra estatísticas do cache."""
    if not CACHE_FILE.exists():
        print("📊 Cache vazio")
        return

    cache = load_cache()
    total_entries = len(cache)

    if total_entries == 0:
        print("📊 Cache vazio")
        return

    # Conta entradas válidas e expiradas
    now = datetime.now()
    valid = 0
    expired = 0

    for entry in cache.values():
        if "timestamp" in entry:
            timestamp = datetime.fromisoformat(entry["timestamp"])
            if now - timestamp < CACHE_TTL:
                valid += 1
            else:
                expired += 1

    size_kb = CACHE_FILE.stat().st_size / 1024

    print("📊 Estatísticas do Cache:")
    print(f"   Total de entradas: {total_entries}")
    print(f"   Entradas válidas: {valid}")
    print(f"   Entradas expiradas: {expired}")
    print(f"   Tamanho: {size_kb:.1f} KB")
    print(f"   Localização: {CACHE_FILE}")


class DependencyCache:
    """Gerenciador de cache para análise de dependências."""

    def __init__(self):
        self.cache = load_cache()
        self.hits = 0
        self.misses = 0

    def get_project_analysis(self, project: Path) -> dict[str, Any] | None:
        """Obtém análise cacheada do projeto."""
        project_hash = get_project_hash(project)
        cache_key = f"{project.name}:{project_hash}"

        if cache_key in self.cache:
            entry = self.cache[cache_key]
            # Verifica se não expirou
            timestamp = datetime.fromisoformat(entry["timestamp"])
            if datetime.now() - timestamp < CACHE_TTL:
                self.hits += 1
                return entry["data"]

        self.misses += 1
        return None

    def set_project_analysis(self, project: Path, data: dict[str, Any]) -> None:
        """Armazena análise do projeto no cache."""
        project_hash = get_project_hash(project)
        cache_key = f"{project.name}:{project_hash}"

        self.cache[cache_key] = {"timestamp": datetime.now().isoformat(), "data": data}

        save_cache(self.cache)

    def get_stats(self) -> dict[str, int]:
        """Retorna estatísticas de uso do cache."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses)
            if (self.hits + self.misses) > 0
            else 0,
        }
