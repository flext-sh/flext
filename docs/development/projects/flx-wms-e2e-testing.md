# WMS E2E Testing Suite

Bateria completa de testes End-to-End (E2E) para o sistema WMS Oracle, conectando no ambiente real e gravando respostas para criação de serviço mockup.

## 🎯 Objetivo

- **Testes E2E**: Validar todas as operações WMS no ambiente real
- **Gravação de Respostas**: Capturar todas as respostas da API real
- **Geração de Mockup**: Criar serviço mockup baseado nas gravações
- **Documentação**: Gerar relatórios completos dos testes

## 📋 Pré-requisitos

1. **Arquivo .env configurado**:

   ```bash
   cp .env.example .env
   # Editar .env com suas credenciais WMS reais
   ```

2. **Variáveis obrigatórias no .env**:

   ```bash
   WMS_URL=https://your-wms-instance.oracle.com
   WMS_USERNAME=your_username
   WMS_PASSWORD=your_password
   WMS_COMPANY_CODE=COMP01
   WMS_FACILITY_CODE=FAC01
   ```

3. **Dependências instaladas**:

   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Execução

### Execução Completa (Recomendado)

```bash
python run_e2e_tests.py
```

### Execução Manual dos Testes

1. **Testes WMS Completos**:

   ```bash
   pytest tests/e2e/test_wms_e2e_complete.py -v -s -m e2e
   ```

2. **Testes CLI**:

   ```bash
   pytest tests/e2e/test_wms_cli_e2e.py -v -s -m e2e
   ```

3. **Todos os Testes E2E**:

   ```bash
   pytest tests/e2e/ -v -s -m e2e
   ```

## 📊 Testes Incluídos

### 1. Testes Completos WMS (`test_wms_e2e_complete.py`)

#### Conectividade

- ✅ Health check do sistema
- ✅ Status do sistema WMS
- ✅ Autenticação e conexão

#### Ciclo de Vida LPN

- ✅ Criação de LPN
- ✅ Recebimento de LPN
- ✅ Indução de LPN
- ✅ Fluxo completo: criar → receber → induzir

#### Operações de Inventário

- ✅ Consulta de inventário
- ✅ Alocação de inventário
- ✅ Liberação de inventário

#### Operações de Picking

- ✅ Confirmação de picking
- ✅ Operações de tarefa

#### Consultas de Objetos

- ✅ Consulta de LPN
- ✅ Consulta de TASK
- ✅ Consulta de ORDER
- ✅ Consulta de LOCATION
- ✅ Consulta de INVENTORY

#### Operações Concorrentes

- ✅ Múltiplas criações simultâneas
- ✅ Teste de performance

#### Cenários de Erro

- ✅ Dados inválidos
- ✅ LPNs inexistentes
- ✅ Tratamento de exceções

#### Benchmarks de Performance

- ✅ Tempo de resposta health check
- ✅ Tempo de resposta system status
- ✅ Métricas de performance

### 2. Testes CLI (`test_wms_cli_e2e.py`)

#### Comandos Básicos

- ✅ Help (`--help`)
- ✅ Version (`--version`)
- ✅ Test connection (`test-connection`)

#### Formatos de Saída

- ✅ JSON format (`--output-format json`)
- ✅ YAML format (`--output-format yaml`)
- ✅ Table format (`--output-format table`)

#### Operações WMS via CLI

- ✅ Criação de LPN (`create-lpn`)
- ✅ Consulta de inventário (`inquiry-inventory`)
- ✅ Status do sistema (`system-status`)
- ✅ Exibir configuração (`show-config`)

#### Tratamento de Erros CLI

- ✅ Comandos inválidos
- ✅ Argumentos ausentes
- ✅ Dados inválidos

#### Operações em Lote

- ✅ Scripts bash com múltiplos comandos
- ✅ Processamento em lote

## 📁 Estrutura de Arquivos

```
tests/e2e/
├── __init__.py                    # Módulo de testes E2E
├── conftest.py                    # Configurações e fixtures
├── test_wms_e2e_complete.py       # Testes WMS completos
├── test_wms_cli_e2e.py           # Testes CLI
├── mockup_generator.py           # Gerador de serviço mockup
├── pytest.ini                    # Configuração pytest
├── README.md                     # Esta documentação
└── recordings/                   # Gravações das respostas
    ├── create_lpn_20240101_120000.json
    ├── receive_lpn_20240101_120001.json
    ├── system_status_20240101_120002.json
    └── wms_session_20240101_120000.json
```

## 🎥 Gravação de Respostas

### Automática

Todas as respostas são automaticamente gravadas durante os testes em:

- `tests/e2e/recordings/`

