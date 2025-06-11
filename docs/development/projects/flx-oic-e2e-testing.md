# End-to-End (E2E) Tests for Oracle Integration Cloud

Este diretório contém testes end-to-end (E2E) que se conectam ao ambiente real do Oracle Integration Cloud (OIC) para validar a funcionalidade completa do cliente HTTP.

## 🎯 Objetivo

Os testes E2E têm dois objetivos principais:

1. **Validação Funcional**: Verificar se o cliente funciona corretamente com o ambiente real do OIC
2. **Gravação de Respostas**: Capturar respostas reais da API para criar serviços de mockup para desenvolvimento

## 📋 Pré-requisitos

### 1. Configuração do Ambiente

Copie o arquivo `.env.example` para `.env` e configure com suas credenciais reais do OIC:

```bash
cp .env.example .env
```

Configure as seguintes variáveis no arquivo `.env`:

```bash
# Configuração da Instância OIC
OIC_INSTANCE_ID=sua_instancia_real
OIC_REGION=us-ashburn-1  # ou sua região

# Configuração de Autenticação IDCS
OIC_IDCS_CLIENT_ID=seu_client_id_real
OIC_IDCS_CLIENT_SECRET=seu_client_secret_real
OIC_IDCS_URL=https://sua_instancia.identity.oraclecloud.com
OIC_IDCS_CLIENT_AUD=https://sua_instancia.integration.ocp.oraclecloud.com

# Configurações Opcionais
OIC_TIMEOUT=60
HTTP_MAX_RETRIES=3
LOG_LEVEL=DEBUG
```

### 2. Acesso à Rede

- Conectividade com a Internet para acessar o OIC
- Credenciais válidas do Oracle Integration Cloud
- Permissões adequadas para listar integrações, conexões, etc.

## 🚀 Executando os Testes

### Usando o Script de Execução

O projeto inclui um script conveniente para executar os testes E2E:

```bash
# Executar todos os testes E2E
python run_e2e_tests.py

# Executar com saída verbosa
python run_e2e_tests.py --verbose

# Executar apenas testes específicos
python run_e2e_tests.py -k "integrations"

# Executar apenas testes que gravam respostas
python run_e2e_tests.py --record-only

# Mostrar informações do ambiente
python run_e2e_tests.py --env-info

# Listar testes disponíveis
python run_e2e_tests.py --list-tests
```

### Usando Pytest Diretamente

```bash
# Executar todos os testes E2E
pytest tests/e2e/ -v -m e2e

# Executar um arquivo específico
pytest tests/e2e/test_oic_integrations_e2e.py -v

# Executar com captura de saída
pytest tests/e2e/ -v -s -m e2e
```

## 📊 Suítes de Teste Disponíveis

### 1. `test_oic_integrations_e2e.py`

Testa operações relacionadas a integrações:

- Listagem de integrações
- Paginação de resultados
- Busca de integração específica
- Filtros por status
- Métricas de performance

### 2. `test_oic_connections_e2e.py`

Testa operações relacionadas a conexões:

- Listagem de conexões
- Análise por tipo de conexão
- Status de saúde das conexões
- Paginação de conexões

### 3. `test_oic_monitoring_e2e.py`

Testa monitoramento e verificações de saúde:

- Health check básico
- Dados de monitoramento
- Métricas de performance
- Inventário de packages

### 4. `test_oic_comprehensive_e2e.py`

Testes abrangentes e de stress:

- Workflow completo do OIC
- Operações concorrentes
- Testes de stress e confiabilidade

## 📹 Gravação de Respostas

Os testes E2E gravam automaticamente as respostas da API real para criar serviços de mockup:

### Onde são Gravadas

```
tests/fixtures/recorded_responses/
├── e2e_session_YYYYMMDD_HHMMSS.json      # Sessão completa
├── oic_mockup_service_YYYYMMDD_HHMMSS.py # Serviço mockup gerado
├── get_integrations_YYYYMMDD_HHMMSS_1.json
├── get_connections_YYYYMMDD_HHMMSS_1.json
└── ...
```

### Estrutura das Respostas Gravadas

Cada resposta gravada inclui:

```json
{
  "timestamp": "2024-06-09T17:30:00",
  "operation": "get_integrations",
  "method": "GET",
  "url": "https://***REDACTED***",
  "status_code": 200,
  "request_params": {"limit": 20, "offset": 0},
  "headers": {"content-type": "application/json"},
  "response_data": {...},
  "metadata": {
    "session_id": "20240609_173000",
    "response_type": "paginated_list",
    "item_count": 15
  }
}
```

