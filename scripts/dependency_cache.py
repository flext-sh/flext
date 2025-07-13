#!/usr/bin/env python3
"""
Sistema de cache para melhorar performance do sync_dependencies.py
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional


class DependencyCache:
    """Cache para resultados de análise de dependências."""
    
    def __init__(self, cache_dir: Path | None = None):
        """Inicializa o cache."""
        self.cache_dir = cache_dir or Path.home() / ".cache" / "flext-deps"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "dependency_analysis.json"
        self.cache_data = self._load_cache()
        
    def _load_cache(self) -> dict[str, Any]:
        """Carrega cache do disco."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_cache(self):
        """Salva cache no disco."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar cache: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calcula hash de um arquivo."""
        try:
            content = file_path.read_bytes()
            return hashlib.sha256(content).hexdigest()[:16]
        except Exception:
            return ""
    
    def _get_project_hash(self, project: Path) -> str:
        """Calcula hash de um projeto baseado em seus arquivos Python."""
        hashes = []
        for py_file in sorted(project.rglob("*.py")):
            if "__pycache__" not in str(py_file):
                hashes.append(self._get_file_hash(py_file))
        
        combined = "".join(hashes)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def get_analysis(self, project: Path, cache_key: str) -> Optional[dict]:
        """Obtém análise do cache se ainda válida."""
        project_name = project.name
        project_hash = self._get_project_hash(project)
        
        if project_name in self.cache_data:
            cached = self.cache_data[project_name]
            
            # Verifica se o hash mudou
            if cached.get("hash") == project_hash:
                # Verifica idade do cache (24 horas)
                age = time.time() - cached.get("timestamp", 0)
                if age < 86400:  # 24 horas
                    return cached.get(cache_key)
        
        return None
    
    def set_analysis(self, project: Path, cache_key: str, data: dict):
        """Armazena análise no cache."""
        project_name = project.name
        project_hash = self._get_project_hash(project)
        
        if project_name not in self.cache_data:
            self.cache_data[project_name] = {}
        
        self.cache_data[project_name].update({
            "hash": project_hash,
            "timestamp": time.time(),
            cache_key: data
        })
        
        self._save_cache()
    
    def clear(self, project: Path | None = None):
        """Limpa cache de um projeto ou todo o cache."""
        if project:
            project_name = project.name
            if project_name in self.cache_data:
                del self.cache_data[project_name]
        else:
            self.cache_data = {}
        
        self._save_cache()
    
    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas do cache."""
        total_projects = len(self.cache_data)
        total_size = len(json.dumps(self.cache_data))
        
        ages = []
        for project_data in self.cache_data.values():
            if "timestamp" in project_data:
                age = time.time() - project_data["timestamp"]
                ages.append(age)
        
        avg_age = sum(ages) / len(ages) if ages else 0
        
        return {
            "total_projects": total_projects,
            "cache_size_bytes": total_size,
            "average_age_hours": avg_age / 3600,
            "cache_file": str(self.cache_file)
        }


# Instância global do cache
_cache_instance: Optional[DependencyCache] = None


def get_cache() -> DependencyCache:
    """Obtém instância global do cache."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DependencyCache()
    return _cache_instance


def clear_cache(project: Path | None = None):
    """Limpa o cache."""
    get_cache().clear(project)


def cache_stats():
    """Mostra estatísticas do cache."""
    stats = get_cache().get_stats()
    print("📊 ESTATÍSTICAS DO CACHE:")
    print(f"  Projetos em cache: {stats['total_projects']}")
    print(f"  Tamanho: {stats['cache_size_bytes'] / 1024:.1f} KB")
    print(f"  Idade média: {stats['average_age_hours']:.1f} horas")
    print(f"  Arquivo: {stats['cache_file']}")


if __name__ == "__main__":
    # Teste do cache
    cache_stats()