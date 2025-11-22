# FlextModels · Serviços de Domínio

Requisições de execução, lote, métricas e recursos usadas em serviços de domínio.

> Fonte: AST de `flext_core/models.py` + varredura estática (testes ignorados).

## Componentes

### `DomainServiceExecutionRequest`

**Por que existe / qual problema resolve**

- Encapsula todos os dados necessários para invocar um serviço de domínio (nome, método, parâmetros, contexto, timeout e flags). Evita o padrão atual de passar múltiplos argumentos soltos para `FlextService`.

**Como funciona**

- `ArbitraryTypesModel` com campos `service_name`, `method_name`, `parameters`, `context` e `timeout_seconds`. Os validadores empregam `FlextUtilities.Generators.ensure_trace_context` e `FlextUtilities.Validation.validate_timeout`, garantindo correlação e limites seguros.

**Aplicações**

- `flext_core/service.py` já aceita esse DTO, permitindo que clientes enviem uma única estrutura com tudo o que o serviço precisa para executar.

**Uso atual**

- `flext-core/src/flext_core/service.py`.

**Benefícios / decisões**

- Simplifica contratações entre camadas e introduz validação centralizada. Recomenda-se migrar serviços que ainda usam dicionários (ex.: targets) para esse modelo.

### `DomainServiceBatchRequest`

**Por que existe**

- Padroniza execuções em lote (lista de operações, paralelismo, política de erro, batch size, timeout por operação). Substitui a multiplicidade de estruturas artesanais usadas em importadores e pipelines.

**Funcionamento**

- `ArbitraryTypesModel` com lista de operações (min 1/max definido em `FlextConstants`), flags `parallel_execution`, `stop_on_error`, `batch_size`, `timeout_per_operation` amarrados ao `FlextConfig`.

**Aplicações esperadas**

- Importadores LDIF/Oracle, sincronizações que executam múltiplas operações por lote.

**Uso atual**

- Ainda não há referências fora do módulo base.

**Decisões**

- Pilotar em pipelines que já implementam lotes manualmente; caso contrário, marcá-lo como experimental para evitar manutenção sem uso.

### `DomainServiceMetricsRequest`

**Motivação**

- Uniformiza consultas de métricas para serviços (tipos de métricas, janelas de tempo, agregação, filtros). Sem esse DTO, cada dashboard implementa filtros próprios.

**Funcionamento**

- `ArbitraryTypesModel` com `service_name`, `metric_types` (literaiss `performance/errors/throughput/...`), `time_range_seconds`, `aggregation`, `group_by`, `filters`.

**Aplicações**

- APIs/serviços que expõem estatísticas sobre execuções, permitindo que consumidores definam janelas e agregações específicas.

**Uso atual**

- Não referenciado fora do módulo base.

**Decisão**

- Integrar com os módulos de observabilidade ou remover se não houver adoção planejada.

### `DomainServiceResourceRequest`

**Motivação**

- DTO para solicitações de recursos (tipo, ID, limite, ação, filtros) a partir de um serviço de domínio. Ajuda a centralizar operações `GET/POST/DELETE` em padrões reutilizáveis.

**Funcionamento**

- `ArbitraryTypesModel` com defaults (`service_name="default_service"`, `resource_type` validado via regex, `resource_limit`, `action`, `data`, `filters`).

**Aplicações**

- Orquestradores que precisam requisitar recursos a subserviços (ex.: buscar configurações adicionais, pools de conexões).

**Uso atual**

- Sem referências fora do módulo base.

**Decisão**

- Documentar como padrão sugerido, garantindo que quem precise expor recursos o faça de forma uniforme. Caso continue sem consumidores, reavaliar sua permanência na API pública.

### `OperationExecutionRequest`

**Motivação**

- Abstrair a execução de uma operação (callable + argumentos + timeout + retry) para reutilizar em `FlextService.execute_operation`, gRPC e outros sistemas.

**Funcionamento**

- `ArbitraryTypesModel` com `operation_name`, `operation_callable`, `arguments`, `keyword_arguments`, `timeout_seconds` e `retry_config`. O validador `validate_operation_callable` usa `FlextUtilities.Validation.validate_callable` para garantir a assinatura.

**Aplicações**

- `flext_core/service.py` ao executar operações e `flext-grpc/api.py` quando expõe operações remotas (único uso externo encontrado).

**Decisões**

- Mantê-lo como DTO oficial para invocações de operações, estimulando outras camadas (CLI, adapters) a adotarem esse contrato em vez de múltiplos argumentos.
