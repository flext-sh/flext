#!/bin/bash

# Script para continuar push dos submódulos restantes

set -e

echo "🚀 Continuando push dos submódulos restantes..."

# Lista dos submódulos restantes (já processados: flext-core, flext-cli, flext-api, flext-auth, flext-meltano, flext-ldap, flext-ldif, flext-db-oracle)
REMAINING=(
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

process_submodule() {
    local submodule=$1
    local submodule_path="./$submodule"
    
    echo "📁 Processando: $submodule"
    
    if [ ! -d "$submodule_path" ]; then
        echo "❌ Submódulo $submodule não encontrado"
        return 1
    fi
    
    if [ ! -f "$submodule_path/.git" ]; then
        echo "❌ $submodule não é um submódulo Git"
        return 1
    fi
    
    cd "$submodule_path"
    
    if ! git remote get-url origin >/dev/null 2>&1; then
        echo "❌ $submodule não tem repositório remoto"
        cd ..
        return 1
    fi
    
    local status=$(git status --porcelain)
    if [ -z "$status" ]; then
        echo "✅ $submodule não tem mudanças"
        cd ..
        return 0
    fi
    
    echo "📝 $submodule tem mudanças"
    
    git add .
    git commit -m "feat: complete architectural refactoring and cleanup" || {
        echo "❌ Falha no commit de $submodule"
        cd ..
        return 1
    }
    
    local commit_hash=$(git rev-parse HEAD)
    
    git checkout main || {
        echo "❌ Falha no checkout de $submodule"
        cd ..
        return 1
    }
    
    git merge "$commit_hash" || {
        echo "❌ Falha no merge de $submodule"
        cd ..
        return 1
    }
    
    git push origin main || {
        echo "❌ Falha no push de $submodule"
        cd ..
        return 1
    }
    
    echo "✅ $submodule processado com sucesso!"
    cd ..
}

for submodule in "${REMAINING[@]}"; do
    process_submodule "$submodule"
done

echo "🎉 Processo concluído!" 
