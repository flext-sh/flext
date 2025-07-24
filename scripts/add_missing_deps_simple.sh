#!/bin/bash

# Script simples para adicionar dependências faltantes identificadas
# Baseado no output do script de pre-commit

set -e

echo "📦 Adicionando dependências faltantes nos projetos FLEXT..."

# Projetos que precisam de detect-secrets
PROJECTS_NEEDING_DETECT_SECRETS=(
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
    "flext-tap-ldap"
    "flext-tap-ldif"
    "flext-tap-oracle-oic"
    "flext-tap-oracle-wms"
    "flext-target-ldap"
    "flext-target-ldif"
    "flext-target-oracle-oic"
    "flext-target-oracle-wms"
    "client-b-meltano-native"
    "client-a-oud-mig"
    "flexcore"
)

# Projetos que precisam de dependências adicionais
PROJECTS_NEEDING_EXTRA_DEPS=(
    "flext-tap-oracle:black,vulture,radon"
    "flext-target-oracle:pre-commit,black,isort,vulture,radon"
)

add_detect_secrets() {
    local project=$1
    local project_path="./$project"
    
    echo "📁 Adicionando detect-secrets em: $project"
    
    if [ ! -d "$project_path" ]; then
        echo "❌ Projeto $project não encontrado"
        return 1
    fi
    
    cd "$project_path"
    
    # Verificar se detect-secrets já está presente
    if grep -q "detect-secrets" pyproject.toml; then
        echo "✅ detect-secrets já presente em $project"
        cd ..
        return 0
    fi
    
    # Adicionar detect-secrets
    echo "📦 Adicionando detect-secrets..."
    if poetry add --group dev detect-secrets 2>/dev/null; then
        echo "✅ detect-secrets adicionado com sucesso"
    else
        echo "⚠️ Falha ao adicionar detect-secrets (pode já estar presente)"
    fi
    
    cd ..
}

add_extra_deps() {
    local project_info=$1
    local project=$(echo "$project_info" | cut -d: -f1)
    local deps=$(echo "$project_info" | cut -d: -f2)
    local project_path="./$project"
    
    echo "📁 Adicionando dependências extras em: $project"
    
    if [ ! -d "$project_path" ]; then
        echo "❌ Projeto $project não encontrado"
        return 1
    fi
    
    cd "$project_path"
    
    # Converter string de dependências em array
    IFS=',' read -ra DEPS_ARRAY <<< "$deps"
    
    for dep in "${DEPS_ARRAY[@]}"; do
        # Verificar se a dependência já está presente
        if grep -q "$dep" pyproject.toml; then
            echo "✅ $dep já presente em $project"
            continue
        fi
        
        # Adicionar dependência
        echo "📦 Adicionando: $dep"
        if poetry add --group dev "$dep" 2>/dev/null; then
            echo "✅ $dep adicionado com sucesso"
        else
            echo "⚠️ Falha ao adicionar $dep"
        fi
    done
    
    cd ..
}

# Contadores
TOTAL=0
SUCCESS=0
FAILED=0

# Adicionar detect-secrets nos projetos que precisam
echo "🔒 Adicionando detect-secrets..."
for project in "${PROJECTS_NEEDING_DETECT_SECRETS[@]}"; do
    TOTAL=$((TOTAL + 1))
    if add_detect_secrets "$project"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

# Adicionar dependências extras
echo "📦 Adicionando dependências extras..."
for project_info in "${PROJECTS_NEEDING_EXTRA_DEPS[@]}"; do
    TOTAL=$((TOTAL + 1))
    if add_extra_deps "$project_info"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

echo "🎉 Adição de dependências concluída!"
echo "📊 Resumo:"
echo "   - Total de projetos processados: $TOTAL"
echo "   - Sucessos: $SUCCESS"
echo "   - Falhas: $FAILED"

if [ $FAILED -gt 0 ]; then
    echo "⚠️ Alguns projetos falharam. Verifique manualmente."
    exit 1
else
    echo "✅ Todos os projetos processados com sucesso!"
fi 
