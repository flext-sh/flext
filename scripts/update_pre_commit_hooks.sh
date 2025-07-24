#!/bin/bash

# Script para atualizar e padronizar todos os pre-commit hooks dos projetos FLEXT
# Alinha com Makefile e Poetry

set -e

echo "🎣 Atualizando pre-commit hooks em todos os projetos FLEXT..."

# Template padrão do pre-commit config
PRE_COMMIT_TEMPLATE='# STRICT Enterprise Pre-commit Configuration
# Zero tolerance for quality violations
# All tools managed by Poetry

minimum_pre_commit_version: "3.5.0"
fail_fast: false
default_stages: [pre-commit, pre-push]
default_language_version:
  python: python3.13

repos:
  # Security scanning FIRST - fail fast on vulnerabilities
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ["--baseline", ".secrets.baseline"]
        exclude: .*\.lock$|.*\.lockb$

  # Poetry-managed tools via local repo
  - repo: local
    hooks:
      # Black formatting (primary formatter)
      - id: black
        name: "⚫ Black Format"
        entry: poetry run black
        language: system
        types: [python]
        require_serial: true
        args: [--check, --diff]

      # Ruff linting and formatting
      - id: ruff-format
        name: "⚡ Ruff Format"
        entry: poetry run ruff format
        language: system
        types: [python]
        require_serial: true
        args: [--check, --diff]

      - id: ruff-lint
        name: "🔥 Ruff Lint (17 categories)"
        entry: poetry run ruff check
        language: system
        types: [python]
        require_serial: true
        args: [--fix, --exit-non-zero-on-fix]

      # isort import sorting
      - id: isort
        name: "📦 Import Sort"
        entry: poetry run isort
        language: system
        types: [python]
        require_serial: true
        args: [--check-only, --diff]

      # MyPy type checking
      - id: mypy
        name: "🛡️ MyPy Strict"
        entry: poetry run mypy
        language: system
        types: [python]
        require_serial: true
        pass_filenames: false
        args: [src/, tests/, --config-file=pyproject.toml]

      # Bandit security
      - id: bandit
        name: "🔒 Bandit Security"
        entry: poetry run bandit
        language: system
        types: [python]
        require_serial: true
        args: [-r, src/, --severity-level=medium]
        exclude: tests/

      # Vulture dead code
      - id: vulture
        name: "🦅 Dead Code Detection"
        entry: poetry run vulture
        language: system
        types: [python]
        pass_filenames: false
        args: [src/, --min-confidence=80]

      # Radon complexity
      - id: radon-cc
        name: "📊 Cyclomatic Complexity"
        entry: poetry run radon cc
        language: system
        types: [python]
        pass_filenames: false
        args: [src/, -a, -nb, --total-average]

      - id: radon-mi
        name: "📊 Maintainability Index"
        entry: poetry run radon mi
        language: system
        types: [python]
        pass_filenames: false
        args: [src/, -nb]

  # YAML/TOML/JSON validation
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
        name: "📋 YAML Syntax Check"
      - id: check-toml
        name: "📋 TOML Syntax Check"
      - id: check-json
        name: "📋 JSON Syntax Check"
      - id: end-of-file-fixer
        name: "📄 EOF Fixer"
      - id: trailing-whitespace
        name: "✂️ Trailing Whitespace"
      - id: check-added-large-files
        name: "📦 Large File Check"
        args: [--maxkb=1000]
      - id: check-case-conflict
        name: "🔤 Case Conflict Check"
      - id: check-merge-conflict
        name: "⚔️ Merge Conflict Check"
      - id: mixed-line-ending
        name: "📏 Line Ending Check"
        args: [--fix=lf]
      - id: debug-statements
        name: "🐛 Debug Statement Check"

  # Python-specific checks
  - repo: https://github.com/pre-commit/pygrep-hooks
    rev: v1.10.0
    hooks:
      - id: python-check-blanket-noqa
        name: "🚫 Blanket noqa Check"
      - id: python-check-blanket-type-ignore
        name: "🚫 Blanket type: ignore Check"
      - id: python-no-eval
        name: "🚫 No eval() Check"
      - id: python-no-log-warn
        name: "⚠️ No log.warn Check"
      - id: python-use-type-annotations
        name: "📝 Type Annotations Check"

  # Commit message validation via Poetry
  - repo: local
    hooks:
      - id: commitizen
        name: "💬 Commit Message Check"
        entry: poetry run cz check
        language: system
        stages: [commit-msg]
        pass_filenames: false
        args: [--commit-msg-file]

# CI configuration
ci:
  autofix_prs: false # No automatic fixes - must be intentional
  autoupdate_schedule: weekly
  skip: [
      # Local Poetry hooks do not work in CI
      black,
      ruff-format,
      ruff-lint,
      isort,
      mypy,
      bandit,
      vulture,
      radon-cc,
      radon-mi,
      commitizen,
    ]
  submodules: false'

# Lista de projetos Python para atualizar
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

# Lista de projetos Go para atualizar (se houver)
GO_PROJECTS=(
    "flexcore"
)

