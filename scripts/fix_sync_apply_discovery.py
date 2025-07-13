#!/usr/bin/env python3
"""
Script para REALMENTE fazer --apply funcionar com --discover-missing
Este é um patch temporário para testar a solução antes de modificar o script principal.
"""

import sys
from pathlib import Path


def analyze_sync_dependencies_apply_issue():
    """Analisa o problema com --apply no sync_dependencies.py"""
    
    print("🔍 ANÁLISE DO PROBLEMA COM --apply E --discover-missing")
    print("=" * 60)
    
    print("\n❌ PROBLEMA IDENTIFICADO:")
    print("1. O modo --discover-missing faz descoberta automática")
    print("2. A função install_discovered_dependencies() adiciona deps automaticamente")
    print("3. MAS não respeita a flag --apply (sempre adiciona!)")
    print("4. O --apply só funciona para padronização de versões")
    
    print("\n🔧 SOLUÇÃO NECESSÁRIA:")
    print("1. Modificar install_discovered_dependencies() para respeitar --dry-run")
    print("2. Fazer --apply controlar se adiciona ou não dependências descobertas")
    print("3. Separar descoberta (análise) de aplicação (poetry add)")
    
    print("\n📋 MUDANÇAS ESPECÍFICAS NO CÓDIGO:")
    print("1. Em sync_project(), linha 2184:")
    print("   ANTES: discovery_stats = install_discovered_dependencies(project, discovered_deps)")
    print("   DEPOIS: if not args.dry_run:")
    print("           discovery_stats = install_discovered_dependencies(project, discovered_deps)")
    print("           else:")
    print("           discovery_stats = show_discovered_dependencies(project, discovered_deps)")
    
    print("\n2. Criar nova função show_discovered_dependencies() que apenas mostra")
    print("3. Passar args para sync_project() para verificar dry_run")
    
    return True


def create_patch_file():
    """Cria um arquivo de patch para aplicar as mudanças."""
    
    patch_content = '''--- sync_dependencies.py.original
+++ sync_dependencies.py
@@ -2163,6 +2163,7 @@
 def sync_project(
     project: Path,
     base_dependencies: dict[str, list[str]],
+    args,  # NOVO: passar argumentos para verificar dry_run
     stdlib_modules: set[str],
     known_deps: set[str],
 ) -> dict[str, int]:
@@ -2180,11 +2181,20 @@
     discovered_deps = discover_project_dependencies(project, stdlib_modules, known_deps)
 
     # Instala dependências descobertas automaticamente
-    if any(deps for deps in discovered_deps.values()):
-        discovery_stats = install_discovered_dependencies(project, discovered_deps)
-        stats["discovered"] = discovery_stats["installed"]
-        stats["conflicts"] = discovery_stats["conflicts"]
-
+    if any(deps for deps in discovered_deps.values()):
+        if not args.dry_run and not args.discover_missing:
+            # Modo normal: instala automaticamente
+            discovery_stats = install_discovered_dependencies(project, discovered_deps)
+            stats["discovered"] = discovery_stats["installed"]
+            stats["conflicts"] = discovery_stats["conflicts"]
+        elif args.discover_missing and args.apply:
+            # Modo descoberta com --apply: instala
+            discovery_stats = install_discovered_dependencies(project, discovered_deps)
+            stats["discovered"] = discovery_stats["installed"]
+            stats["conflicts"] = discovery_stats["conflicts"]
+        else:
+            # Modo descoberta sem --apply ou dry-run: apenas mostra
+            discovery_stats = show_discovered_dependencies(project, discovered_deps)
'''
    
    with open("/home/marlonsc/flext/scripts/sync_dependencies_apply.patch", "w") as f:
        f.write(patch_content)
    
    print("\n✅ Arquivo de patch criado: sync_dependencies_apply.patch")
    print("Para aplicar: patch -p0 < sync_dependencies_apply.patch")
    
    return True


def main():
    """Função principal."""
    
    # Analisa o problema
    analyze_sync_dependencies_apply_issue()
    
    # Cria arquivo de patch
    create_patch_file()
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Implementar show_discovered_dependencies()")
    print("2. Modificar chamadas de sync_project() para passar args")
    print("3. Testar com --discover-missing --dry-run")
    print("4. Testar com --discover-missing --apply")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())