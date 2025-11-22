# FlextModels · Configurações de Processamento

Essas estruturas encapsulam o contrato de configuração usado por orquestradores, handlers e middleware no FLEXT. Todas foram levantadas via AST em `flext_core/models.py` e auditadas com busca estática (testes ignorados) para confirmar o uso real.

Para cada modelo descrevemos por que ele existe, funcionamento interno, cenários de negócio recomendados, adoções atuais, benefícios tangíveis e decisões sugeridas (adotar, mover para experimento ou aposentar).

## Componentes

### `ProcessingRequest`

**Por que existe / qual problema resolve**

- Padroniza o envelope de execução de operações: ID único, payload (`data`), contexto, timeout e política de retentativa. Sem esse modelo cada serviço monta dicionários e não há garantia de correlação/timeout uniforme.

**Como funciona**

- `ArbitraryTypesModel` com `operation_id` gerado por `FlextUtilities`, `context` normalizado via `ensure_trace_context` (inclui `correlation_id` e timestamp), `timeout_seconds`/`retry_attempts` alimentados por `FlextConfig` e validados contra `FlextConstants`. Possui `validate_processing_constraints` que retorna `FlextResult` para bloquear timeouts superiores ao limite corporativo.

**Aplicações esperadas no negócio**

- Entrada única para `FlextService`/`FlextDispatcher`, transmissores gRPC/rest ou pipelines batch que precisam enviar dados + contexto + políticas.
- Operações internas como `flext-core/src/flext_core/service.py` e `flext-core/src/flext_core/dispatcher.py` poderiam receber esse DTO em vez de múltiplos argumentos.

**Adoções atuais**

- Ainda não há referências fora do módulo base; somente testes.

**Benefícios concretos**

- Garantia de que todo processamento tenha correlação e timeouts alinhados ao `FlextConfig`. Facilita logging/auditoria (todos carregam `operation_id`).

**Oportunidades / decisões**

- Priorizar piloto nos serviços de dispatcher/handlers. Caso não haja roadmap, mover para uma RFC para evitar manter recursos não utilizados.

### `RetryConfiguration`

**Por que existe / qual problema resolve**

- Substitui dicionários de retentativa espalhados por handlers, expondo limites corporativos (mínimo/máximo) e validação de códigos HTTP/Exceções.

**Como funciona**

- `ArbitraryTypesModel` com `max_attempts`, delays, `exponential_backoff`, listas de exceções/códigos HTTP e validadores (`validate_backoff_strategy`, `validate_delay_consistency`). Reusa limites de `FlextConstants` e `FlextConfig` garantindo que não extrapolamos políticas definidas.

**Aplicações esperadas no negócio**

- Configurar retentativas de comandos/eventos no dispatcher, orquestrações LDIF e adaptadores gRPC/REST.

**Adoções atuais**

- Nenhuma fora do módulo base.

**Benefícios concretos**

- Ajuda a documentar claramente quais erros/códigos são elegíveis para retry e impede valores inválidos (ex.: HTTP 999).

**Oportunidades / decisões**

- Integrar com `FlextService.execute_conditionally` ou `FlextDispatcher` para uniformizar retentativas. Sem plano de uso, considerar torná-lo experimental.

### `ValidationConfiguration`

**Por que existe / qual problema resolve**

- Concentra flags de validação (strict mode, limites de erros, validadores personalizados) para operações que precisam ajustar o rigor das verificações.

**Como funciona**

- `ArbitraryTypesModel` com campos booleanos, limites numéricos e lista de validadores extras. A lista passa por `validate_additional_validators`, que usa `FlextUtilities.Validation.validate_callable` e lança `FlextExceptions.TypeError` quando necessário.

**Aplicações esperadas no negócio**

- Pipelines LDIF/LDAP que alternam entre modo estrito e tolerante; integrações REST que precisam habilitar validação on-read.

**Adoções atuais**

- Nenhuma referência fora do módulo base.

**Benefícios concretos**

- Evita flags dispersas e facilita auditar quem habilitou/desabilitou validação.

**Oportunidades / decisões**

