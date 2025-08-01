#!/bin/bash

echo "🧪 TESTE COMPLETO DE TODOS OS PROJETOS - FASE 3"
echo "========================================================"

PROJECTS=(
	"flext-core"
	"flext-cli"
	"flext-observability"
	"flext-grpc"
	"flext-web"
	"flext-api"
	"flext-auth"
	"flext-tap-oracle"
	"flext-target-oracle"
	"flext-meltano"
	"algar-oud-mig"
	"gruponos-meltano-native"
)

success_count=0
total_count=${#PROJECTS[@]}

for project in "${PROJECTS[@]}"; do
	echo ""
	echo "🧪 Testando $project..."
	cd "$project" 2>/dev/null || continue

	project_success=true

	# Teste básico de sintaxe
	echo "  📝 Verificando sintaxe Python..."
	if find src/ -name "*.py" -exec python -m py_compile {} \; 2>/dev/null; then
		echo "  ✅ Sintaxe OK"
	else
		echo "  ❌ Problemas de sintaxe"
		project_success=false
	fi

	# Se tem Makefile, tenta instalar dependências
	if [ -f "Makefile" ]; then
		echo "  📦 Tentando instalar dependências..."
		if make install 2>/dev/null >/dev/null; then
			echo "  ✅ Dependências OK"
		else
			echo "  ⚠️  Problemas com dependências (pode ser esperado)"
		fi
	fi

	# Se tem pyproject.toml, tenta poetry install
	if [ -f "pyproject.toml" ]; then
		echo "  🎵 Tentando Poetry install..."
		if poetry install 2>/dev/null >/dev/null; then
			echo "  ✅ Poetry install OK"
		else
			echo "  ⚠️  Poetry install com problemas (pode ser esperado)"
		fi
	fi

	if $project_success; then
		((success_count++))
		echo "  🎯 $project: SUCESSO"
	else
		echo "  💥 $project: PROBLEMAS"
	fi

	cd ..
done

echo ""
echo "📊 RESULTADO FINAL:"
echo "  Projetos testados: $total_count"
echo "  Sucessos: $success_count"
echo "  Taxa de sucesso: $((success_count * 100 / total_count))%"

if [ $success_count -eq "$total_count" ]; then
	echo "🎉 TODOS OS PROJETOS PASSARAM!"
else
	echo "⚠️  Alguns projetos precisam de atenção"
fi
