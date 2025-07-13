#!/bin/bash
# Script INFORMATIVO para verificar estado real dos testes

echo "=== VERIFICAÇÃO DE TESTES - FLEXT WORKSPACE ==="
echo "Data: $(date)"
echo ""

for project in flext-*; do
    if [ -d "$project" ] && [ -f "$project/Makefile" ]; then
        echo "----------------------------------------"
        echo "📦 Projeto: $project"
        cd "$project"
        
        # Tenta rodar os testes
        if timeout 30 make test > test_output.tmp 2>&1; then
            # Sucesso
            passed=$(grep -E "passed|PASSED" test_output.tmp | tail -1)
            echo "✅ TESTES PASSARAM: $passed"
        else
            # Falhou - vamos ver por quê
            if grep -q "collected 0 items" test_output.tmp; then
                echo "⚠️  SEM TESTES"
            elif grep -q "ERROR" test_output.tmp; then
                error=$(grep -A2 "ERROR" test_output.tmp | head -3)
                echo "❌ ERRO: $error"
            elif grep -q "FAILED" test_output.tmp; then
                failed=$(grep "failed" test_output.tmp | tail -1)
                echo "❌ TESTES FALHARAM: $failed"
            elif grep -q "Required test coverage" test_output.tmp; then
                passed=$(grep -E "passed|PASSED" test_output.tmp | tail -1)
                echo "✅ TESTES PASSARAM (coverage baixa): $passed"
            else
                echo "❓ ESTADO DESCONHECIDO"
            fi
        fi
        
        rm -f test_output.tmp
        cd ..
    fi
done

echo ""
echo "=== FIM DA VERIFICAÇÃO ==="