#!/usr/bin/env python3
"""
Teste específico para verificar mapeamento pydantic_settings -> pydantic-settings
"""

import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


def create_test_project_with_pydantic_settings():
    """Cria projeto com import de pydantic_settings."""
    test_dir = Path(tempfile.mkdtemp(prefix="test_pydantic_"))
    
    # Estrutura do projeto
    src_dir = test_dir / "src" / "myproject"
    src_dir.mkdir(parents=True)
    
    # pyproject.toml sem pydantic-settings
    pyproject = test_dir / "pyproject.toml"
    pyproject_content = """
[tool.poetry]
name = "myproject"
version = "0.1.0"
description = "Test project"
authors = ["Test <test@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
pydantic = "^2.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
    pyproject.write_text(pyproject_content.strip())
    
    # __init__.py
    (src_dir / "__init__.py").write_text("")
    
    # config.py com import de pydantic_settings
    config_py = src_dir / "config.py"
    config_content = '''
"""Configuração do projeto."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Configurações da aplicação."""
    
    app_name: str = "MyApp"
    debug: bool = False
    
    class Config:
        env_prefix = "MYAPP_"


settings = AppSettings()
'''
    config_py.write_text(config_content.strip())
    
    return test_dir


def test_pydantic_settings_mapping():
    """Testa se pydantic_settings é mapeado para pydantic-settings."""
    print("=== TESTE: Mapeamento pydantic_settings -> pydantic-settings ===\n")
    
    test_dir = create_test_project_with_pydantic_settings()
    print(f"Projeto teste criado em: {test_dir}")
    
    try:
        # 1. Descoberta
        print("\n1. Testando descoberta...")
        cmd_discover = [
            sys.executable,
            "scripts/discover_missing_deps.py",
            str(test_dir),
            "--dry-run"
        ]
        
        result = subprocess.run(
            cmd_discover,
            check=False, cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        print(f"Return code: {result.returncode}")
        
        if "pydantic_settings" in result.stdout:
            print("✓ Detectou pydantic_settings como faltante")
        else:
            print("✗ NÃO detectou pydantic_settings")
            print(f"Output:\n{result.stdout}")
            return False
            
        # 2. Aplicação com mapeamento
        print("\n2. Testando aplicação com mapeamento...")
        cmd_apply = [
            sys.executable,
            "scripts/discover_missing_deps.py",
            str(test_dir),
            "--apply"
        ]
        
        result_apply = subprocess.run(
            cmd_apply,
            check=False, cwd=Path.cwd(),
            capture_output=True,
            text=True
        )
        
        print(f"Return code: {result_apply.returncode}")
        
        # Verifica se usou o nome correto
        if "poetry add pydantic-settings" in result_apply.stdout:
            print("✓ Usou nome correto: pydantic-settings")
        else:
            print("✗ NÃO usou nome correto")
            print(f"Output:\n{result_apply.stdout}")
            return False
            
        # 3. Verifica pyproject.toml
        print("\n3. Verificando pyproject.toml...")
        with open(test_dir / "pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            
        deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
        
        if "pydantic-settings" in deps:
            print("✓ pydantic-settings foi adicionado ao pyproject.toml")
            print(f"  Versão: {deps['pydantic-settings']}")
            return True
        else:
            print("✗ pydantic-settings NÃO foi adicionado")
            print(f"  Dependências encontradas: {list(deps.keys())}")
            return False
            
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_sync_dependencies_mapping():
    """Testa mapeamento no sync_dependencies.py."""
    print("\n=== TESTE: Mapeamento no sync_dependencies.py ===\n")
    
    test_dir = create_test_project_with_pydantic_settings()
    print(f"Projeto teste criado em: {test_dir}")
    
    try:
        cmd = [
            sys.executable,
            "scripts/sync_dependencies.py",
            "--projects", str(test_dir),
            "--discover-missing",
            "--dry-run"
        ]
        
        print(f"Executando: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            check=False, cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        
        # Procura por menções de pydantic-settings (nome correto)
        if "pydantic-settings" in result.stdout or "pydantic-settings" in result.stderr:
            print("✓ sync_dependencies.py usa nome correto: pydantic-settings")
            return True
        else:
            print("✗ sync_dependencies.py não mencionou pydantic-settings")
            print(f"Output (primeiras 500 chars):\n{result.stdout[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Timeout no sync_dependencies.py")
        return False
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def main():
    """Executa todos os testes."""
    print("TESTE DE MAPEAMENTO: pydantic_settings -> pydantic-settings")
    print("=" * 60)
    
    results = []
    
    # Teste 1: discover_missing_deps.py
    results.append(test_pydantic_settings_mapping())
    
    # Teste 2: sync_dependencies.py
    results.append(test_sync_dependencies_mapping())
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO:")
    print(f"Testes executados: {len(results)}")
    print(f"Sucessos: {sum(results)}")
    print(f"Falhas: {len(results) - sum(results)}")
    
    if all(results):
        print("\n✓ TODOS OS TESTES PASSARAM")
        print("O mapeamento pydantic_settings -> pydantic-settings está funcionando!")
        return 0
    else:
        print("\n✗ ALGUNS TESTES FALHARAM")
        return 1


if __name__ == "__main__":
    sys.exit(main())