#!/bin/bash

echo "🚀 Validando API FLEXT Unificada"
echo "================================"

# Iniciar servidor em background na porta 8081
./flext &
SERVER_PID=$!

# Aguardar servidor iniciar
sleep 2

# Testar health endpoint
echo "1. Testando Health Check:"
curl -s http://localhost:8081/health | jq .

# Testar endpoint raiz
echo -e "\n2. Testando Endpoint Raiz:"
curl -s http://localhost:8081/ | jq .

# Criar pipeline
echo -e "\n3. Criando Pipeline:"
PIPELINE_RESPONSE=$(curl -s -X POST http://localhost:8081/api/v1/pipelines \
	-H "Content-Type: application/json" \
	-d '{
    "name": "Pipeline de Teste",
    "description": "Pipeline para validação da API",
    "tags": ["test", "validation"]
  }')
echo $PIPELINE_RESPONSE | jq .
PIPELINE_ID=$(echo $PIPELINE_RESPONSE | jq -r .id)

# Registrar plugin
echo -e "\n4. Registrando Plugin:"
PLUGIN_RESPONSE=$(curl -s -X POST http://localhost:8081/api/v1/plugins \
	-H "Content-Type: application/json" \
	-d '{
    "name": "Plugin de Teste",
    "type": "source",
    "version": "1.0.0",
    "description": "Plugin para validação da API",
    "author": "FLEXT Team",
    "entry_point": "/usr/bin/test-plugin",
    "ports": [
      {
        "name": "input",
        "type": "source",
        "required": true,
        "description": "Porta de entrada"
      }
    ]
  }')
echo $PLUGIN_RESPONSE | jq .
PLUGIN_ID=$(echo $PLUGIN_RESPONSE | jq -r .id)

# Listar pipelines
echo -e "\n5. Listando Pipelines:"
curl -s http://localhost:8081/api/v1/pipelines | jq .

# Listar plugins
echo -e "\n6. Listando Plugins:"
curl -s http://localhost:8081/api/v1/plugins | jq .

# Buscar pipeline criado
echo -e "\n7. Buscando Pipeline por ID:"
curl -s http://localhost:8081/api/v1/pipelines/$PIPELINE_ID | jq .

# Buscar plugin criado
echo -e "\n8. Buscando Plugin por ID:"
curl -s http://localhost:8081/api/v1/plugins/$PLUGIN_ID | jq .

# Adicionar step ao pipeline
echo -e "\n9. Adicionando Step ao Pipeline:"
curl -s -X POST http://localhost:8081/api/v1/pipelines/$PIPELINE_ID/steps \
	-H "Content-Type: application/json" \
	-d "{
    \"name\": \"Step de Teste\",
    \"plugin_id\": \"$PLUGIN_ID\",
    \"configuration\": {
      \"param1\": \"value1\",
      \"param2\": 42
    }
  }" | jq .

# Buscar pipeline atualizado
echo -e "\n10. Pipeline Atualizado com Step:"
curl -s http://localhost:8081/api/v1/pipelines/$PIPELINE_ID | jq .

echo -e "\n✅ Validação da API Completada!"

# Finalizar servidor
kill $SERVER_PID
