#!/bin/bash
# 🔧 SCRIPT DE CORREÇÃO DOS 33 REPOSITÓRIOS GIT
# Execute este script para corrigir problemas críticos em todos os repositórios

set -e

echo "🚀 INICIANDO CORREÇÃO DOS 33 REPOSITÓRIOS GIT"
echo "============================================="

# ========================================
# 1. LIMPEZA DE ARQUIVOS CRÍTICOS (.env)
# ========================================
echo ""
echo "🚨 STEP 1: REMOVENDO ARQUIVOS .env CRÍTICOS"
echo "-------------------------------------------"

# Workspace principal
if [ -f ".env" ]; then
    echo "❌ Removendo .env do workspace principal..."
    rm -f .env
fi

# algar-oud-mig
if [ -f "algar-oud-mig/.env" ]; then
    echo "❌ Removendo .env do algar-oud-mig..."
    rm -f algar-oud-mig/.env
    rm -f algar-oud-mig/.env.bak
    rm -f algar-oud-mig/.env.test
fi

echo "✅ Arquivos .env removidos com segurança"

# ========================================
# 2. LIMPEZA DE ARTEFATOS TEMPORÁRIOS
# ========================================
echo ""
echo "🧹 STEP 2: LIMPANDO ARTEFATOS TEMPORÁRIOS"
echo "-----------------------------------------"

# Documentação temporária CLAUDE
echo "📄 Removendo documentação temporária..."
rm -f CLAUDE*.md
rm -f DOCUMENTATION_*.md
rm -f DUPLICATE_*.md
rm -f FLEXT_*.md
rm -f GENSIM_*.md
rm -f LINT_*.md
rm -f CURSOR_*.md

# Logs e análises
echo "📊 Removendo logs e análises..."
rm -f *.log
rm -f *.xml
rm -f ruff_violations*.json
rm -f test_failures.log

# Backups e logs do sistema
echo "🗂️ Removendo backups e logs do sistema..."
rm -rf .flext_backups/
rm -rf .flext_logs/
rm -rf .benchmarks/
rm -rf .logfire/

echo "✅ Artefatos temporários removidos"

# ========================================
# 3. CORREÇÃO DO .gitignore PRINCIPAL
# ========================================
echo ""
echo "📝 STEP 3: CORRIGINDO .gitignore PRINCIPAL"
echo "------------------------------------------"

# Adicionar regras críticas ao .gitignore se não existirem
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore
grep -q "^\*\*/\.env\*$" .gitignore || echo "**/.env*" >> .gitignore
grep -q "^CLAUDE\*\.md$" .gitignore || echo "CLAUDE*.md" >> .gitignore
grep -q "^\.flext_backups/$" .gitignore || echo ".flext_backups/" >> .gitignore
grep -q "^\.flext_logs/$" .gitignore || echo ".flext_logs/" >> .gitignore

echo "✅ .gitignore principal corrigido"

# ========================================
# 4. STATUS DOS 33 REPOSITÓRIOS
# ========================================
echo ""
echo "📊 STEP 4: STATUS DOS 33 REPOSITÓRIOS"
echo "-------------------------------------"

echo "🔍 Verificando status dos submódulos..."
git submodule status | head -10

echo ""
echo "📦 Contagem total:"
echo "Workspace: 1"
echo "Submódulos: $(git submodule status | wc -l)"
echo "Total: $((1 + $(git submodule status | wc -l)))"

# ========================================
# 5. VERIFICAÇÃO DE ARQUIVOS PROBLEMÁTICOS
# ========================================
echo ""
echo "🔍 STEP 5: VERIFICAÇÃO FINAL"
echo "----------------------------"

echo "❌ Verificando se ainda existem arquivos .env:"
find . -name ".env*" -type f | head -5

echo ""
echo "📄 Verificando se ainda existem CLAUDE*.md:"
find . -name "CLAUDE*.md" -type f | head -5

echo ""
echo "🗂️ Verificando se ainda existem backups:"
find . -name ".flext_backups" -type d | head -3

# ========================================
# 6. COMANDOS PARA COMMITS SEGUROS
# ========================================
echo ""
echo "✅ CORREÇÃO CONCLUÍDA!"
echo "====================="
echo ""
echo "📌 PRÓXIMOS PASSOS MANUAIS:"
echo ""
echo "1. EXECUTE O RSYNC CORRIGIDO:"
echo "   rsync -rv --exclude='**/.env*' --exclude='**/CLAUDE*.md' [...] flext.bkp/ flext/"
echo ""
echo "2. VERIFIQUE O STATUS:"
echo "   git status"
echo ""
echo "3. ADICIONE APENAS ARQUIVOS SEGUROS:"
echo "   git add Makefile Makefile.build gopy.mod .gitignore"
echo ""
echo "4. COMMIT SEGURO:"
echo "   git commit -m 'fix: cleaned artifacts and secured .env files'"
echo ""
echo "5. VERIFIQUE SUBMÓDULOS:"
echo "   git submodule foreach 'git status'"
echo ""
echo "⚠️  NUNCA execute 'git add .' sem verificar os arquivos!"
echo ""
echo "📋 Para mais detalhes, consulte: GIT_ANALYSIS_33_REPOS.md" 
