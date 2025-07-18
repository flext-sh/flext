#!/bin/bash

# MyPy check script - analisa apenas as pastas src de todos os projetos
set -e

echo "🔍 Executando MyPy em todas as pastas src..."

# Encontrar todas as pastas src excluindo vendor, .venv, cache e client-b-meltano-native (conflito de namespace)
SRC_DIRS=$(find . -name "src" -type d | grep -v vendor | grep -v ".venv" | grep -v ".mypy_cache" | grep -v "client-b-meltano-native" | sort)

echo "📁 Pastas src encontradas:"
echo "$SRC_DIRS" | sed 's/^/  /'
echo

# Executar mypy com as configurações corretas
exec mypy \
	--config-file=pyproject.toml \
	--explicit-package-bases \
	--namespace-packages \
	$SRC_DIRS \
	"$@"
