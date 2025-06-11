#!/bin/bash
# Script para verificar se as variáveis WMS_ estão presentes no ambiente
echo "===== Verificando variáveis WMS_ ====="
env | grep -i WMS_ || echo "Nenhuma variável WMS_ encontrada"
echo
echo "===== Variáveis de ambiente geradas automaticamente pelo Cursor ====="
echo "Para desativar esse comportamento, adicione a seguinte configuração:"
echo "Abra o VSCode/Cursor > Settings > Pesquise por 'terminal.integrated.inheritEnv' > Desative essa opção"
echo "OU"
echo "Crie um arquivo .internal.invalid ao invés de .env, que não será carregado automaticamente" 
