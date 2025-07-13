#!/usr/bin/env python3
"""
Testa os diferentes modos de descoberta de dependências.
"""

import subprocess
import sys
from pathlib import Path


def run_test(cmd, description):
    """Executa um teste e mostra resultado."""
    print(f"\n{'=' * 60}")
    print(f"🧪 TESTE: {description}")
    print(f"📍 Comando: {' '.join(cmd)}")
    print('=' * 60)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Mostra apenas linhas relevantes
        lines = result.stdout.split('\n')
        relevant = False
        for line in lines:
            if any(keyword in line for keyword in [
                'flext-web', 'descobert', 'depend', 'install', 
                'aplicar', 'apply', '💡', '📋', '✅', '❌'
            ]):
                print(line)
                relevant = True
            elif relevant and line.strip() == '':
                relevant = False
                
        if result.stderr:
            print(f"\n⚠️ STDERR: {result.stderr}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout após 30 segundos!")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def main():
    """Testa diferentes modos."""
    
    print("🔍 TESTANDO MODOS DE DESCOBERTA DE DEPENDÊNCIAS")
    
    base_cmd = [
        sys.executable,
        "/home/marlonsc/flext/scripts/sync_dependencies.py",
        "--projects", "flext-web"
    ]
    
    tests = [
        # Teste 1: Descoberta sem --apply (não deve instalar)
        (
            base_cmd + ["--discover-missing", "--dry-run"],
            "Descoberta com --dry-run (NÃO deve instalar)"
        ),
        
        # Teste 2: Descoberta com --apply (DEVE instalar)
        (
            base_cmd + ["--discover-missing", "--apply", "--dry-run"],
            "Descoberta com --apply --dry-run (deve mostrar o que instalaria)"
        ),
        
        # Teste 3: Modo normal com dry-run
        (
            base_cmd + ["--dry-run"],
            "Modo normal com --dry-run (não deve instalar descobertas)"
        ),
    ]
    
    results = []
    for cmd, desc in tests:
        success = run_test(cmd, desc)
        results.append((desc, success))
    
    # Resumo
    print(f"\n{'=' * 60}")
    print("📊 RESUMO DOS TESTES:")
    print('=' * 60)
    
    for desc, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status}: {desc}")
    
    # Teste específico para verificar se mostra corretamente
    print(f"\n{'=' * 60}")
    print("🔍 VERIFICAÇÃO DETALHADA:")
    
    # Usa o discover_missing_deps.py para comparar
    cmd = [
        sys.executable,
        "/home/marlonsc/flext/scripts/discover_missing_deps.py",
        "flext-web"
    ]
    
    print(f"Comparando com discover_missing_deps.py:")
    subprocess.run(cmd)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())