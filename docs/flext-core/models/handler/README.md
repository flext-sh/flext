# FlextModels · Gerenciamento de Handlers

<!-- TOC START -->

- [Componentes](#componentes)
  - [`HandlerRegistration`](#handlerregistration)
  - [`RegistrationDetails`](#registrationdetails)
  - [`HandlerExecutionContext`](#handlerexecutioncontext)
  <!-- TOC END -->

Modelos para registrar handlers, detalhar capacidades e monitorar execução. Dados extraídos via AST em `flext_core/models.py` e confirmados com busca estática (testes ignorados).

Para cada componente descrevemos motivação, funcionamento, aplicações no negócio, uso atual, benefícios e decisões recomendadas.

## Componentes

### `HandlerRegistration`

**Por que existe / qual problema resolve**

- Padroniza o cadastro de handlers no dispatcher/registry. Sem esse DTO cada time criaria dicionários com campos diferentes e validações frágeis.

**Como funciona**

- `ArbitraryTypesModel` com `name`, `handler` (callable validado via `validate_handler`), `event_types`. O validator garante que o handler seja realmente chamável sem precisar importar utilitários adicionais.

**Aplicações esperadas**

- Registrar handlers no `FlextRegistry`, orquestrar pipelines com `handlers.py`, expor handlers via APIs de configuração.

**Adoções atuais**

- Ainda não referenciado fora do módulo base (o registry utiliza o nível inferior `RegistrationDetails`).

**Benefícios / decisões**

- Fornece contrato único para cadastro e habilita validação automática. Recomenda-se integrá-lo ao `flext_core/registry.py` para substituir dicts ad-hoc; caso não ocorra, considerar mover para módulo experimental.

### `RegistrationDetails`

**Por que existe / qual problema resolve**

- Rastreamento detalhado das inscrições (ID único, modo, timestamp, status). Ajuda a auditar quando/como cada handler foi registrado.

**Como funciona**

- `BaseModel` com campos validados (timestamp ISO via `validate_timestamp_format`, enums de status/handler mode). Roda dentro do `FlextRegistry` para cada registro efetuado.

**Aplicações esperadas**

- Monitoramento em `flext_core/src/flext_core/registry.py`, dashboards de operabilidade, auditoria de handlers instalados.

**Adoções atuais**

- Usado diretamente no `FlextRegistry`.

**Benefícios / decisões**

- Habilita logs/telemetria consistentes sobre cadastro de handlers. Manter como base oficial e expandir coleta de métricas/alertas.

### `HandlerExecutionContext`

**Por que existe / qual problema resolve**

- Controla métricas e estado de execução de handlers (tempo de execução, métricas customizadas) de forma padronizada. Sem isso cada handler teria seu próprio contador.

**Como funciona**

- `BaseModel` com campos `handler_name`/`handler_mode` e atributos privados (`_start_time`, `_metrics_state`). Métodos como `start_execution`, `execution_time_ms`, `set_metrics_state` permitem medir e compartilhar dados via `FlextContext`.

**Aplicações esperadas**

- `flext_core/src/flext_core/handlers.py` utiliza para medir tempo de cada handler, bem como exportar métricas ao final da execução.

**Adoções atuais**

- Referenciado em `flext_core/src/flext_core/handlers.py` (único arquivo identificado).

**Benefícios / decisões**

- Facilita observabilidade (latências, métricas) e padroniza como handlers reportam estado. Recomenda-se expandir uso a outros projetos que implementam handlers custom (targets/taps) para compartilhar métricas no mesmo formato.
