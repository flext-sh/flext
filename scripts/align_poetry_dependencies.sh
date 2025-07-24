#!/bin/bash

# Script para alinhar dependências do Poetry com ferramentas do Makefile
# Garante que todas as ferramentas usadas no Makefile estejam no pyproject.toml

set -e

echo "🔧 Alinhando dependências Poetry com ferramentas do Makefile..."

# Dependências essenciais que devem estar em todos os projetos Python
ESSENTIAL_DEPS=(
    "pre-commit"
    "ruff"
    "mypy"
    "bandit"
    "black"
    "isort"
    "vulture"
    "radon"
    "detect-secrets"
    "pytest"
    "pytest-cov"
    "pytest-asyncio"
    "pytest-mock"
    "pytest-xdist"
    "pytest-timeout"
    "pytest-sugar"
    "pytest-clarity"
    "pytest-benchmark"
    "pip-audit"
    "commitizen"
)

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
    "gruponos-meltano-native"
    "algar-oud-mig"
)

# Função para verificar se uma dependência está no pyproject.toml
check_dependency() {
    local dep=$1
    local pyproject_file=$2
    
    # Verificar em diferentes seções do pyproject.toml
    if grep -q "\"$dep\"" "$pyproject_file" || \
       grep -q "'$dep'" "$pyproject_file" || \
       grep -q "^$dep" "$pyproject_file" || \
       grep -q "=.*\"$dep\"" "$pyproject_file"; then
        return 0  # Encontrado
    else
        return 1  # Não encontrado
    fi
}

# Função para adicionar dependência com tratamento de erro
add_dependency() {
    local dep=$1
    local group=${2:-dev}
    
    echo "📦 Adicionando: $dep (grupo: $group)"
    
    # Tentar adicionar com diferentes estratégias
    if poetry add --group "$group" "$dep" 2>/dev/null; then
        echo "✅ $dep adicionado com sucesso"
        return 0
    elif poetry add --group "$group" "$dep" --allow-prereleases 2>/dev/null; then
        echo "✅ $dep adicionado com sucesso (prerelease)"
        return 0
    else
        echo "⚠️ Falha ao adicionar $dep (pode não existir ou ter conflitos)"
        return 1
    fi
}

