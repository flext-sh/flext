#!/bin/bash
# Setup completo do PyAuto: PEP8 + Instalação

set -e

echo "🚀 Setup Completo do PyAuto"
echo "==========================="
echo ""

# 1. Ativar ambiente virtual
echo "→ Ativando ambiente virtual..."
source .venv/bin/activate

# 2. Instalar ferramentas de formatação
echo ""
echo "📦 Instalando ferramentas de formatação..."
pip install black isort ruff tomlkit

# 3. Aplicar Black em todos os projetos
echo ""
echo "⚫ Aplicando Black (formatação de código)..."
PROJECTS="flx flx-database-oracle flx-http-oracle-oic flx-http-oracle-wms algar-mig-oud gruponos-poc-oic-wms flx-adapter-example dc-code-analyzer"

for proj in $PROJECTS; do
    if [ -d "$proj" ]; then
        echo "  → Formatando $proj..."
        black "$proj" --quiet || true
    fi
done

# 4. Aplicar isort
echo ""
echo "🔤 Aplicando isort (organização de imports)..."
for proj in $PROJECTS; do
    if [ -d "$proj" ]; then
        echo "  → Organizando imports em $proj..."
        isort "$proj" --quiet || true
    fi
done

# 5. Aplicar Ruff com correções automáticas
echo ""
echo "🦀 Aplicando Ruff (linting com correções)..."
for proj in $PROJECTS; do
    if [ -d "$proj" ]; then
        echo "  → Linting $proj..."
        ruff check "$proj" --fix --quiet || true
    fi
done

# 6. Instalar todas as dependências via Poetry
echo ""
echo "📦 Instalando todas as dependências via Poetry..."
echo ""

# Workspace principal
echo "→ Instalando workspace principal..."
poetry install --all-extras --with dev --no-interaction

# Projetos individuais
for proj in $PROJECTS; do
    if [ -d "$proj" ] && [ -f "$proj/pyproject.toml" ]; then
        echo ""
        echo "→ Instalando $proj..."
        cd "$proj"
        poetry install --no-interaction || true
        cd ..
    fi
done

# 7. Instalar em modo editable
echo ""
echo "🔗 Instalando projetos em modo editable..."
pip install -e flx/
pip install -e flx-database-oracle/
pip install -e flx-http-oracle-oic/
pip install -e flx-http-oracle-wms/
pip install -e algar-mig-oud/
pip install -e gruponos-poc-oic-wms/
pip install -e flx-adapter-example/

# 8. Validar instalação
echo ""
echo "✅ Validando instalação..."
python -c "
import sys
print(f'Python: {sys.version}')
print(f'Venv: {sys.prefix}')
print()

imports = [
    ('flx', 'Core framework'),
    ('flx_database_oracle', 'Oracle DB adapter'),
    ('flx_http_oracle_oic', 'Oracle OIC adapter'),
    ('flx_http_oracle_wms', 'Oracle WMS adapter'),
    ('algar_oud_mig', 'LDAP migration'),
    ('gn_oic_wms_db', 'GrupoNos integration')
]

success = 0
for module, desc in imports:
    try:
        __import__(module)
        print(f'✅ {module} ({desc})')
        success += 1
    except Exception as e:
        print(f'❌ {module} ({desc}): {e}')

print()
print(f'Total: {success}/{len(imports)} imports funcionando')
"

# 9. Contar pacotes instalados
echo ""
echo "📊 Total de pacotes instalados:"
pip list | wc -l

echo ""
echo "✅ Setup completo finalizado!"
echo ""
echo "Para usar o ambiente:"
echo "  source .venv/bin/activate"
echo ""
echo "Comandos disponíveis via Makefile:"
echo "  make pep8-validate    # Validar conformidade PEP8"
echo "  make test            # Executar testes"
echo "  make lint            # Verificar código"