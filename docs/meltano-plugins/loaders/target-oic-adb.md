# target-oic-adb

This Meltano loader for Oracle Autonomous Database via Oracle Integration Cloud (OIC) allows loading data into Oracle tables from any Meltano/Singer extractor, using OIC as an intermediate layer.

## Features

- Efficient data loading to Oracle Autonomous Database via OIC
- Simplified Oracle Autonomous Database connection configuration
- Automatic table creation when they don't exist
- Insert, update, merge (upsert) and complete replacement operations
- Bulk loading optimization using Direct Path Insert
- Support for data type transformations and column mapping
- Direct integration with OIC for additional data processing

## Differences from traditional target-oracle

This loader is a specialization of `target-oracle` that uses Oracle Integration Cloud (OIC) as an intermediate layer for connection to Autonomous Database. This provides some advantages:

- **Enhanced security**: Centralized connection managed by OIC
- **Ease of configuration**: Reduces the need for local wallet and complex connectivity configurations
- **Additional processing**: Allows triggering OIC integrations for transformations, validations or data enrichment
- **Centralized monitoring**: View data flows directly in the OIC console
- **Oracle standard**: Follows Oracle's recommended pattern for cloud service integrations

## Requirements

- Python 3.8 or higher
- Oracle Client driver (Python-oracledb)
- Access to Oracle Autonomous Database
- Access to Oracle Integration Cloud (OIC v3)
- Wallet for Oracle Autonomous Database connection (optional if using OIC for direct connection)
- CREATE TABLE, INSERT, UPDATE, DELETE privileges on the database

## Installation

```bash
# Via pip
pip install target-oic-adb

# Via Meltano
meltano add loader target-oic-adb
```

### Oracle Driver Installation

Oracle drivers are required for database connection:

#### Using Python-oracledb (recommended)

```bash
pip install oracledb
```

For Thick Client mode, you also need to install Oracle Instant Client.

## Configuration

### Basic Configuration

```yaml
# meltano.yml
plugins:
  loaders:
    - name: target-oic-adb
      variant: custom
      pip_url: target-oic-adb
      config:
        connection_type: autonomous
        user: ADMIN
        password: your_password
        service_name: dbname_low
        wallet_location: /path/to/wallet.zip
        wallet_password: wallet_password
        default_target_schema: WMSSTAGE
        oic_config:
          url: "https://your-instance.integration.ocp.oraclecloud.com"
          auth_method: "basic"
          username: "oic_user"
          password: "oic_password"
```

### OAuth2 Configuration for OIC

```yaml
# meltano.yml
plugins:
  loaders:
    - name: target-oic-adb
      variant: custom
      pip_url: target-oic-adb
      config:
        connection_type: autonomous
        user: ADMIN
        password: your_password
        service_name: dbname_low
        wallet_location: /path/to/wallet.zip
        wallet_password: wallet_password
        default_target_schema: WMSSTAGE
        oic_config:
          url: "https://your-instance.integration.ocp.oraclecloud.com"
          auth_method: "oauth2"
          client_id: "your_client_id"
          client_secret: "your_client_secret"
```

### Advanced Configuration

```yaml
# Complete config.json
{
  "connection_type": "autonomous",
  "host": "adb.sa-saopaulo-1.oraclecloud.com",
  "port": 1522,
  "user": "ADMIN",
  "password": "your_password",
  "service_name": "dbname_low",
  "wallet_location": "/path/to/wallet.zip",
  "wallet_password": "wallet_password",
  "default_target_schema": "WMSSTAGE",
  "table_prefix": "", # Optional: prefix for all tables
  "table_suffix": "_STAGE", # Optional: suffix for all tables
  "schema_mapping": { "tap_schema": "target_schema" },
  "add_metadata_columns": true,
  "metadata_columns": { "LOADED_AT": "TIMESTAMP", "BATCH_ID": "VARCHAR2(50)" },
  "batch_size_rows": 100000,
  "flush_all_streams": false,
  "parallelism": 4,
  "data_flattening_max_level": 0,
  "primary_key_required": false,
  "validate_records": true,
  "load_method": "append", # append, upsert, insert, overwrite
  "bulk_load": false, # Use Direct Path for fast loading
  "oic_integration": "WMS_PROCESS_DATA", # OIC integration name for additional processing
  "oic_config": {
      "url": "https://your-instance.integration.ocp.oraclecloud.com",
      "auth_method": "basic", # basic or oauth2
      "username": "oic_username",
      "password": "oic_password",
      "client_id": "your_oauth_client_id",
      "client_secret": "your_oauth_client_secret",
    },
}
```

