#!/bin/bash
# Test script para demonstrar as cores do Makefile

echo "=== Teste de Cores do Makefile ==="
echo ""

echo "1. Testando com cores habilitadas (padrão):"
make help | head -5
echo ""

echo "2. Testando com cores desabilitadas (NO_COLOR=1):"
NO_COLOR=1 make help | head -5
echo ""

echo "3. Testando comando com cores:"
make list-projects | head -5
echo ""

echo "4. Testando comando sem cores:"
NO_COLOR=1 make list-projects | head -5
echo ""

echo "=== Teste concluído ===" 