check_and_add_deps() {
    local project=$1
    local project_path="./$project"
    
    echo "📁 Verificando: $project"
    
    if [ ! -d "$project_path" ]; then
        echo "❌ Projeto $project não encontrado"
        return 1
    fi
    
    if [ ! -f "$project_path/pyproject.toml" ]; then
        echo "❌ pyproject.toml não encontrado em $project"
        return 1
    fi
    
    cd "$project_path"
    
    echo "📦 Verificando dependências essenciais..."
    local missing_essential=()
    
    for dep in "${ESSENTIAL_DEPS[@]}"; do
        if ! check_dependency "$dep" "pyproject.toml"; then
            missing_essential+=("$dep")
        fi
    done
    
    if [ ${#missing_essential[@]} -gt 0 ]; then
        echo "⚠️ Dependências essenciais faltando: ${missing_essential[*]}"
        echo "💡 Adicionando dependências essenciais..."
        
        # Adicionar dependências essenciais em lotes para evitar conflitos
        local added_count=0
        for dep in "${missing_essential[@]}"; do
            if add_dependency "$dep" "dev"; then
                added_count=$((added_count + 1))
            fi
        done
        
        if [ $added_count -gt 0 ]; then
            echo "✅ $added_count dependências essenciais adicionadas"
        fi
    else
        echo "✅ Todas as dependências essenciais presentes"
    fi
    
    # Verificar se há Makefile e alinhar com ferramentas específicas
    if [ -f "Makefile" ]; then
        echo "🔧 Verificando alinhamento com Makefile..."
        
        # Verificar ferramentas específicas mencionadas no Makefile
        local makefile_tools=()
        
        if grep -q "mkdocs" Makefile; then
            makefile_tools+=("mkdocs" "mkdocs-material")
        fi
        
        if grep -q "sphinx" Makefile; then
            makefile_tools+=("sphinx" "sphinx-rtd-theme")
        fi
        
        if grep -q "coverage" Makefile; then
            makefile_tools+=("pytest-cov")
        fi
        
        if grep -q "security" Makefile; then
            makefile_tools+=("bandit" "pip-audit" "detect-secrets")
        fi
        
        if grep -q "complexity" Makefile; then
            makefile_tools+=("radon")
        fi
        
        if grep -q "dead.*code" Makefile; then
            makefile_tools+=("vulture")
        fi
        
        # Verificar e adicionar ferramentas específicas do Makefile
        for tool in "${makefile_tools[@]}"; do
            if ! check_dependency "$tool" "pyproject.toml"; then
                add_dependency "$tool" "dev" || true
            fi
        done
    fi
    
    # Verificar se há configurações específicas que precisam de dependências
    if [ -f "mkdocs.yml" ] && ! check_dependency "mkdocs" "pyproject.toml"; then
        echo "📚 Adicionando dependências MkDocs..."
        add_dependency "mkdocs" "dev" || true
        add_dependency "mkdocs-material" "dev" || true
    fi
    
    if [ -f "docs/conf.py" ] && ! check_dependency "sphinx" "pyproject.toml"; then
        echo "📚 Adicionando dependências Sphinx..."
        add_dependency "sphinx" "dev" || true
        add_dependency "sphinx-rtd-theme" "dev" || true
    fi
    
    # Verificar se há testes que precisam de dependências específicas
    if [ -d "tests" ]; then
        local test_deps=()
        
        # Verificar dependências de teste de forma mais robusta
        if find tests -name "*.py" -exec grep -l "hypothesis" {} \; 2>/dev/null | head -1 | grep -q .; then
            test_deps+=("hypothesis")
        fi
        
        if find tests -name "*.py" -exec grep -l "factory" {} \; 2>/dev/null | head -1 | grep -q .; then
            test_deps+=("factory-boy")
        fi
        
        if find tests -name "*.py" -exec grep -l "faker" {} \; 2>/dev/null | head -1 | grep -q .; then
            test_deps+=("faker")
        fi
        
        if find tests -name "*.py" -exec grep -l "django" {} \; 2>/dev/null | head -1 | grep -q .; then
            test_deps+=("django")
        fi
        
        if find tests -name "*.py" -exec grep -l "redis" {} \; 2>/dev/null | head -1 | grep -q .; then
            test_deps+=("redis")
        fi
        
        if find tests -name "*.py" -exec grep -l "ldap" {} \; 2>/dev/null | head -1 | grep -q .; then
            test_deps+=("python-ldap")
        fi
        
        # Adicionar dependências de teste encontradas
        for dep in "${test_deps[@]}"; do
            if ! check_dependency "$dep" "pyproject.toml"; then
                echo "🧪 Adicionando dependência de teste: $dep"
                add_dependency "$dep" "test" || true
            fi
        done
    fi
    
    # Verificar se há configurações de qualidade que precisam de dependências
    if [ -f ".pre-commit-config.yaml" ]; then
        echo "🎣 Verificando dependências do pre-commit..."
        
        local precommit_deps=()
        
        if grep -q "commitizen" .pre-commit-config.yaml; then
            precommit_deps+=("commitizen")
        fi
        
        if grep -q "codespell" .pre-commit-config.yaml; then
            precommit_deps+=("codespell")
        fi
        
        if grep -q "pyupgrade" .pre-commit-config.yaml; then
            precommit_deps+=("pyupgrade")
        fi
        
        if grep -q "autoflake" .pre-commit-config.yaml; then
            precommit_deps+=("autoflake")
        fi
        
        # Adicionar dependências do pre-commit
        for dep in "${precommit_deps[@]}"; do
            if ! check_dependency "$dep" "pyproject.toml"; then
                echo "🎣 Adicionando dependência do pre-commit: $dep"
                add_dependency "$dep" "dev" || true
            fi
        done
    fi
    
    # Atualizar lock file apenas se houve mudanças
    if [ -f "poetry.lock" ]; then
        echo "🔒 Atualizando poetry.lock..."
        poetry lock --no-update 2>/dev/null || {
            echo "⚠️ Falha ao atualizar poetry.lock (pode ser normal)"
        }
    fi
    
    cd ..
    echo "✅ $project processado"
}

# Contadores
TOTAL=0
SUCCESS=0
FAILED=0

# Processar cada projeto
for project in "${PYTHON_PROJECTS[@]}"; do
    TOTAL=$((TOTAL + 1))
    if check_and_add_deps "$project"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

echo "🎉 Alinhamento de dependências concluído!"
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