## Loading Configuration

### Loading Methods

The loader supports several loading methods:

#### Append (Default)

Adds new records to existing table:

```yaml
config:
  load_method: append
```

#### Upsert

Inserts new records or updates existing ones based on primary key:

```yaml
config:
  load_method: upsert
```

#### Overwrite

Replaces entire table with each load:

```yaml
config:
  load_method: overwrite
```

### Bulk Loading

For high-volume loads:

```yaml
config:
  bulk_load: true # Enable Direct Path Insert for fast loading
```

## OIC Integration

The advantage of this loader is the ability to integrate with Oracle Integration Cloud:

### Acionando uma Integração OIC para Processamento Adicional

```yaml
config:
  oic_integration: "WMS_DATA_PROCESSOR" # Nome da integração a ser chamada após carga no DB
```

Quando configurado, o loader notificará o OIC após a carga bem-sucedida, permitindo processamentos adicionais como:

- Transformações complexas dos dados
- Enriquecimento com outras fontes
- Validações adicionais
- Notificações ou alertas baseados nos dados
- Iniciar fluxos de negócio no OIC

## Mapeamento e Transformação

### Mapeamento de Schema

Para carregar dados de um schema de origem para outro destino:

```yaml
config:
  schema_mapping:
    "source_schema": "WMSSTAGE"
```

### Colunas de Metadados

Adicionar colunas de metadados em cada tabela:

```yaml
config:
  add_metadata_columns: true
  metadata_columns:
    "LOADED_AT": "TIMESTAMP"
    "BATCH_ID": "VARCHAR2(50)"
```

## Exemplo com Meltano

### Pipeline Básico

```bash
# Extrair dados do WMS e carregar no Oracle Autonomous Database via OIC
meltano elt tap-wms target-oic-adb --job-id=wms_to_adb
```

### Configuração com Agendamento

```yaml
# meltano.yml
schedules:
  - name: wms_daily_sync
    extractor: tap-wms
    loader: target-oic-adb
    interval: "@daily"
    start_date: 2023-01-01
```

## Arquitetura

Este loader implementa um padrão de integração híbrido:

1. Os dados são extraídos do sistema de origem (ex: WMS) via tap/extractor Meltano
2. O loader target-oic-adb armazena diretamente os dados no Oracle Autonomous Database
3. Opcionalmente, o OIC é notificado para realizar processamentos adicionais
4. O OIC pode executar transformações, consolidações ou iniciar processos de negócio com os dados

Esse padrão combina:

- A flexibilidade e facilidade do Meltano para extração
- A confiabilidade do acesso direto ao banco de dados
- A capacidade de orquestração e transformação do OIC

## Desenvolvimento

Este plugin foi desenvolvido usando o [Meltano SDK](https://sdk.meltano.com/) para garantir compatibilidade e seguir as melhores práticas de construção de loaders.

### Estrutura do Código

```
target_oic_adb/
├── __init__.py
├── connection.py     # Gerenciamento de conexão Oracle
├── sinks.py          # Implementação dos coletores de dados
├── target.py         # Classe principal do loader
```

## Resolução de Problemas

### Erros de Conexão com Autonomous Database

Se encontrar problemas com o wallet:

1. Verifique se o arquivo wallet.zip está acessível para o usuário que executa o Meltano
2. Certifique-se de que a senha do wallet está correta
3. Confirme que o service_name utilizado é o correto (recomendamos usar o perfil_low para integração)

### Erros de Autenticação no OIC

Para problemas de autenticação:

1. Verifique as credenciais do usuário OIC ou Client ID/Secret
2. Confirme se o usuário tem permissões para acessar/invocar a integração configurada
3. Para OAuth2, confirme se o client tem os escopos adequados no IDCS

### Problemas de Performance

Para cargas de grande volume:

```yaml
config:
  batch_size_rows: 250000
  bulk_load: true
  parallelism: 8
```