### Serviço Mockup Gerado

O sistema gera automaticamente um serviço FastAPI baseado nas respostas gravadas:

```python
# Arquivo gerado: oic_mockup_service_YYYYMMDD_HHMMSS.py
from fastapi import FastAPI

app = FastAPI(title="OIC Mockup Service")

@app.get("/get_integrations")
async def get_integrations(response_index: int = 0):
    """Retorna resposta gravada para get_integrations."""
    return mockup_service.get_response_for_operation("get_integrations", response_index)
```

Para executar o serviço mockup:

```bash
python tests/fixtures/recorded_responses/oic_mockup_service_YYYYMMDD_HHMMSS.py
# Serviço disponível em http://localhost:8000
```

## 🛡️ Segurança

### Dados Sensíveis

O sistema automaticamente remove dados sensíveis das gravações:

- **URLs**: Query parameters são mascarados como `***REDACTED***`
- **Headers**: Authorization, API keys, cookies são mascarados
- **Credenciais**: Nunca são incluídas nas gravações

### Exemplo de Redação

```json
{
  "url": "https://instance.integration.ocp.oraclecloud.com/api/v1/integrations?***REDACTED***",
  "headers": {
    "authorization": "***REDACTED***",
    "content-type": "application/json"
  }
}
```

## 📈 Métricas e Relatórios

### Métricas de Performance

Os testes capturam métricas detalhadas:

```json
{
  "operation": "get_integrations",
  "duration_ms": 1250.5,
  "items_retrieved": 25,
  "items_per_second": 20.0,
  "success_rate": 100.0
}
```

### Análises Disponíveis

- **Distribuição de Status**: Análise de status de integrações/conexões
- **Tipos de Conexão**: Classificação por tipos de adapter
- **Performance**: Métricas de latência e throughput
- **Confiabilidade**: Taxa de sucesso e falhas

## 🎭 Usando Mockups para Desenvolvimento

### 1. Geração Automática

Após executar os testes E2E, você terá:

- Dados reais gravados em JSON
- Serviço FastAPI funcional
- Endpoints que espelham a API real

### 2. Integração no Desenvolvimento

```python
# Em seus testes de desenvolvimento
import requests

# Use o serviço mockup em vez da API real
response = requests.get("http://localhost:8000/get_integrations")
integrations = response.json()
```

### 3. CI/CD Pipeline

```yaml
# .github/workflows/test.yml
- name: Start Mockup Service
  run: |
    python tests/fixtures/recorded_responses/latest_mockup_service.py &
    
- name: Run Development Tests
  run: |
    export OIC_BASE_URL=http://localhost:8000
    pytest tests/
```

## 🚨 Solução de Problemas

### Erro de Conectividade

```bash
❌ Error: Connection failed to OIC instance
```

**Soluções**:

1. Verifique suas credenciais no `.env`
2. Confirme conectividade de rede
3. Valide se a instância OIC está ativa

### Erro de Autenticação

```bash
❌ Error: Authentication failed (401)
```

**Soluções**:

1. Verifique `OIC_IDCS_CLIENT_ID` e `OIC_IDCS_CLIENT_SECRET`
2. Confirme se as credenciais não expiraram
3. Teste manualmente a autenticação IDCS

### Testes Pulados

```bash
SKIPPED - E2E tests skipped - real environment not configured
```

**Soluções**:

1. Configure o arquivo `.env` com credenciais reais
2. Execute `python run_e2e_tests.py --env-info` para diagnóstico

## 📝 Contribuindo

### Adicionando Novos Testes

1. Crie um novo arquivo `test_oic_feature_e2e.py`
2. Use os fixtures `e2e_client` e `response_recorder`
3. Marque com `@pytest.mark.e2e`
4. Grave respostas para mockup

### Exemplo de Novo Teste

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_new_feature(
    e2e_client: OracleOicClient,
    response_recorder: E2EResponseRecorder
) -> None:
    """Test new OIC feature."""
    result = await e2e_client.new_feature()
    
    response_recorder.record_response(
        operation="new_feature",
        method="GET",
        url=f"{e2e_client.config.base_url}/api/new_feature",
        status_code=200,
        response_data=result,
    )
    
    assert result is not None
```

## 📞 Suporte

Para questões sobre os testes E2E:

1. Verifique a documentação da API OIC
2. Execute `python run_e2e_tests.py --env-info` para diagnóstico
3. Revise os logs em `logs/flx.log`
4. Consulte as respostas gravadas para debug

---

**Nota**: Os testes E2E são executados contra ambiente real e podem consumir recursos da API. Use com moderação em ambientes de produção.
