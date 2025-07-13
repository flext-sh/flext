#!/usr/bin/env python3
"""
Teste real: procura projetos que usam pydantic_settings mas não têm declarado
"""

import subprocess
import sys
from pathlib import Path


def check_project_for_pydantic_settings(project: Path) -> tuple[bool, bool]:
    """
    Verifica se projeto usa pydantic_settings e se está declarado.
    Retorna: (usa_pydantic_settings, tem_declarado)
    """
    # Verifica se usa pydantic_settings
    uses_pydantic_settings = False
    
    # Procura em arquivos Python
    py_files = list(project.rglob("*.py"))
    for py_file in py_files:
        # Pula testes e arquivos temporários
        if any(part in py_file.parts for part in ["tests", "test", "__pycache__", ".venv"]):
            continue
            
        try:
            content = py_file.read_text(encoding="utf-8")
            if "from pydantic_settings" in content or "import pydantic_settings" in content:
                uses_pydantic_settings = True
                print(f"    📄 Usa em: {py_file.relative_to(project)}")
        except Exception:
            pass
    
    # Verifica se está declarado
    has_declared = False
    pyproject = project / "pyproject.toml"
    
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            if "pydantic-settings" in content or "pydantic_settings" in content:
                has_declared = True
        except Exception:
            pass
    
    return uses_pydantic_settings, has_declared


def main():
    """Função principal."""
    print("🔍 VERIFICANDO PROJETOS QUE USAM pydantic_settings SEM DECLARAR")
    print("=" * 60)
    
    workspace = Path.cwd()
    projects_missing = []
    
    # Lista todos os projetos FLEXT
    flext_projects = [
        "flext-core", "flext-auth", "flext-api", "flext-grpc", "flext-web",
        "flext-cli", "flext-plugin", "flext-meltano", "flext-observability",
        "flext-ldap", "flext-quality", "flext-db-oracle",
        "flext-tap-ldap", "flext-tap-oracle-oic", "flext-tap-oracle-wms",
        "flext-target-ldap", "flext-target-oracle", "flext-target-oracle-oic",
        "flext-target-oracle-wms", "flext-dbt-ldap", "flext-oracle-oic-ext",
    ]
    
    for project_name in flext_projects:
        project_path = workspace / project_name
        
        if not project_path.exists():
            continue
            
        print(f"\n📁 Verificando: {project_name}")
        
        uses, declared = check_project_for_pydantic_settings(project_path)
        
        if uses and not declared:
            print(f"    ❌ USA pydantic_settings mas NÃO declara!")
            projects_missing.append(project_name)
        elif uses and declared:
            print(f"    ✅ USA e declara corretamente")
        elif not uses:
            print(f"    ⏭️  Não usa pydantic_settings")
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO:")
    
    if projects_missing:
        print(f"\n❌ Projetos com pydantic_settings FALTANTE:")
        for proj in projects_missing:
            print(f"   - {proj}")
            
        # Testa descoberta em um dos projetos
        if projects_missing:
            print(f"\n🧪 Testando descoberta em: {projects_missing[0]}")
            
            cmd = [
                sys.executable,
                "scripts/discover_missing_deps.py",
                projects_missing[0],
                "--dry-run"
            ]
            
            result = subprocess.run(
                cmd,
                check=False, cwd=workspace,
                capture_output=True,
                text=True
            )
            
            if "pydantic_settings" in result.stdout:
                print("✅ Script detectou corretamente!")
            else:
                print("❌ Script NÃO detectou!")
                print(f"Output: {result.stdout[:500]}")
    else:
        print("\n✅ Todos os projetos que usam pydantic_settings já têm declarado!")
    
    return 0 if not projects_missing else 1


if __name__ == "__main__":
    sys.exit(main())