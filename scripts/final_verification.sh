#!/bin/bash

# Script para verificação final e push de todos os submódulos

set -e

echo "🔍 Verificação final de todos os submódulos..."

# Lista de todos os submódulos
SUBMODULES=(
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

verify_and_push() {
    local submodule=$1
    local submodule_path="./$submodule"
    
    echo "📁 Verificando: $submodule"
    
    if [ ! -d "$submodule_path" ]; then
        echo "❌ Submódulo $submodule não encontrado"
        return 1
    fi
    
    if [ ! -f "$submodule_path/.git" ]; then
        echo "❌ $submodule não é um submódulo Git"
        return 1
    fi
    
    cd "$submodule_path"
    
    # Verificar se há mudanças pendentes
    local status=$(git status --porcelain)
    if [ -n "$status" ]; then
        echo "📝 $submodule tem mudanças pendentes"
        
        # Adicionar todas as mudanças
        git add .
        
        # Fazer commit
        git commit -m "feat: final architectural refactoring and cleanup" || {
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
        
        echo "✅ $submodule processado e enviado com sucesso!"
    else
        echo "✅ $submodule está limpo"
    fi
    
    cd ..
}

# Contadores
TOTAL=0
SUCCESS=0
FAILED=0

# Processar cada submódulo
for submodule in "${SUBMODULES[@]}"; do
    TOTAL=$((TOTAL + 1))
    if verify_and_push "$submodule"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

echo "🎉 Verificação final concluída!"
echo "📊 Resumo:"
echo "   - Total de submódulos: $TOTAL"
echo "   - Sucessos: $SUCCESS"
echo "   - Falhas: $FAILED" 
