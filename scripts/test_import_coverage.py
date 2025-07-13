#!/usr/bin/env python3
"""
Testa se a detecção de imports já cobertos está funcionando.
"""

import subprocess
import sys
from pathlib import Path


def test_coverage():
    """Testa a cobertura de imports."""
    
    print("🧪 TESTANDO DETECÇÃO DE IMPORTS JÁ COBERTOS")
    print("=" * 60)
    
    # Teste 1: Com discover_missing_deps.py (referência)
    print("\n1️⃣ Teste com discover_missing_deps.py:")
    cmd1 = [
        sys.executable,
        "/home/marlonsc/flext/scripts/discover_missing_deps.py",
        "flext-web"
    ]
    
    result1 = subprocess.run(cmd1, capture_output=True, text=True)
    print(result1.stdout)
    
    # Teste 2: Com sync_dependencies.py --discover-missing
    print("\n2️⃣ Teste com sync_dependencies.py --discover-missing:")
    cmd2 = [
        sys.executable,
        "/home/marlonsc/flext/scripts/sync_dependencies.py",
        "--projects", "flext-web",
        "--discover-missing",
        "--dry-run"
    ]
    
    result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
    
    # Filtra só as linhas relevantes
    lines = result2.stdout.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in [
            'descobert', 'found', 'missing', 'google', 'grpc', 
            'protobuf', 'dependencies', 'imports'
        ]):
            print(line)
    
    # Análise específica
    print("\n📊 ANÁLISE:")
    print("- discover_missing_deps.py encontrou 'google' e 'grpc'")
    print("- Estes vêm de 'protobuf' e 'grpcio' que JÁ ESTÃO instalados")
    print("- sync_dependencies.py DEVE filtrar estes imports")
    
    # Verifica se protobuf e grpcio estão instalados
    print("\n🔍 Verificando se protobuf e grpcio estão no pyproject.toml:")
    pyproject = Path("/home/marlonsc/flext/flext-web/pyproject.toml")
    if pyproject.exists():
        content = pyproject.read_text()
        if "protobuf" in content:
            print("✅ protobuf está instalado")
        if "grpcio" in content:
            print("✅ grpcio está instalado")
    
    return 0


if __name__ == "__main__":
    sys.exit(test_coverage())