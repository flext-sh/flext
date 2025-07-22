#!/bin/bash

# Script para resolver automaticamente todos os conflitos de merge
# usando a versão atual (nossa versão)

set -e

echo "🚀 Resolvendo todos os conflitos de merge automaticamente..."

# Lista de todos os submódulos para verificar
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
    "gruponos-meltano-native"
    "algar-oud-mig"
    "flexcore"
)

resolve_conflicts() {
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
    
    # Verificar se há conflitos de merge
    if git status --porcelain | grep -q "^UU\|^AA\|^DD"; then
        echo "🔧 Resolvendo conflitos em $submodule"
        
        # Obter lista de arquivos com conflitos
        local conflicted_files=$(git status --porcelain | grep "^UU\|^AA\|^DD" | awk '{print $2}')
        
        for file in $conflicted_files; do
            if [ -f "$file" ]; then
                echo "  📝 Resolvendo conflito em: $file"
                # Usar nossa versão (--ours) para todos os arquivos
                git checkout --ours "$file" 2>/dev/null || true
            fi
        done
        
        # Remover arquivos deletados por nós
        git status --porcelain | grep "^DD" | awk '{print $2}' | xargs -r git rm 2>/dev/null || true
        
        # Adicionar todos os arquivos resolvidos
        git add .
        
        # Fazer commit da resolução
        git commit -m "fix: resolve merge conflicts using current version" || {
            echo "❌ Falha ao fazer commit da resolução em $submodule"
            cd ..
            return 1
        }
        
        # Fazer push
        git push origin main || {
            echo "❌ Falha ao fazer push de $submodule"
            cd ..
            return 1
        }
        
        echo "✅ Conflitos resolvidos em $submodule"
    else
        echo "✅ $submodule não tem conflitos"
    fi
    
    cd ..
}

# Processar cada submódulo
for submodule in "${SUBMODULES[@]}"; do
    resolve_conflicts "$submodule"
done

echo "🎉 Processo de resolução de conflitos concluído!" 
