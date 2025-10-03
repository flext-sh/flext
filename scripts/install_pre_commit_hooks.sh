#!/bin/bash

# Script para instalar pre-commit hooks em todos os projetos FLEXT

set -e

echo "🎣 Instalando pre-commit hooks em todos os projetos FLEXT..."

# Lista de projetos Python
PYTHON_PROJECTS=(
	"flext-core"
	"flext-cli"
	"flext-api"
	"flext-auth"
	"flext-meltano"
	"flext-ldap"
	"flext-ldif"
	"flext-db-oracle"
	"flext-dbt-oracle"
	"flext-dbt-oracle-wms"
	"flext-dbt-ldap"
	"flext-dbt-ldif"
	"flext-grpc"
	"flext-observability"
	"flext-web"
	"flext-oracle-wms"
	"flext-oracle-oic"
	"flext-plugin"
	"flext-quality"
	"flext-tap-oracle"
	"flext-tap-ldap"
	"flext-tap-ldif"
	"flext-tap-oracle-oic"
	"flext-tap-oracle-wms"
	"flext-target-oracle"
	"flext-target-ldap"
	"flext-target-ldif"
	"flext-target-oracle-oic"
	"flext-target-oracle-wms"
	"client-b-meltano-native"
	"client-a-oud-mig"
	"flexcore"
)

install_hooks() {
	local project=$1
	local project_path="./$project"

	echo "📁 Instalando hooks em: $project"

	if [ ! -d "$project_path" ]; then
		echo "❌ Projeto $project não encontrado"
		return 1
	fi

	cd "$project_path"

	# Verificar se tem pyproject.toml
	if [ ! -f "pyproject.toml" ]; then
		echo "❌ pyproject.toml não encontrado"
		cd ..
		return 1
	fi

	# Verificar se tem .pre-commit-config.yaml
	if [ ! -f ".pre-commit-config.yaml" ]; then
		echo "❌ .pre-commit-config.yaml não encontrado"
		cd ..
		return 1
	fi

	# Verificar se os hooks já estão instalados
	if [ -f ".git/hooks/pre-commit" ]; then
		echo "✅ Pre-commit hooks já instalados"
		cd ..
		return 0
	fi

	# Instalar pre-commit hooks
	echo "🎣 Instalando pre-commit hooks..."
	if poetry run pre-commit install 2>/dev/null; then
		echo "✅ Pre-commit hooks instalados com sucesso"
	else
		echo "⚠️ Falha ao instalar pre-commit hooks (pode ser normal em alguns casos)"
	fi

	cd ..
}

# Contadores
TOTAL=0
SUCCESS=0
FAILED=0

# Instalar hooks em cada projeto
for project in "${PYTHON_PROJECTS[@]}"; do
	TOTAL=$((TOTAL + 1))
	if install_hooks "$project"; then
		SUCCESS=$((SUCCESS + 1))
	else
		FAILED=$((FAILED + 1))
	fi
done

echo "🎉 Instalação de pre-commit hooks concluída!"
echo "📊 Resumo:"
echo "   - Total de projetos: $TOTAL"
echo "   - Sucessos: $SUCCESS"
echo "   - Falhas: $FAILED"

if [ $FAILED -gt 0 ]; then
	echo "⚠️ Alguns projetos falharam. Verifique manualmente."
	exit 1
else
	echo "✅ Todos os projetos processados com sucesso!"
fi

echo ""
echo "💡 Para testar os hooks:"
echo "   cd <projeto> && poetry run pre-commit run --all-files"
echo ""
echo "💡 Para executar hooks em arquivos específicos:"
echo "   cd <projeto> && poetry run pre-commit run --files <arquivo>"
