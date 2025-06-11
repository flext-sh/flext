#!/usr/bin/env bash
set -e

echo "=== Script de depuração para identificar o erro na linha 137 ==="

# Configurações básicas
WORKSPACE_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${WORKSPACE_ROOT}/.venv"
VENV_BIN="${VENV_DIR}/bin"
PYTHON_VERSION="3.10"

echo "1. Configurações básicas definidas."

# Função simples de log
log() { echo "[LOG] $*"; }
warn() { echo "[WARN] $*"; }
err() { echo "[ERROR] $*"; }
info() { echo "[INFO] $*"; }

echo "2. Funções de log definidas."

# Testar verificação de Python
echo "3. Testando verificações funcionais..."

# Verifica se o Python do ambiente virtual está funcionando
echo "3.1 Verificando Python do ambiente virtual..."
if [ -f "${VENV_BIN}/python" ]; then
    echo "Python existe no path."
else
    echo "Python não existe no path."
fi

echo "3.2 Testando comando Python..."
if [ -f "${VENV_BIN}/python" ] && "${VENV_BIN}/python" --version >/dev/null 2>&1; then
    echo "Python funciona."
else
    echo "Python não funciona."
fi

echo "3.3 Testando comando Poetry..."
if [ -f "${VENV_BIN}/poetry" ] && "${VENV_BIN}/poetry" --version >/dev/null 2>&1; then
    echo "Poetry funciona."
else
    echo "Poetry não funciona."
fi

echo "3.4 Testando verificação de pip..."
if [ -f "${VENV_BIN}/pip" ] && "${VENV_BIN}/pip" --version >/dev/null 2>&1; then
    echo "Pip funciona."
else
    echo "Pip não funciona."
fi

echo "3.5 Testando importação de módulos..."
if [ -f "${VENV_BIN}/python" ]; then
    echo "Tentando importar setuptools e wheel..."
    if "${VENV_BIN}/python" -c 'import setuptools, wheel' >/dev/null 2>&1; then
        echo "Importação bem-sucedida."
    else
        echo "Importação falhou."
    fi
fi

echo "4. Verificações concluídas."

echo "=== Fim da depuração ===" 
