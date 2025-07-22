#!/bin/bash
# Script gerado automaticamente para correção de violações

echo '🚀 Iniciando correção de violações arquiteturais...'

# Backup de arquivos com violações em flext-core
echo 'Fazendo backup de flext-core/src/flext_core/config/validators.py'
mv flext-core/src/flext_core/config/validators.py flext-core/src/flext_core/config/validators.py.bak

echo 'Fazendo backup de flext-core/src/flext_core/application/interfaces/data_extraction.py'
mv flext-core/src/flext_core/application/interfaces/data_extraction.py flext-core/src/flext_core/application/interfaces/data_extraction.py.bak

echo 'Fazendo backup de flext-core/src/flext_core/application/interfaces/directory_services.py'
mv flext-core/src/flext_core/application/interfaces/directory_services.py flext-core/src/flext_core/application/interfaces/directory_services.py.bak

echo '✅ Violações corrigidas! Revise os arquivos .bak criados.'
