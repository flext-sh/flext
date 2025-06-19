#!/bin/bash
# Script de Padronização PYAUTO
# Executa a padronização completa do workspace

set -e

echo "🔧 Iniciando Padronização PYAUTO..."
echo "=================================="

# Verifica se as dependências estão instaladas
echo "📦 Verificando dependências..."
python3 -c "import tomli, tomli_w, rich" 2>/dev/null || {
	echo "❌ Dependências não encontradas. Instalando..."
	pip install tomli tomli-w rich
}

# Executa validação inicial
echo "🔍 Validando estado atual..."
python3 validate_standards.py || echo "⚠️  Issues encontradas, prosseguindo com padronização..."

# Executa padronização
echo "🚀 Executando padronização..."
python3 standardize_projects.py --force

# Atualiza locks do Poetry
echo "🔄 Atualizando Poetry locks..."
find . -name "pyproject.toml" -not -path "./.venv/*" -not -path "./.mypy_cache/*" | while read -r project; do
	project_dir=$(dirname "$project")
	echo "  Processando: $project_dir"
	cd "$project_dir"
	if command -v poetry &>/dev/null; then
		poetry lock --no-update 2>/dev/null || echo "    ⚠️  Erro no poetry lock"
	fi
	cd - >/dev/null
done

# Validação final
echo "✅ Validação final..."
python3 validate_standards.py

echo "🎉 Padronização concluída!"
echo "========================"
echo "Próximos passos:"
echo "1. Execute 'make lint' para verificar conformidade"
echo "2. Execute 'make test' para validar funcionalidade"
echo "3. Commit as mudanças"
