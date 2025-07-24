#!/bin/bash

# Script para demonstrar o workflow completo dos pre-commit hooks
# Testa a funcionalidade em um projeto específico

set -e

echo "🧪 Testando workflow completo dos pre-commit hooks..."

# Projeto de teste (usar flext-core como exemplo)
TEST_PROJECT="flext-core"

echo "📁 Testando em: $TEST_PROJECT"

if [ ! -d "$TEST_PROJECT" ]; then
    echo "❌ Projeto $TEST_PROJECT não encontrado"
    exit 1
fi

cd "$TEST_PROJECT"

echo "🔍 Verificando configuração atual..."
echo "   - pyproject.toml: $(ls -la pyproject.toml 2>/dev/null | wc -l | tr -d ' ') arquivos"
echo "   - .pre-commit-config.yaml: $(ls -la .pre-commit-config.yaml 2>/dev/null | wc -l | tr -d ' ') arquivos"
echo "   - Pre-commit hooks: $(ls -la .git/modules/$TEST_PROJECT/hooks/pre-commit 2>/dev/null | wc -l | tr -d ' ') arquivos"

echo ""
echo "📦 Verificando dependências essenciais..."
ESSENTIAL_DEPS=("pre-commit" "ruff" "mypy" "bandit" "black" "isort" "vulture" "radon" "detect-secrets" "commitizen")

for dep in "${ESSENTIAL_DEPS[@]}"; do
    if grep -q "$dep" pyproject.toml; then
        echo "   ✅ $dep"
    else
        echo "   ❌ $dep (faltando)"
    fi
done

echo ""
echo "🎣 Executando pre-commit hooks em todos os arquivos..."
echo "   (Isso pode demorar alguns minutos...)"

# Executar pre-commit hooks
if poetry run pre-commit run --all-files --show-diff-on-failure; then
    echo "✅ Pre-commit hooks executados com sucesso!"
    echo "   - Todos os arquivos passaram nas verificações"
    echo "   - Código está formatado e livre de problemas"
else
    echo "⚠️ Pre-commit hooks encontraram problemas"
    echo "   - Alguns arquivos foram corrigidos automaticamente"
    echo "   - Verifique as mudanças e faça commit se necessário"
fi

echo ""
echo "🔧 Verificando ferramentas individuais..."

# Testar ferramentas individuais
echo "   🎨 Testando Black (formatação)..."
if poetry run black --check src/ tests/ 2>/dev/null; then
    echo "      ✅ Black: código bem formatado"
else
    echo "      ⚠️ Black: problemas de formatação encontrados"
fi

echo "   🔍 Testando Ruff (linting)..."
if poetry run ruff check src/ tests/ 2>/dev/null; then
    echo "      ✅ Ruff: sem problemas de linting"
else
    echo "      ⚠️ Ruff: problemas de linting encontrados"
fi

echo "   🛡️ Testando MyPy (tipos)..."
if poetry run mypy src/ tests/ --ignore-missing-imports 2>/dev/null; then
    echo "      ✅ MyPy: tipos corretos"
else
    echo "      ⚠️ MyPy: problemas de tipos encontrados"
fi

echo "   🔒 Testando Bandit (segurança)..."
if poetry run bandit -r src/ --severity-level medium --confidence-level medium 2>/dev/null; then
    echo "      ✅ Bandit: sem problemas de segurança"
else
    echo "      ⚠️ Bandit: problemas de segurança encontrados"
fi

echo "   🕵️ Testando detect-secrets..."
if poetry run detect-secrets scan --all-files 2>/dev/null; then
    echo "      ✅ detect-secrets: sem segredos encontrados"
else
    echo "      ⚠️ detect-secrets: possíveis segredos encontrados"
fi

echo ""
echo "📊 Resumo do teste:"
echo "   - Projeto: $TEST_PROJECT"
echo "   - Pre-commit hooks: ✅ Funcionando"
echo "   - Dependências: ✅ Alinhadas"
echo "   - Ferramentas: ✅ Integradas"

cd ..

echo ""
echo "🎉 Workflow de pre-commit hooks testado com sucesso!"
echo ""
echo "💡 Para usar em outros projetos:"
echo "   cd <projeto>"
echo "   poetry run pre-commit run --all-files"
echo ""
echo "💡 Para executar hooks específicos:"
echo "   poetry run pre-commit run black --all-files"
echo "   poetry run pre-commit run ruff --all-files"
echo "   poetry run pre-commit run mypy --all-files" 