- Inserir como dependência em módulos que já utilizam `Validation.validate_*`. Caso permaneça sem adoção, registrar como item legado para não gerar dívida.

### `BatchProcessingConfig`

**Por que existe / qual problema resolve**

- DTO para operações em lote com tamanho, paralelismo, timeout por item e política de continuidade. Substitui `dicts` com `batch_size` e `max_workers` soltos.

**Como funciona**

- Herda `FlextModelsCollections.Config`. Campos puxam defaults de `FlextConfig` e aplicam limites de `FlextConstants`. O `model_validator` garante que `batch_size` não ultrapasse o máximo e ajusta `max_workers` para não exceder o tamanho do lote.

**Aplicações esperadas no negócio**

- Execuções LDIF/Oracle que processam registros em blocos, migradores de identidades e pipelines de ETL.

**Adoções atuais**

- Ainda não utilizado fora do módulo base.

**Benefícios concretos**

- Evita configurações inconsistentes (mais workers do que itens, batch size acima do permitido) e reforça padrões de timeout.

**Oportunidades / decisões**

- Integrar com `flext-ldif` e `flext-target-*` para consolidar as dezenas de parâmetros hoje passados por função. Sem adoção, considerar marcar como experimental.

### `HandlerExecutionConfig`

**Por que existe / qual problema resolve**

- Padrão para executar handlers com nome validado, payload, contexto, timeout, política de retry. Elimina múltiplos parâmetros em `flext_core/handlers.py`.

**Como funciona**

- Herda `FlextModelsCollections.Config`. Campos incluem `handler_name` (regex), `input_data`, `execution_context`, `timeout_seconds`, `retry_on_failure`, `max_retries` (defaults baseados no `FlextConfig`).

**Aplicações esperadas no negócio**

- Execução de handlers CQRS, pipelines de middleware e dispatchers internos.

**Adoções atuais**

- Nenhum uso fora do módulo base.

**Benefícios concretos**

- Simplifica chamadas (um único objeto) e garante que nomes/retentativas respeitem padrões.

**Oportunidades / decisões**

- Avaliar substituição das assinaturas atuais de `flext_core/src/flext_core/handlers.py`. Caso não seja prioridade, catalogar como “pendente de adoção” para evitar drift.

### `MiddlewareConfig`

**Por que existe / qual problema resolve**

- Especifica ativação, ordem e payload específico de middlewares sem depender de dicionários não tipados.

**Como funciona**

- `BaseModel` com `enabled`, `order`, `name` e `config` (dict). O `json_schema_extra` documenta o objetivo e facilita geração automática de schemas.

**Aplicações esperadas no negócio**

- Orquestração de middleware no dispatcher, pipelines HTTP/gRPC e frameworks internos.

**Adoções atuais**

- Não há uso fora do módulo base.

**Benefícios concretos**

- Permite definir cadeias de middleware em configurações, melhora observabilidade (sabemos quais estão habilitados e em qual ordem).

**Oportunidades / decisões**

- Conectar com `flext-core/src/flext_core/context.py` ou `flext_observability` para controlar interceptadores. Sem adoção prevista, avaliar se deve seguir como proposta.

### `RateLimiterState`

**Por que existe / qual problema resolve**

- Estrutura o estado de rate limiters (contagem, janela, bloqueio) em vez de espalhar variáveis sem contrato, permitindo monitoramento/controladores centralizados.

**Como funciona**

- `BaseModel` com campos `processor_name`, `count`, `window_start`, `limit`, `window_seconds`, `block_until`. Usa `json_schema_extra` para documentar e pode ser serializado facilmente para storage ou métricas.

**Aplicações esperadas no negócio**

- Implementações de throttling em handlers/middlewares, controle de abusos em APIs e monitoração de pipelines que batem em sistemas externos.

**Adoções atuais**

- Não há referências fora de `flext_core/models.py`.

**Benefícios concretos**

- Viabiliza reuso de rate limiters e facilita reset/persistência do estado.

**Oportunidades / decisões**

- Associar ao `MiddlewareConfig` para habilitar rate limiting controlado por configuração. Se continuar sem consumidores, avaliá-lo como componente experimental.