### Estrutura das Gravações

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "operation": "create_lpn",
  "request": {
    "lpn_nbr": "E2E_LPN_20240101_120000",
    "qty": 10,
    "item_code": "E2E_ITEM_20240101_120000",
    "location_barcode": "E2E_LOC_20240101_120000"
  },
  "response": {
    "lpn_id": "LPN_001",
    "status": "CREATED",
    "created_at": "2024-01-01T12:00:00"
  },
  "status_code": 200,
  "headers": {},
  "session_id": "20240101_120000"
}
```

## 🛠️ Geração de Serviço Mockup

### Automática

Após os testes, o serviço mockup é gerado automaticamente:

```bash
python run_e2e_tests.py
```

### Manual

```bash
python tests/e2e/mockup_generator.py tests/e2e/recordings --output wms_mockup_service
```

### Estrutura do Mockup

```
wms_mockup_service/
├── main.py                       # Aplicação FastAPI
├── mockup_generator.py           # Gerador de mockup
├── requirements.txt              # Dependências
├── Dockerfile                    # Container Docker
├── docker-compose.yml            # Orquestração
├── start_mockup.sh              # Script de inicialização
├── README.md                     # Documentação do mockup
└── recordings/                   # Cópia das gravações
```

### Executar Mockup

```bash
cd wms_mockup_service
python main.py
```

Serviço disponível em: <http://localhost:8888>

### Endpoints do Mockup

- `GET /` - Informações do serviço
- `GET /health` - Health check
- `GET /recordings` - Listar gravações
- `GET /recordings/{operation}` - Gravação específica
- `POST /wms/lgfapi/v10/*` - Endpoints WMS

## 📈 Relatórios

### Relatório Automático

Gerado em: `E2E_TEST_REPORT.md`

### Conteúdo

- ✅ Resultados dos testes
- ✅ Lista de gravações
- ✅ Instruções do mockup
- ✅ Estatísticas de performance
- ✅ Logs de erro

## 🐳 Docker Support

### Construir Mockup

```bash
cd wms_mockup_service
docker-compose up -d
```

### Serviços

- **wms-mockup**: Serviço mockup (porta 8888)
- **nginx**: Proxy reverso (portas 80/443)

## 🔧 Configuração Avançada

### Variáveis de Ambiente E2E

```bash
E2E_RECORD_RESPONSES=true           # Gravar respostas
E2E_OUTPUT_DIR=tests/e2e/recordings # Diretório de gravação
E2E_MOCK_SERVER_PORT=8888          # Porta do mockup
E2E_ENVIRONMENT=test               # Ambiente de teste
```

### Timeout Customizado

```bash
pytest tests/e2e/ --timeout=600    # 10 minutos
```

### Filtros de Teste

```bash
pytest tests/e2e/ -m "e2e and not slow"           # Apenas E2E rápidos
pytest tests/e2e/ -m "performance"                # Apenas performance
pytest tests/e2e/ -k "lpn"                       # Apenas testes LPN
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Arquivo .env não encontrado**:

   ```bash
   cp .env.example .env
   # Configurar credenciais
   ```

2. **Credenciais inválidas**:

   ```bash
   # Verificar variáveis no .env
   echo $WMS_USERNAME
   echo $WMS_URL
   ```

3. **Timeout de conexão**:

   ```bash
   # Aumentar timeout no .env
   WMS_TIMEOUT=60
   ```

4. **SSL/TLS errors**:

   ```bash
   # Desabilitar verificação SSL (desenvolvimento)
   WMS_VERIFY_SSL=false
   ```

### Debug Mode

```bash
pytest tests/e2e/ -v -s --tb=long --capture=no
```

### Logs Detalhados

```bash
export WMS_DEBUG_MODE=true
export WMS_LOG_REQUESTS=true
export WMS_LOG_RESPONSES=true
```

## 📝 Exemplos de Uso

### Teste Específico

```bash
pytest tests/e2e/test_wms_e2e_complete.py::TestWmsE2EComplete::test_lpn_lifecycle -v -s
```

### Apenas Testes de Performance

```bash
pytest tests/e2e/ -m performance -v
```

### Gerar Apenas Mockup

```bash
python tests/e2e/mockup_generator.py tests/e2e/recordings
```

### Validar Mockup

```bash
curl http://localhost:8888/health
curl http://localhost:8888/recordings
```

## 🎯 Próximos Passos

1. **Executar os testes**: `python run_e2e_tests.py`
2. **Verificar gravações**: `ls tests/e2e/recordings/`
3. **Iniciar mockup**: `cd wms_mockup_service && python main.py`
4. **Testar mockup**: Acessar <http://localhost:8888>
5. **Ler relatório**: `cat E2E_TEST_REPORT.md`

---

_Esta documentação é atualizada automaticamente durante a execução dos testes E2E._
