#!/usr/bin/env python3
"""
Teste mínimo para validar funcionalidade core do sync_dependencies.py
OBJETIVO: Verificar se consegue descobrir e adicionar dependência faltante
"""

import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


def create_test_project():
    """Cria projeto Python mínimo com import faltante."""
    test_dir = Path(tempfile.mkdtemp(prefix="test_sync_"))

    # Cria estrutura mínima
    src_dir = test_dir / "src" / "testproject"
    src_dir.mkdir(parents=True)

    # pyproject.toml mínimo (sem requests)
    pyproject = test_dir / "pyproject.toml"
    pyproject_content = """
[tool.poetry]
name = "testproject"
version = "0.1.0"
description = "Test project"
authors = ["Test <test@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
    pyproject.write_text(pyproject_content.strip())

    # __init__.py vazio
    (src_dir / "__init__.py").write_text("")

    # main.py com import faltante
    main_py = src_dir / "main.py"
    main_content = '''
"""Módulo de teste com import faltante."""

import requests  # Esta biblioteca NÃO está no pyproject.toml

def fetch_data():
    """Função que usa requests."""
    response = requests.get("https://api.example.com")
    return response.json()

if __name__ == "__main__":
    print("Test project")
'''
    main_py.write_text(main_content.strip())

    return test_dir


def test_discovery_only():
    """Testa apenas descoberta de imports sem adicionar."""
    print("=== TESTE 1: Descoberta de Imports ===")

    test_dir = create_test_project()
    print(f"Projeto teste criado em: {test_dir}")

    try:
        # Executa sync_dependencies em modo dry-run
        cmd = [
            sys.executable,
            "sync_dependencies.py",
            "--projects", str(test_dir),
            "--dry-run"
        ]

        print(f"Executando: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            check=False, cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=60
        )

        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        # Verifica se detectou 'requests' como faltante
        if "requests" in result.stdout.lower():
            print("✓ SUCESSO: Detectou 'requests' como dependência faltante")
            return True
        print("✗ FALHA: Não detectou 'requests' como dependência faltante")
        return False

    except subprocess.TimeoutExpired:
        print("✗ FALHA: Script deu timeout (>60s)")
        return False
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_poetry_add():
    """Testa se poetry add realmente funciona."""
    print("\n=== TESTE 2: Poetry Add ===")

    test_dir = create_test_project()
    print(f"Projeto teste criado em: {test_dir}")

    try:
        # Tenta adicionar requests com poetry
        cmd = ["poetry", "add", "requests", "--dry-run"]
        print(f"Executando: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            check=False, cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=30
        )

        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

        if result.returncode == 0:
            print("✓ Poetry add --dry-run funcionou")

            # Agora testa sem --dry-run
            cmd_real = ["poetry", "add", "requests"]
            print(f"\nExecutando: {' '.join(cmd_real)}")

            result_real = subprocess.run(
                cmd_real,
                check=False, cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result_real.returncode == 0:
                # Verifica se foi adicionado ao pyproject.toml
                with open(test_dir / "pyproject.toml", "rb") as f:
                    data = tomllib.load(f)

                if "requests" in data.get("tool", {}).get("poetry", {}).get("dependencies", {}):
                    print("✓ SUCESSO: 'requests' foi adicionado ao pyproject.toml")
                    return True
                print("✗ FALHA: 'requests' não foi encontrado no pyproject.toml após poetry add")
                return False
            print(f"✗ FALHA: poetry add retornou erro {result_real.returncode}")
            return False
        print(f"✗ FALHA: poetry add --dry-run retornou erro {result.returncode}")
        return False

    except subprocess.TimeoutExpired:
        print("✗ FALHA: Comando deu timeout")
        return False
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def main():
    """Executa todos os testes."""
    print("TESTE MÍNIMO - sync_dependencies.py")
    print("=" * 50)

    # Verifica se poetry está disponível
    try:
        subprocess.run(["poetry", "--version"], capture_output=True, check=True)
    except:
        print("ERRO: Poetry não está instalado ou não está no PATH")
        return 1

    # Executa testes
    results = []

    # Teste 1: Descoberta
    results.append(test_discovery_only())

    # Teste 2: Poetry add
    results.append(test_poetry_add())

    # Resumo
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES:")
    print(f"Testes executados: {len(results)}")
    print(f"Sucessos: {sum(results)}")
    print(f"Falhas: {len(results) - sum(results)}")

    if all(results):
        print("\n✓ TODOS OS TESTES PASSARAM")
        return 0
    print("\n✗ ALGUNS TESTES FALHARAM")
    return 1


if __name__ == "__main__":
    sys.exit(main())
