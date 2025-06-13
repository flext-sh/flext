#!/usr/bin/env python3
"""
Systematic Docstring Standardization Tool

This script systematically identifies and translates Portuguese docstrings
to professional English across the entire codebase.
"""

import argparse
import re
from pathlib import Path


class DocstringTranslator:
    """Professional docstring translation system."""

    def __init__(self):
        """Initialize the translator with Portuguese-to-English mappings."""
        self.translations = {
            # Common Portuguese docstring patterns
            r'"""[\s]*Configura[çc]ão': '"""Configuration',
            r'"""[\s]*Configuração': '"""Configuration',
            r'"""[\s]*Classe': '"""Class',
            r'"""[\s]*Função': '"""Function',
            r'"""[\s]*Método': '"""Method',
            r'"""[\s]*Utilitário': '"""Utility',
            r'"""[\s]*Utilitarios': '"""Utilities',
            r'"""[\s]*Gerencia': '"""Manages',
            r'"""[\s]*Executa': '"""Executes',
            r'"""[\s]*Processa': '"""Processes',
            r'"""[\s]*Valida': '"""Validates',
            r'"""[\s]*Verifica': '"""Verifies',
            r'"""[\s]*Carrega': '"""Loads',
            r'"""[\s]*Salva': '"""Saves',
            r'"""[\s]*Cria': '"""Creates',
            r'"""[\s]*Remove': '"""Removes',
            r'"""[\s]*Atualiza': '"""Updates',
            r'"""[\s]*Retorna': '"""Returns',
            r'"""[\s]*Implementa': '"""Implements',
            r'"""[\s]*Define': '"""Defines',

            # Common words and phrases
            r'\bconfiguração\b': 'configuration',
            r'\bconfiguracão\b': 'configuration',
            r'\bconfiguracoes\b': 'configurations',
            r'\bparâmetros\b': 'parameters',
            r'\bparametros\b': 'parameters',
            r'\bargumentos\b': 'arguments',
            r'\bretorna\b': 'returns',
            r'\bexecuta\b': 'executes',
            r'\bprocessa\b': 'processes',
            r'\bvalida\b': 'validates',
            r'\bverifica\b': 'verifies',
            r'\bcarrega\b': 'loads',
            r'\bsalva\b': 'saves',
            r'\bcria\b': 'creates',
            r'\bremove\b': 'removes',
            r'\batualiza\b': 'updates',
            r'\bimplementa\b': 'implements',
            r'\bdefine\b': 'defines',
            r'\bgerencia\b': 'manages',
            r'\butilitário\b': 'utility',
            r'\butilitarios\b': 'utilities',
            r'\bfunção\b': 'function',
            r'\bfuncao\b': 'function',
            r'\bmétodo\b': 'method',
            r'\bmetodo\b': 'method',
            r'\bclasse\b': 'class',
            r'\barquivo\b': 'file',
            r'\bdiretório\b': 'directory',
            r'\bdiretorio\b': 'directory',
            r'\bcaminho\b': 'path',
            r'\bdados\b': 'data',
            r'\bresultado\b': 'result',
            r'\bresultados\b': 'results',
            r'\berro\b': 'error',
            r'\berros\b': 'errors',
            r'\bexceção\b': 'exception',
            r'\bexcecao\b': 'exception',
            r'\bexceções\b': 'exceptions',
            r'\bexcecoes\b': 'exceptions',
            r'\bverdadeiro\b': 'true',
            r'\bfalso\b': 'false',
            r'\bvazio\b': 'empty',
            r'\bnulo\b': 'null',
            r'\bpadrão\b': 'default',
            r'\bpadrao\b': 'default',
            r'\bopcional\b': 'optional',
            r'\bobrigatório\b': 'required',
            r'\bobrigatorio\b': 'required',
            r'\bdisponível\b': 'available',
            r'\bdisponivel\b': 'available',
            r'\bnecessário\b': 'necessary',
            r'\bnecessario\b': 'necessary',
            r'\bpossível\b': 'possible',
            r'\bpossivel\b': 'possible',
            r'\bválido\b': 'valid',
            r'\bvalido\b': 'valid',
            r'\binválido\b': 'invalid',
            r'\binvalido\b': 'invalid',

            # Specific technical terms
            r'\bconexão\b': 'connection',
            r'\bconexao\b': 'connection',
            r'\bconexões\b': 'connections',
            r'\bconexoes\b': 'connections',
            r'\bautenticação\b': 'authentication',
            r'\bautenticacao\b': 'authentication',
            r'\bautorização\b': 'authorization',
            r'\bautorizacao\b': 'authorization',
            r'\bsessão\b': 'session',
            r'\bsessao\b': 'session',
            r'\bsessões\b': 'sessions',
            r'\bsessoes\b': 'sessions',
            r'\btransação\b': 'transaction',
            r'\btransacao\b': 'transaction',
            r'\btransações\b': 'transactions',
            r'\btransacoes\b': 'transactions',
            r'\bconsulta\b': 'query',
            r'\bconsultas\b': 'queries',
            r'\boperação\b': 'operation',
            r'\boperacao\b': 'operation',
            r'\boperações\b': 'operations',
            r'\boperacoes\b': 'operations',
            r'\bprocessamento\b': 'processing',
            r'\bvalidação\b': 'validation',
            r'\bvalidacao\b': 'validation',
            r'\bverificação\b': 'verification',
            r'\bverificacao\b': 'verification',
            r'\bintegração\b': 'integration',
            r'\bintegracao\b': 'integration',
            r'\bmigração\b': 'migration',
            r'\bmigracao\b': 'migration',
            r'\bimportação\b': 'import',
            r'\bimportacao\b': 'import',
            r'\bexportação\b': 'export',
            r'\bexportacao\b': 'export',
            r'\bsincronização\b': 'synchronization',
            r'\bsincronizacao\b': 'synchronization',

            # Common phrases
            r'\bse necessário\b': 'if necessary',
            r'\bse necessario\b': 'if necessary',
            r'\bpor padrão\b': 'by default',
            r'\bpor padrao\b': 'by default',
            r'\bem caso de erro\b': 'in case of error',
            r'\bem caso de\b': 'in case of',
            r'\bno caso de\b': 'in case of',
            r'\bpara cada\b': 'for each',
            r'\bde acordo com\b': 'according to',
            r'\batravés de\b': 'through',
            r'\batraves de\b': 'through',
            r'\bpor meio de\b': 'by means of',
            r'\bcom base em\b': 'based on',
            r'\ba partir de\b': 'from',
            r'\bem relação a\b': 'regarding',
            r'\bem relacao a\b': 'regarding',
            r'\bcom relação a\b': 'regarding',
            r'\bcom relacao a\b': 'regarding',
        }

                 # Files to process (from our analysis)
         self.target_files = [
             'scripts/utilities/sync_dependencies.py',
             'scripts/analysis/generate_full_coverage_report.py',
             'scripts/utilities/standardize_projects.py',
             'scripts/utilities/resolve_dependencies.py',
             'scripts/analysis/validate_standards.py',
             'scripts/dev_tools/dc_api_x_monkeytype.py',
             'scripts/maintenance/cleanup_temp_scripts.py',
             'client-b-poc-oic-wms/test_real_cli.py',
             'client-b-poc-oic-wms/test_all_commands.py',
             'client-b-poc-oic-wms/show_all_commands.py',
             'client-b-poc-oic-wms/test_commands_mock.py',
             'client-a-mig-oud/comparison_demo.py',
             'client-a-mig-oud/create_links.py',
             'flx/src/flx/core/commands/base.py',
             'flx/src/flx/core/commands/bus.py',
             'flx/src/flx/core/commands/registry.py',
             'flx/src/flx/core/commands/__init__.py',
             'flx/src/flx/core/commands/exceptions.py',
             'flx/src/flx/core/domain/services/ldap.py',
             'flx/src/flx/core/domain/services/__init__.py',
             'flx/src/flx/core/domain/value_object_types/ldap.py',
             'flx/src/flx/core/domain/value_object_types/__init__.py',
             'flx/src/flx/core/domain/entities.py',
             'flx/src/flx/core/domain/exceptions.py',
             'flx/src/flx/core/domain/base_service.py',
             'flx/src/flx/core/domain/__init__.py',
             'flx/src/flx/core/domain/value_objects.py',
             'flx/src/flx/core/domain/customer.py',
             'flx/src/flx/core/contracts/adapters.py',
             'flx/src/flx/core/contracts/logging.py'
         ]

    def find_portuguese_content(self, file_path: Path) -> list[tuple[int, str]]:
        """Find Portuguese content in a file."""
        portuguese_lines = []

        try:
            with open(file_path, encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                # Check for Portuguese words
                for pattern in self.translations:
                    if re.search(pattern, line, re.IGNORECASE):
                        portuguese_lines.append((i, line.strip()))
                        break

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

        return portuguese_lines

    def translate_content(self, content: str) -> str:
        """Translate Portuguese content to English."""
        translated = content

        for portuguese_pattern, english_replacement in self.translations.items():
            translated = re.sub(portuguese_pattern, english_replacement, translated, flags=re.IGNORECASE)

        return translated

    def process_file(self, file_path: Path) -> bool:
        """Process a single file for translation."""
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return False

        try:
            # Read original content
            with open(file_path, encoding='utf-8') as f:
                original_content = f.read()

            # Translate content
            translated_content = self.translate_content(original_content)

            # Check if changes were made
            if original_content != translated_content:
                # Create backup
                backup_path = file_path.with_suffix(f'{file_path.suffix}.bak')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)

                # Write translated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(translated_content)

                print(f"✅ Translated: {file_path}")
                return True
            print(f"⏭️  No changes needed: {file_path}")
            return False

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def process_all_files(self) -> dict[str, bool]:
        """Process all target files."""
        results = {}

        print("🚀 Starting systematic docstring translation...")
        print(f"📋 Processing {len(self.target_files)} files...")
        print()

        for file_path_str in self.target_files:
            file_path = Path(file_path_str)
            print(f"🔄 Processing: {file_path}")

            # Find Portuguese content first
            portuguese_lines = self.find_portuguese_content(file_path)
            if portuguese_lines:
                print(f"   📝 Found {len(portuguese_lines)} Portuguese items")
                for line_num, line in portuguese_lines[:3]:  # Show first 3
                    print(f"      Line {line_num}: {line[:60]}...")
                if len(portuguese_lines) > 3:
                    print(f"      ... and {len(portuguese_lines) - 3} more")

            # Process the file
            success = self.process_file(file_path)
            results[file_path_str] = success
            print()

        return results

    def generate_report(self, results: dict[str, bool]) -> None:
        """Generate a completion report."""
        total_files = len(results)
        processed_files = sum(results.values())

        print("=" * 60)
        print("📊 SYSTEMATIC TRANSLATION REPORT")
        print("=" * 60)
        print(f"Total files processed: {total_files}")
        print(f"Files with changes: {processed_files}")
        print(f"Files unchanged: {total_files - processed_files}")
        print()

        if processed_files > 0:
            print("✅ Files successfully translated:")
            for file_path, success in results.items():
                if success:
                    print(f"   • {file_path}")

        print()
        print("🔍 Next steps:")
        print("1. Run validation to verify all Portuguese content is removed")
        print("2. Test affected functionality")
        print("3. Commit changes with proper documentation")
        print()
        print("💾 Backup files created with .bak extension")
        print("🔄 Use 'git diff' to review all changes")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Systematic docstring translation tool')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--file', type=str, help='Process specific file only')

    args = parser.parse_args()

    translator = DocstringTranslator()

    if args.file:
        # Process single file
        file_path = Path(args.file)
        if args.dry_run:
            portuguese_lines = translator.find_portuguese_content(file_path)
            if portuguese_lines:
                print(f"Would translate {len(portuguese_lines)} items in {file_path}")
                for line_num, line in portuguese_lines:
                    print(f"  Line {line_num}: {line}")
            else:
                print(f"No Portuguese content found in {file_path}")
        else:
            translator.process_file(file_path)
    # Process all files
    elif args.dry_run:
        print("DRY RUN - No changes will be made")
        for file_path_str in translator.target_files:
            file_path = Path(file_path_str)
            portuguese_lines = translator.find_portuguese_content(file_path)
            if portuguese_lines:
                print(f"{file_path}: {len(portuguese_lines)} Portuguese items")
    else:
        results = translator.process_all_files()
        translator.generate_report(results)


if __name__ == '__main__':
    main()