update_pre_commit() {
    local project=$1
    local project_path="./$project"
    
    echo "📁 Atualizando: $project"
    
    if [ ! -d "$project_path" ]; then
        echo "❌ Projeto $project não encontrado"
        return 1
    fi
    
    cd "$project_path"
    
    # Verificar se é um projeto Python
    if [ -f "pyproject.toml" ]; then
        echo "🐍 Projeto Python detectado"
        
        # Criar/atualizar .pre-commit-config.yaml
        echo "$PRE_COMMIT_TEMPLATE" > .pre-commit-config.yaml
        
        # Verificar se poetry está configurado
        if [ -f "pyproject.toml" ]; then
            echo "📦 Verificando dependências Poetry..."
            
            # Verificar se pre-commit está nas dependências
            if ! grep -q "pre-commit" pyproject.toml; then
                echo "⚠️ pre-commit não encontrado em pyproject.toml"
                echo "💡 Execute: poetry add --group dev pre-commit"
            fi
            
            # Verificar outras dependências importantes
            local missing_deps=()
            
            if ! grep -q "ruff" pyproject.toml; then
                missing_deps+=("ruff")
            fi
            
            if ! grep -q "mypy" pyproject.toml; then
                missing_deps+=("mypy")
            fi
            
            if ! grep -q "bandit" pyproject.toml; then
                missing_deps+=("bandit")
            fi
            
            if ! grep -q "black" pyproject.toml; then
                missing_deps+=("black")
            fi
            
            if ! grep -q "isort" pyproject.toml; then
                missing_deps+=("isort")
            fi
            
            if ! grep -q "vulture" pyproject.toml; then
                missing_deps+=("vulture")
            fi
            
            if ! grep -q "radon" pyproject.toml; then
                missing_deps+=("radon")
            fi
            
            if ! grep -q "detect-secrets" pyproject.toml; then
                missing_deps+=("detect-secrets")
            fi
            
            if [ ${#missing_deps[@]} -gt 0 ]; then
                echo "⚠️ Dependências faltando: ${missing_deps[*]}"
                echo "💡 Execute: poetry add --group dev ${missing_deps[*]}"
            fi
        fi
        
        # Instalar pre-commit hooks se poetry estiver disponível
        if command -v poetry &> /dev/null; then
            echo "🎣 Instalando pre-commit hooks..."
            poetry run pre-commit install || {
                echo "❌ Falha ao instalar pre-commit hooks"
                cd ..
                return 1
            }
            echo "✅ Pre-commit hooks instalados"
        else
            echo "⚠️ Poetry não encontrado, pulando instalação de hooks"
        fi
        
    elif [ -f "go.mod" ]; then
        echo "🐹 Projeto Go detectado"
        
        # Para projetos Go, criar configuração específica
        cat > .pre-commit-config.yaml << 'EOF'
# Go Pre-commit Configuration
minimum_pre_commit_version: "3.5.0"
fail_fast: false
default_stages: [pre-commit, pre-push]

repos:
  # Go-specific hooks
  - repo: https://github.com/dnephin/pre-commit-golang
    rev: v0.5.1
    hooks:
      - id: go-fmt
        name: "🐹 Go Format"
      - id: go-imports
        name: "📦 Go Imports"
      - id: go-vet
        name: "🔍 Go Vet"
      - id: go-build
        name: "🔨 Go Build"
      - id: go-test
        name: "🧪 Go Test"
      - id: go-mod-tidy
        name: "🧹 Go Mod Tidy"
      - id: golangci-lint
        name: "🔥 GolangCI Lint"

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
      - id: check-json
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files
        args: [--maxkb=1000]
      - id: check-case-conflict
      - id: check-merge-conflict
      - id: mixed-line-ending
        args: [--fix=lf]
      - id: debug-statements

ci:
  autofix_prs: false
  autoupdate_schedule: weekly
EOF
        
        echo "✅ Configuração Go criada"
        
    else
        echo "❓ Tipo de projeto não reconhecido (sem pyproject.toml ou go.mod)"
        cd ..
        return 1
    fi
    
    cd ..
    echo "✅ $project atualizado"
}

# Contadores
TOTAL=0
SUCCESS=0
FAILED=0

# Atualizar projetos Python
echo "🐍 Atualizando projetos Python..."
for project in "${PYTHON_PROJECTS[@]}"; do
    TOTAL=$((TOTAL + 1))
    if update_pre_commit "$project"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

# Atualizar projetos Go
echo "🐹 Atualizando projetos Go..."
for project in "${GO_PROJECTS[@]}"; do
    TOTAL=$((TOTAL + 1))
    if update_pre_commit "$project"; then
        SUCCESS=$((SUCCESS + 1))
    else
        FAILED=$((FAILED + 1))
    fi
done

echo "🎉 Atualização de pre-commit hooks concluída!"
echo "📊 Resumo:"
echo "   - Total de projetos: $TOTAL"
echo "   - Sucessos: $SUCCESS"
echo "   - Falhas: $FAILED"

if [ $FAILED -gt 0 ]; then
    echo "⚠️ Alguns projetos falharam. Verifique manualmente."
    exit 1
else
    echo "✅ Todos os projetos atualizados com sucesso!"
fi 
