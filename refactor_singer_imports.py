#!/usr/bin/env python3.13
"""
Script para refatorar imports singer_sdk para usar flext-meltano centralizado
EXECUTAR IMEDIATAMENTE para completar arquitetura
"""

import re
import sys
from pathlib import Path

def refactor_file(file_path: Path) -> bool:
    """Refatora um arquivo para usar flext-meltano em vez de singer_sdk."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Padrões de substituição para centralizacao via flext-meltano
        replacements = [
            # Singer SDK imports básicos
            (r'from singer_sdk import Stream, typing as th', 'from flext_meltano import Stream, th'),
            (r'from singer_sdk import Stream', 'from flext_meltano import Stream'),
            (r'from singer_sdk import typing as th', 'from flext_meltano import th'),
            (r'from singer_sdk import Tap', 'from flext_meltano import Tap'),
            (r'from singer_sdk import Target', 'from flext_meltano import Target'),
            
            # Singer SDK imports específicos
            (r'from singer_sdk\.streams import RESTStream', 'from flext_meltano import RESTStream'),
            (r'from singer_sdk\.streams import GraphQLStream', 'from flext_meltano import GraphQLStream'),
            (r'from singer_sdk\.authenticators import OAuthAuthenticator', 'from flext_meltano import OAuthAuthenticator'),
            (r'from singer_sdk\.pagination import BaseOffsetPaginator', 'from flext_meltano import BaseOffsetPaginator'),
            (r'from singer_sdk\.helpers\.capabilities import PluginCapabilities', 'from flext_meltano import PluginCapabilities'),
            
            # Singer SDK typing imports
            (r'from singer_sdk\.typing import PropertiesList, Property, StringType', 'from flext_meltano import PropertiesList, Property, StringType'),
            (r'from singer_sdk\.typing import PropertiesList', 'from flext_meltano import PropertiesList'),
            (r'from singer_sdk\.typing import Property', 'from flext_meltano import Property'),
            (r'from singer_sdk\.typing import StringType', 'from flext_meltano import StringType'),
            
            # Import direto singer_sdk
            (r'import singer_sdk', '# MIGRATED: Use flext-meltano centralized imports\n# import singer_sdk'),
        ]
        
        # Aplicar substituições
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Se houve mudança, adicionar comentário de migração
        if content != original_content:
            if '# MIGRATED:' not in content:
                # Adicionar comentário no topo após imports
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        insert_pos = i
                        break
                
                comment = '# MIGRATED: Singer SDK imports centralized via flext-meltano'
                if insert_pos > 0:
                    lines.insert(insert_pos, comment)
                else:
                    lines.insert(0, comment)
                content = '\n'.join(lines)
            
            file_path.write_text(content, encoding='utf-8')
            return True
        
        return False
    except Exception as e:
        print(f"ERRO ao refatorar {file_path}: {e}")
        return False

def main():
    """Executa refatoração em massa de todos os plugins."""
    print("🔄 REFATORAÇÃO IMEDIATA: Centralizando Singer SDK via flext-meltano")
    
    # Buscar todos os arquivos Python nos plugins
    plugin_dirs = [
        "/home/marlonsc/flext/flext-tap-*",
        "/home/marlonsc/flext/flext-target-*"
    ]
    
    total_files = 0
    refactored_files = 0
    
    for pattern in plugin_dirs:
        for plugin_dir in Path("/home/marlonsc/flext").glob(pattern.split('/')[-1]):
            if plugin_dir.is_dir():
                print(f"📂 Processando: {plugin_dir.name}")
                
                # Encontrar todos os arquivos Python
                for py_file in plugin_dir.rglob("*.py"):
                    if 'singer_sdk' in py_file.read_text(encoding='utf-8', errors='ignore'):
                        total_files += 1
                        if refactor_file(py_file):
                            refactored_files += 1
                            print(f"  ✅ Refatorado: {py_file.relative_to(plugin_dir)}")
    
    print(f"\n✅ CONCLUÍDO: {refactored_files}/{total_files} arquivos refatorados")
    print("🎯 Singer SDK agora centralizado via flext-meltano!")

if __name__ == "__main__":
    main()