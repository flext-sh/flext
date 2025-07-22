#!/bin/bash

# Script para fazer push forçado de repositórios FLEXT em paralelo
# com merge em main

set -e

echo "🚀 Iniciando push forçado paralelo de repositórios FLEXT..."

# Lista de repositórios para processar
REPOS=(
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
        echo "❌ Diretório $repo não encontrado"
        return 1
    fi
    
    cd "$repo_path"
    
    # Verificar se é um repositório Git
    if [ ! -d ".git" ]; then
        echo "❌ $repo não é um repositório Git"
        cd ..
        return 1
    fi
    
    # Verificar se há repositório remoto
    if ! git remote get-url origin >/dev/null 2>&1; then
        echo "❌ $repo não tem repositório remoto configurado"
        cd ..
        return 1
    fi
    
    # Verificar status
    local status=$(git status --porcelain)
    if [ -z "$status" ]; then
        echo "✅ $repo não tem mudanças"
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

# Processar repositórios em paralelo (máximo 5 simultâneos)
MAX_JOBS=5
JOBS=()

for repo in "${REPOS[@]}"; do
    # Aguardar se já temos o máximo de jobs rodando
    while [ ${#JOBS[@]} -ge $MAX_JOBS ]; do
        for i in "${!JOBS[@]}"; do
            if ! kill -0 "${JOBS[$i]}" 2>/dev/null; then
                unset "JOBS[$i]"
            fi
        done
        JOBS=("${JOBS[@]}")  # Reindexar array
        sleep 1
    done
    
    # Iniciar processamento em background
    process_repo "$repo" &
    JOBS+=($!)
done

# Aguardar todos os jobs terminarem
for job in "${JOBS[@]}"; do
    wait "$job"
done

echo "🎉 Processo de push forçado paralelo concluído!" 
