#!/bin/bash

# Script para fazer push forçado de submódulos FLEXT
# com merge em main

set -e

echo "🚀 Iniciando push forçado de submódulos FLEXT..."

# Lista de submódulos para processar
SUBMODULES=(
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

# Função para processar um submódulo
process_submodule() {
	local submodule=$1
	local submodule_path="./$submodule"

	echo "📁 Processando submódulo: $submodule"

	if [ ! -d "$submodule_path" ]; then
		echo "❌ Submódulo $submodule não encontrado"
		return 1
	fi

	# Verificar se é um submódulo Git
	if [ ! -f "$submodule_path/.git" ]; then
		echo "❌ $submodule não é um submódulo Git"
		return 1
	fi

	cd "$submodule_path"

	# Verificar se há repositório remoto
	if ! git remote get-url origin >/dev/null 2>&1; then
		echo "❌ $submodule não tem repositório remoto configurado"
		cd ..
		return 1
	fi

	echo "✅ $submodule é um submódulo Git válido"

	# Verificar status
	local status=$(git status --porcelain)
	if [ -z "$status" ]; then
		echo "✅ $submodule não tem mudanças"
		cd ..
		return 0
	fi

	echo "📝 $submodule tem mudanças pendentes"

	# Adicionar todas as mudanças
	git add .

	# Fazer commit
	git commit -m "feat: complete architectural refactoring and cleanup" || {
		echo "❌ Falha ao fazer commit em $submodule"
		cd ..
		return 1
	}

	# Obter o hash do commit
	local commit_hash=$(git rev-parse HEAD)

	# Fazer checkout para main
	git checkout main || {
		echo "❌ Falha ao fazer checkout para main em $submodule"
		cd ..
		return 1
	}

	# Fazer merge
	git merge "$commit_hash" || {
		echo "❌ Falha ao fazer merge em $submodule"
		cd ..
		return 1
	}

	# Fazer push
	git push origin main || {
		echo "❌ Falha ao fazer push de $submodule"
		cd ..
		return 1
	}

	echo "✅ $submodule processado com sucesso!"
	cd ..
}

# Processar cada submódulo
for submodule in "${SUBMODULES[@]}"; do
	process_submodule "$submodule"
done

echo "🎉 Processo de push forçado de submódulos concluído!"
