#!/usr/bin/env python3
"""
Teste real da descoberta de imports do sync_dependencies.py
Objetivo: Testar se a função analyze_and_fix_missing_imports funciona
"""

import ast
import sys
from pathlib import Path

# Importa diretamente as funções do script
sys.path.insert(0, str(Path(__file__).parent))
from sync_dependencies import (
    analyze_and_fix_missing_imports,
    analyze_imports_intelligently,
    get_stdlib_modules,
)


def test_analyze_imports():
    """Testa análise de imports em arquivo Python."""
    print("=== TESTE 1: Análise de Imports Python ===")

    # Cria arquivo temporário com imports
    test_file = Path("/tmp/test_imports.py")
    test_content = """
import os
import sys
from pathlib import Path
import requests  # Terceiro
import pandas as pd  # Terceiro
from typing import Dict, List
import numpy  # Terceiro
try:
    import optional_lib  # Opcional
except ImportError:
    pass
"""
    test_file.write_text(test_content)

    # Analisa imports
    stdlib = get_stdlib_modules()
    imports = analyze_imports_intelligently(test_file, stdlib)

    print(f"Imports encontrados: {imports}")

    # Verifica se detectou corretamente
    expected = {"requests", "pandas", "numpy", "optional_lib"}
    if imports == expected:
        print("✓ SUCESSO: Detectou todos os imports de terceiros")
        return True
    print(f"✗ FALHA: Esperado {expected}, encontrado {imports}")
    return False


def test_missing_import_detection():
    """Testa detecção de imports faltantes via ModuleNotFoundError."""
    print("\n=== TESTE 2: Detecção de Imports Faltantes ===")

    # Cria projeto temporário
    project_dir = Path("/tmp/test_project")
    project_dir.mkdir(exist_ok=True)
    src_dir = project_dir / "src" / "myproject"
    src_dir.mkdir(parents=True, exist_ok=True)

    # Cria __init__.py
    (src_dir / "__init__.py").write_text("")

    # Cria arquivo com import faltante
    test_py = src_dir / "test.py"
    test_py.write_text("""
import requests  # Este import vai falhar se não estiver instalado
import boto3     # Este também

def main():
    print("Test")
""")

    # Analisa imports faltantes
    try:
        missing = analyze_and_fix_missing_imports(project_dir)
        print(f"Imports faltantes detectados: {missing}")

        # Verifica se detectou algo
        if missing.get("runtime") or missing.get("test"):
            print("✓ SUCESSO: Detectou imports faltantes")
            return True
        print("✗ FALHA: Não detectou nenhum import faltante")
        return False

    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False


def test_ast_parsing():
    """Testa parsing AST direto."""
    print("\n=== TESTE 3: AST Parsing ===")

    code = """
import requests
from flask import Flask
import pandas as pd

try:
    import optional_module
except ImportError:
    pass

def dynamic_import():
    __import__('dynamic_module')
    import importlib
    importlib.import_module('another_module')
"""

    try:
        tree = ast.parse(code)
        imports = set()

        # Percorre a AST
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                # Detecta __import__ e importlib.import_module
                if isinstance(node.func, ast.Name) and node.func.id == "__import__":
                    if node.args and isinstance(node.args[0], ast.Constant):
                        imports.add(node.args[0].value)
                elif isinstance(node.func, ast.Attribute):
                    if (node.func.attr == "import_module" and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id == "importlib"):
                        if node.args and isinstance(node.args[0], ast.Constant):
                            imports.add(node.args[0].value)

        print(f"Imports encontrados via AST: {imports}")

        expected = {"requests", "flask", "pandas", "optional_module",
                   "dynamic_module", "importlib", "another_module"}

        if imports == expected:
            print("✓ SUCESSO: AST parsing funcionou corretamente")
            return True
        print(f"✗ FALHA: Esperado {expected}, encontrado {imports}")
        return False

    except Exception as e:
        print(f"✗ ERRO no AST parsing: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("TESTE DE DESCOBERTA DE IMPORTS")
    print("=" * 50)

    results = []

    # Teste 1: Análise de imports
    results.append(test_analyze_imports())

    # Teste 2: Detecção de faltantes
    results.append(test_missing_import_detection())

    # Teste 3: AST parsing
    results.append(test_ast_parsing())

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
