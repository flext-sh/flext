#!/bin/bash

# Script para verificar se todos os pre-commit hooks estão configurados e funcionando

set -e

echo "🔍 Verificando configuração dos pre-commit hooks..."

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

verify_pre_commit() {
    local project=$1
    local project_path="./$project"
    
    echo "📁 Verificando: $project"
    
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
    
    # Verificar se pre-commit está nas dependências
    if ! grep -q "pre-commit" pyproject.toml; then
        echo "❌ pre-commit não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se detect-secrets está nas dependências
    if ! grep -q "detect-secrets" pyproject.toml; then
        echo "❌ detect-secrets não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se ruff está nas dependências
    if ! grep -q "ruff" pyproject.toml; then
        echo "❌ ruff não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se mypy está nas dependências
    if ! grep -q "mypy" pyproject.toml; then
        echo "❌ mypy não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se bandit está nas dependências
    if ! grep -q "bandit" pyproject.toml; then
        echo "❌ bandit não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se black está nas dependências
    if ! grep -q "black" pyproject.toml; then
        echo "❌ black não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se isort está nas dependências
    if ! grep -q "isort" pyproject.toml; then
        echo "❌ isort não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se vulture está nas dependências
    if ! grep -q "vulture" pyproject.toml; then
        echo "❌ vulture não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se radon está nas dependências
    if ! grep -q "radon" pyproject.toml; then
        echo "❌ radon não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se pytest está nas dependências
    if ! grep -q "pytest" pyproject.toml; then
        echo "❌ pytest não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se commitizen está nas dependências
    if ! grep -q "commitizen" pyproject.toml; then
        echo "❌ commitizen não está nas dependências"
        cd ..
        return 1
    fi
    
    # Verificar se os hooks estão instalados (para submódulos Git)
    local hooks_installed=false
    
    # Verificar se é um submódulo Git
    if [ -f ".git" ] && grep -q "gitdir:" .git; then
        # É um submódulo, verificar no diretório do submódulo
        local gitdir=$(grep "gitdir:" .git | cut -d' ' -f2)
        if [ -f "$gitdir/hooks/pre-commit" ]; then
            hooks_installed=true
        fi
    elif [ -d ".git/hooks" ] && [ -f ".git/hooks/pre-commit" ]; then
        # É um repositório Git normal
        hooks_installed=true
    fi
    
    if [ "$hooks_installed" = false ]; then
        echo "⚠️ Pre-commit hooks não instalados (execute: poetry run pre-commit install)"
    else
        echo "✅ Pre-commit hooks instalados"
    fi
    
    # Verificar se poetry.lock existe
    if [ ! -f "poetry.lock" ]; then
        echo "⚠️ poetry.lock não encontrado (execute: poetry lock)"
    fi
    
    cd ..
    echo "✅ $project configurado corretamente"
}

# Contadores
TOTAL=0
SUCCESS=0
FAILED=0
WARNINGS=0

# Verificar cada projeto
for project in "${PYTHON_PROJECTS[@]}"; do
    TOTAL=$((TOTAL + 1))
    if verify_pre_commit "$project"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

echo "🎉 Verificação de pre-commit hooks concluída!"
echo "📊 Resumo:"
echo "   - Total de projetos: $TOTAL"
echo "   - Sucessos: $SUCCESS"
echo "   - Falhas: $FAILED"

if [ $FAILED -gt 0 ]; then
    echo "❌ Alguns projetos têm problemas de configuração"
    exit 1
else
    echo "✅ Todos os projetos estão configurados corretamente!"
fi

echo ""
echo "💡 Para instalar os hooks em projetos que não os têm:"
echo "   cd <projeto> && poetry run pre-commit install"
echo ""
echo "💡 Para testar os hooks:"
echo "   cd <projeto> && poetry run pre-commit run --all-files" 
