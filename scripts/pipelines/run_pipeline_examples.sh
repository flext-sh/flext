#!/bin/bash
# Exemplos de uso do Pipeline WMS para Oracle Database
# Este script demonstra diferentes formas de usar o pipeline

set -euo pipefail

echo "🚀 Iniciando exemplos do pipeline WMS → Oracle"
echo "=============================================="

# Verifica se o arquivo de pipeline existe
if [ -z "$(test -f "wms_to_oracle_pipeline.py" && echo exists)" ]; then
	echo "❌ Arquivo wms_to_oracle_pipeline.py não encontrado no diretório atual"
	echo "💡 Execute este script no diretório onde está o pipeline"
	exit 1
fi

# Verifica se o Python está disponível
if [ -z "$(command -v python)" ]; then
	echo "❌ Python não encontrado"
	echo "💡 Instale o Python antes de continuar"
	exit 1
fi

echo "✅ Verificações iniciais concluídas"

echo ""
echo "📋 Exemplos disponíveis:"
echo "1. Pipeline básico - Orders"
echo "2. Pipeline com filtros - Items ativos"
echo "3. Pipeline com limite - Locations (100 registros)"
echo "4. Pipeline com configuração customizada"
echo "5. Pipeline com campos específicos"
echo "6. Pipeline com query avançada"
echo ""

# Função para executar exemplo com confirmação
run_example() {
	local description="$1"
	local command="$2"

	echo "📌 $description"
	echo "Comando: $command"
	echo ""

	read -p "Executar este exemplo? (y/N): " -n 1 -r
	echo ""

	if [[ $REPLY =~ ^[Yy]$ ]]; then
		echo "🔄 Executando..."
		eval "$command"
		echo "✅ Exemplo concluído!"
	else
		echo "⏭️ Exemplo pulado"
	fi
	echo ""
	echo "----------------------------------------"
	echo ""
}

# Exemplo 1: Pipeline básico
run_example \
	"Exemplo 1: Pipeline básico - Extrair orders e inserir em WMS_ORDERS" \
	"python wms_to_oracle_pipeline.py --resource orders --table WMS_ORDERS --limit 10"

# Exemplo 2: Pipeline com filtros
run_example \
	"Exemplo 2: Pipeline com filtros - Extrair apenas items ativos" \
	"python wms_to_oracle_pipeline.py --resource items --table WMS_ITEMS --filter 'status:eq:ACTIVE' --limit 50"

# Exemplo 3: Pipeline com limite
run_example \
	"Exemplo 3: Pipeline com limite - Extrair 100 locations" \
	"python wms_to_oracle_pipeline.py --resource locations --table WMS_LOCATIONS --limit 100"

# Exemplo 4: Pipeline com configuração
run_example \
	"Exemplo 4: Pipeline com configuração customizada" \
	"python wms_to_oracle_pipeline.py --config pipeline_config.json --resource inventory --table WMS_INVENTORY --limit 200"

# Exemplo 5: Pipeline com campos específicos
run_example \
	"Exemplo 5: Pipeline com campos específicos - Apenas ID e nome dos items" \
	"python wms_to_oracle_pipeline.py --resource items --table WMS_ITEMS_SUMMARY --fields 'item_id,item_name,status' --limit 25"

# Exemplo 6: Pipeline com query avançada
run_example \
	"Exemplo 6: Pipeline com query avançada - Orders dos últimos 30 dias" \
	"python wms_to_oracle_pipeline.py --resource orders --table WMS_RECENT_ORDERS --query 'order_date >= \"2024-01-01\"' --limit 100"

echo ""
echo "=" * 60
echo "🎯 Exemplos de uso do pipeline concluídos"
echo "=" * 60
echo "💡 Dicas:"
echo "- Use --verbose para logging detalhado"
echo "- Customize pipeline_config.json para suas necessidades"
echo "- Verifique os logs gerados para troubleshooting"
echo "- Use --help para ver todas as opções disponíveis"
echo ""
echo "📚 Para mais informações:"
echo "python wms_to_oracle_pipeline.py --help"
