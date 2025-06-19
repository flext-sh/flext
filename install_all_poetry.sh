#!/bin/bash
# Script para instalar TODAS as dependências do PyAuto via Poetry

set -e # Exit on error

echo "🚀 Instalação completa do PyAuto via Poetry"
echo "==========================================="

# Ativar ambiente virtual
echo "→ Ativando ambiente virtual..."
source .venv/bin/activate

# Verificar Poetry
echo "→ Verificando Poetry..."
which poetry
poetry --version

# Instalar dependências do workspace principal
echo ""
echo "📦 Instalando dependências do workspace principal..."
poetry install --all-extras --with dev

# Lista de projetos
PROJECTS="flx flx-database-oracle flx-http-oracle-oic flx-http-oracle-wms client-a-mig-oud client-b-poc-oic-wms flx-adapter-example"

# Instalar cada projeto
echo ""
echo "📦 Instalando projetos individuais..."
for proj in $PROJECTS; do
	if [ -d "$proj" ]; then
		echo ""
		echo "→ Instalando $proj..."
		cd "$proj"
		if [ -f "pyproject.toml" ]; then
			# Criar poetry.lock se não existir
			if [ ! -f "poetry.lock" ] || [ "pyproject.toml" -nt "poetry.lock" ]; then
				poetry lock --no-update || true
			fi
			# Instalar dependências
			poetry install --all-extras || poetry install || true
		fi
		cd ..
	fi
done

# Instalar projetos em modo editable
echo ""
echo "🔗 Instalando projetos em modo editable..."
pip install -e flx/
pip install -e flx-database-oracle/
pip install -e flx-http-oracle-oic/
pip install -e flx-http-oracle-wms/
pip install -e client-a-mig-oud/
pip install -e client-b-poc-oic-wms/
pip install -e flx-adapter-example/

# Validar instalação
echo ""
echo "✅ Validando instalação..."
python -c "
import sys
print(f'Python: {sys.version}')
print(f'Venv: {sys.prefix}')

try:
    import flx
    print('✅ flx importado')
except Exception as e:
    print(f'❌ flx: {e}')

try:
    import flx_database_oracle
    print('✅ flx_database_oracle importado')
except Exception as e:
    print(f'❌ flx_database_oracle: {e}')

try:
    import flx_http_oracle_oic
    print('✅ flx_http_oracle_oic importado')
except Exception as e:
    print(f'❌ flx_http_oracle_oic: {e}')

try:
    import flx_http_oracle_wms
    print('✅ flx_http_oracle_wms importado')
except Exception as e:
    print(f'❌ flx_http_oracle_wms: {e}')

try:
    import client-a_oud_mig
    print('✅ client-a_oud_mig importado')
except Exception as e:
    print(f'❌ client-a_oud_mig: {e}')

try:
    import gn_oic_wms_db
    print('✅ gn_oic_wms_db importado')
except Exception as e:
    print(f'❌ gn_oic_wms_db: {e}')
"

# Contar pacotes instalados
echo ""
echo "📊 Total de pacotes instalados:"
pip list | wc -l

echo ""
echo "✅ Instalação completa!"
echo "Para usar: source .venv/bin/activate"
