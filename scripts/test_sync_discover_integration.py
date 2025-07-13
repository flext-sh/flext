#!/usr/bin/env python3
"""
Teste de integração REAL para sync_dependencies.py --discover-missing
Verifica que a descoberta de dependências funciona corretamente.
"""

import subprocess
import sys
from pathlib import Path


def test_discover_missing():
    """Testa descoberta de dependências faltantes."""
    print("🧪 TESTE DE INTEGRAÇÃO: sync_dependencies.py --discover-missing")
    print("=" * 60)
    
    # Usa flext-web como projeto de teste (sabemos que tem pydantic_settings)
    test_project = Path("/home/marlonsc/flext/flext-web")
    
    if not test_project.exists():
        print("❌ Projeto de teste não encontrado!")
        return False
    
    # Executa sync_dependencies.py com --discover-missing
    cmd = [
        sys.executable,
        "/home/marlonsc/flext/scripts/sync_dependencies.py",
        "--projects", str(test_project),
        "--discover-missing",
        "--dry-run"  # Não modifica nada
    ]
    
    print(f"📍 Executando: {' '.join(cmd)}")
    print("⏳ Aguarde, pode demorar alguns segundos...")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 1 minuto máximo
        )
        
        print("\n📋 STDOUT:")
        print("-" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ STDERR:")
            print("-" * 40)
            print(result.stderr)
        
        # Verifica se encontrou imports não declarados
        if "imports não declarados" in result.stdout:
            print("\n✅ Script detectou imports não declarados!")
            
            # Verifica se o mapeamento funcionou
            if "pydantic-settings" in result.stdout and "pydantic_settings" in result.stdout:
                print("✅ Mapeamento pydantic_settings -> pydantic-settings funcionou!")
            else:
                print("⚠️ Mapeamento pode não ter funcionado corretamente")
                
        else:
            print("\n⚠️ Nenhum import não declarado foi detectado")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout! Script demorou mais de 60 segundos")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        return False


def test_analyze_who_blocks():
    """Testa script de análise de bloqueios."""
    print("\n\n🧪 TESTE: analyze_who_blocks_updates.py")
    print("=" * 60)
    
    cmd = [
        sys.executable,
        "/home/marlonsc/flext/scripts/analyze_who_blocks_updates.py",
        "--workspace", "/home/marlonsc/flext"
    ]
    
    print(f"📍 Executando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("\n📋 Resultado:")
        print("-" * 40)
        print(result.stdout)
        
        if "QUEM ESTÁ SEGURANDO ATUALIZAÇÕES" in result.stdout:
            print("\n✅ Script de análise funcionou!")
            
            # Verifica se encontrou bloqueadores
            if "Projetos bloqueando:" in result.stdout:
                print("✅ Identificou projetos que bloqueiam atualizações!")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")
        return False


def main():
    """Executa todos os testes."""
    success = True
    
    # Teste 1: Descoberta de dependências
    if not test_discover_missing():
        success = False
        
    # Teste 2: Análise de bloqueios
    if not test_analyze_who_blocks():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TODOS OS TESTES PASSARAM!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())