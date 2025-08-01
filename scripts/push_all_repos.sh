#!/bin/bash

# Script para fazer push forçado de todos os repositórios FLEXT
# com merge em main

set -e

echo "🚀 Iniciando push forçado de todos os repositórios FLEXT..."

# Lista de repositórios para processar
REPOS=(
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
	"flext-oracle-oic-ext"
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

# Função para processar um repositório
process_repo() {
	local repo=$1
	local repo_path="./$repo"

	echo "📁 Processando: $repo"

	if [ ! -d "$repo_path" ]; then
		echo "❌ Diretório $repo não encontrado, pulando..."
		return 1
	fi

	cd "$repo_path"

	# Verificar se é um repositório Git
	if [ ! -d ".git" ]; then
		echo "❌ $repo não é um repositório Git, pulando..."
		cd ..
		return 1
	fi

	# Verificar se há repositório remoto
	if ! git remote get-url origin >/dev/null 2>&1; then
		echo "❌ $repo não tem repositório remoto configurado, pulando..."
		cd ..
		return 1
	fi

	echo "✅ $repo é um repositório Git válido"

	# Verificar status
	local status=$(git status --porcelain)
	if [ -z "$status" ]; then
		echo "✅ $repo não tem mudanças, pulando..."
		cd ..
		return 0
	fi

	echo "📝 $repo tem mudanças pendentes"

	# Adicionar todas as mudanças
	git add .

	# Fazer commit
	git commit -m "feat: complete architectural refactoring and cleanup" || {
		echo "❌ Falha ao fazer commit em $repo"
		cd ..
		return 1
	}

	# Obter o hash do commit
	local commit_hash=$(git rev-parse HEAD)

	# Fazer checkout para main
	git checkout main || {
		echo "❌ Falha ao fazer checkout para main em $repo"
		cd ..
		return 1
	}

	# Fazer merge
	git merge "$commit_hash" || {
		echo "❌ Falha ao fazer merge em $repo"
		cd ..
		return 1
	}

	# Fazer push
	git push origin main || {
		echo "❌ Falha ao fazer push de $repo"
		cd ..
		return 1
	}

	echo "✅ $repo processado com sucesso!"
	cd ..
}

# Processar repositório principal primeiro
echo "🏠 Processando repositório principal..."
cd /home/marlonsc/flext

# Verificar se há mudanças no repositório principal
if [ -n "$(git status --porcelain)" ]; then
	echo "📝 Repositório principal tem mudanças"
	git add .
	git commit -m "feat: update submodules and architectural improvements"
	git push origin refactor/architecture-cleanup
else
	echo "✅ Repositório principal não tem mudanças"
fi

# Processar cada repositório
for repo in "${REPOS[@]}"; do
	process_repo "$repo"
done

echo "🎉 Processo de push forçado concluído!"
echo "📊 Resumo:"
echo "   - Repositórios processados: ${#REPOS[@]}"
echo "   - Verifique os logs acima para detalhes"
