#!/bin/bash
# check_venv.sh - Check for virtual environment
# This script verifies if the workspace virtual environment is set up correctly

WORKSPACE_ROOT=$(git -C "$(pwd)" rev-parse --show-toplevel 2>/dev/null || echo "$(pwd)")
VENV_DIR="${WORKSPACE_ROOT}/.venv"

echo "Verificando ambiente virtual..."

# Check if .venv directory exists
if [ -z "$(test -d "${VENV_DIR}" && echo exists)" ]; then
	echo "❌ Diretório ${VENV_DIR} não encontrado"
	echo "Execute 'make setup' ou 'make fix-venv' para criar o ambiente virtual"
	exit 1
fi

# Check if Python interpreter exists
if [ -z "$(test -f "${VENV_DIR}/bin/python" && echo exists)" ]; then
	echo "❌ Python não encontrado em ${VENV_DIR}/bin/python"
	echo "Execute 'make fix-venv' para recriar o ambiente virtual"
	exit 1
fi

# Check if pip exists
if [ -z "$(test -f "${VENV_DIR}/bin/pip" && echo exists)" ]; then
	echo "❌ Pip não encontrado em ${VENV_DIR}/bin/pip"
	echo "Execute 'make fix-venv' para recriar o ambiente virtual"
	exit 1
fi

# Check if poetry is installed
if [ -z "$(command -v poetry)" ]; then
	echo "❌ Poetry não encontrado no PATH"
	echo "Instale o Poetry seguindo as instruções em: https://python-poetry.org/docs/#installation"
	exit 1
fi

# All checks passed
echo "✅ Ambiente virtual verificado e pronto para uso"
exit 0
