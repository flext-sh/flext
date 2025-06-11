# tap-wms

Este extrator Meltano para Oracle WMS Cloud (Warehouse Management System) permite extrair dados de entidades e eventos do WMS para uso em pipelines de dados.

## Funcionalidades

- Extração de pedidos (orders) e detalhes
- Extração de alocações de estoque (allocations)
- Suporte a cargas incrementais e captura de alterações  
- Suporte para webhooks via servidor auxiliar
- Exportação de dados via CSV para cargas iniciais de alto volume

## Requisitos

- Python 3.8 ou superior
- Acesso ao Oracle WMS Cloud v25A/25B ou superior
- Credenciais Basic Auth para APIs do WMS
- SFTP server configurado (opcional, para extrações via CSV)

## Instalação

```bash
# Via pip
pip install tap-wms

# Via Meltano
meltano add extractor tap-wms
```

## Configuração

### Configuração Básica

```yaml
# meltano.yml
plugins:
  extractors:
    - name: tap-wms
      variant: custom
      pip_url: tap-wms
      config:
        wms_url: https://tenantname.wms.ocs.oraclecloud.com/env/wms/api
        username: INT_OIC  # Usuário de integração criado no WMS
        password: YOUR_PASSWORD
        start_date: '2023-01-01T00:00:00Z'
```

### Configuração Avançada

```yaml
# config.json completo
{
  "wms_url": "https://tenantname.wms.ocs.oraclecloud.com/env/wms/api",
  "username": "INT_OIC",
  "password": "YOUR_PASSWORD",
  "start_date": "2023-01-01T00:00:00Z",
  "company_code": "YOURCO",
  "facility_code": "WH1",
  "batch_size": 100,
  "request_timeout": 300,
  "extraction_mode": "api",  # Opções: "api", "csv", "webhook"
  "sftp_config": {
    "host": "sftp.example.com",
    "port": 22,
    "username": "sftp_user",
    "password": "sftp_password",
    "directory": "/WMSInitialLoad"
  },
  "webhook_config": {
    "listen_port": 5000,
    "endpoint_path": "/wms-events",
    "auth_required": true,
    "webhook_username": "webhook_user",
    "webhook_password": "webhook_password"
  },
  "enable_metadata_columns": true,
  "retry_count": 3,
  "connection_timeout": 60
}
```

## Modos de Extração

Este extrator suporta três modos de extração:

### 1. Modo API (Padrão)

Extrai dados diretamente através das APIs REST do WMS Cloud.

```yaml
config:
  extraction_mode: "api"
```

### 2. Modo CSV (Para Grandes Volumes)

Utiliza exportações CSV via SFTP para cargas iniciais ou grandes volumes de dados. Este modo requer jobs agendados no Meltano que verificam periodicamente a existência de novos arquivos no servidor SFTP:

```yaml
config:
  extraction_mode: "csv"
  sftp_config:
    host: "sftp.example.com"
    port: 22
    username: "sftp_user"
    password: "sftp_password"
    directory: "/WMSInitialLoad"
```

### 3. Modo Webhook (Para Eventos em Tempo Real)

Configura um servidor webhook local para receber eventos do WMS:

```yaml
config:
  extraction_mode: "webhook"
  webhook_config:
    listen_port: 5000
    endpoint_path: "/wms-events"
    auth_required: true
    webhook_username: "webhook_user"
    webhook_password: "webhook_password"
```

Após configurar este modo, você precisará configurar as Output Interfaces no WMS Cloud para apontar para este endpoint.

## Streams Disponíveis

Este extrator fornece as seguintes streams principais:

- **order_hdr**: Cabeçalhos de pedidos
- **order_dtl**: Detalhes de pedidos (linhas)
- **allocations**: Alocações de estoque
- **inventory_history**: Histórico de transações de inventário
- **facilities**: Instalações/armazéns
- **items**: Itens/produtos
- **lpns**: Unidades logísticas
- **locations**: Localizações no armazém

## Configuração no WMS Cloud

Para usar este extrator, você deve configurar no WMS Cloud:

### Para Extração API

- Crie um usuário de integração com permissão `can_run_ws_stage_interface`
- Atribua ao usuário acesso às empresas/facilidades necessárias

### Para Extração Webhook

1. Acesse o menu de Endpoint no WMS (Output Interface Configuration)
2. Configure Output Interfaces para Orders e Allocations:
   - Selecione REST Web Service como protocolo
   - Aponte para o endpoint do seu servidor webhook
   - Configure Basic Auth com as credenciais configuradas
   - Ative as interfaces

## Exemplo com Meltano

### Pipeline Completo

```bash
# Extração inicial via CSV e carregamento no Oracle Database
meltano elt tap-wms target-oracle --job-id=wms_initial_load

# Extração contínua via API
meltano elt tap-wms target-oracle --job-id=wms_daily_sync
```

### Configuração com Agendamento

```yaml
# meltano.yml
schedules:
  - name: wms_daily_sync
    extractor: tap-wms
    loader: target-oracle
    interval: '@daily'
    start_date: 2023-01-01
    config:
      extraction_mode: "api"
```

## Desenvolvimento

Este plugin foi desenvolvido usando o [Meltano SDK](https://sdk.meltano.com/) para garantir compatibilidade e seguir as melhores práticas de construção de extratores.

### Estrutura do Código

```
tap_wms/
├── __init__.py
├── auth.py        # Lógica de autenticação
├── client.py      # Cliente HTTP para API do WMS
├── streams.py     # Definição dos streams de dados
├── webhook.py     # Implementação do servidor webhook
├── csv_reader.py  # Lógica para processamento de CSV
└── tap.py         # Classe principal do extrator
```

## Resolução de Problemas

### Timeout em Grandes Volumes

Para extrações de grande volume, recomendamos:

- Usar o modo `csv` para carga inicial
- Aumentar `request_timeout` e `connection_timeout`
- Reduzir o `batch_size` para valores menores

### Erros de Autenticação

- Verifique se o usuário tem as permissões corretas no WMS
- Confirme que o usuário tem acesso às empresas/facilidades configuradas

### Problemas com Webhook

- Verifique se o servidor webhook está acessível externamente
- Confirme se o firewall permite acesso à porta configurada
- Verifique os logs do servidor para garantir que está recebendo as chamadas

## Formato de Estado e Bookmarks

O extrator mantém estado para permitir extrações incrementais:

```json
{
  "bookmarks": {
    "order_hdr": {
      "modified_date": "2023-06-01T12:34:56Z"
    },
    "allocations": {
      "allocation_time": "2023-06-01T12:34:56Z"
    }
  }
}
```

## Exemplos de Resposta de API

### Exemplo: Order Header

```json
{
  "company_code": "YOURCO",
  "facility_code": "WH1",
  "order_nbr": "ORD12345",
  "order_type": "SO",
  "order_date": "2023-06-01T10:00:00",
  "destination": "STORE123",
  "status": "Created"
}
```
