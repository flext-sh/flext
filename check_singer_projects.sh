#!/bin/bash
# Verificação rápida dos projetos Singer/Meltano

echo "=== VERIFICAÇÃO PROJETOS SINGER/MELTANO ==="
echo ""

SINGER_PROJECTS=(
    "flext-tap-ldap"
    "flext-tap-oracle-oic" 
    "flext-tap-oracle-wms"
    "flext-target-ldap"
    "flext-target-oracle-oic"
    "flext-target-oracle-wms"
    "flext-dbt-ldap"
    "flext-meltano"
)

for project in "${SINGER_PROJECTS[@]}"; do
    if [ -d "$project" ]; then
        echo "----------------------------------------"
        echo "📦 $project"
        cd "$project"
        
        # Verifica se tem Makefile
        if [ -f "Makefile" ]; then
            # Tenta rodar teste com timeout curto
            if timeout 10 make test > /tmp/test_output.tmp 2>&1; then
                passed=$(grep -E "passed|PASSED" /tmp/test_output.tmp | tail -1)
                if [ -n "$passed" ]; then
                    echo "✅ TESTES PASSARAM: $passed"
                else
                    echo "✅ Comando completou (verificar output)"
                fi
            else
                if grep -q "collected 0 items" /tmp/test_output.tmp; then
                    echo "⚠️  SEM TESTES"
                elif grep -q "ImportError\|ModuleNotFoundError" /tmp/test_output.tmp; then
                    error=$(grep -E "ImportError|ModuleNotFoundError" /tmp/test_output.tmp | head -1)
                    echo "❌ IMPORT ERROR: $error"
                elif grep -q "FAILED" /tmp/test_output.tmp; then
                    failed=$(grep "failed" /tmp/test_output.tmp | tail -1)
                    echo "❌ TESTES FALHARAM: $failed"
                else
                    echo "⏱️  TIMEOUT ou outro erro"
                fi
            fi
        else
            echo "❌ Sem Makefile"
        fi
        
        cd ..
    else
        echo "❌ Diretório $project não existe"
    fi
done

echo ""
echo "=== FIM DA VERIFICAÇÃO ==="
rm -f /tmp/test_output.tmp