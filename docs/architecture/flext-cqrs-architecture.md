# Flext CQRS Architecture – Migração Completa


<!-- TOC START -->
- [Documentação de destino](#documentao-de-destino)
- [TODOs migrados para código](#todos-migrados-para-cdigo)
- [Conteúdo restante (pendente de implementação)](#contedo-restante-pendente-de-implementao)
- [~~Snapshot~~ ✅ MIGRADO](#snapshot-migrado)
- [~~Current Capabilities (V1 Baseline)~~ ✅ MIGRADO](#current-capabilities-v1-baseline-migrado)
  - [~~Handler lifecycle~~](#handler-lifecycle)
  - [~~Dispatcher responsibilities~~](#dispatcher-responsibilities)
  - [~~Infrastructure gaps~~](#infrastructure-gaps)
- [~~Modernisation Roadmap~~ ✅ MIGRADO](#modernisation-roadmap-migrado)
- [~~Handler Patterns~~ ✅ MIGRADO](#handler-patterns-migrado)
- [~~Dispatcher Evolution~~ ✅ MIGRADO](#dispatcher-evolution-migrado)
- [~~Integration With FlextService~~ ✅ MIGRADO](#integration-with-flextservice-migrado)
- [~~Testing Guidance~~ ✅ MIGRADO](#testing-guidance-migrado)
- [~~TODO Backlog~~ ✅ MIGRADO](#todo-backlog-migrado)
- [~~References~~ ✅ MIGRADO](#references-migrado)
- [~~🗺️ Roadmap de Evolução CQRS~~ ✅ MIGRADO](#roadmap-de-evoluo-cqrs-migrado)
- [~~📊 Sumário Executivo~~ ✅ MIGRADO](#sumrio-executivo-migrado)
- [~~🔍 Análise do Ecossistema CQRS~~ ✅ MIGRADO](#anlise-do-ecossistema-cqrs-migrado)
  - [~~Arquitetura de Tiers~~ ✅](#arquitetura-de-tiers)
  - [~~FlextHandlers (Tier 3.1)~~ ✅](#flexthandlers-tier-31)
  - [~~FlextDispatcher (Tier 3.2)~~ ✅](#flextdispatcher-tier-32)
  - [~~Integração com FlextContainer (Target)~~ ✅](#integrao-com-flextcontainer-target)
- [~~📈 Análise do Estado Atual~~ ✅ MIGRADO](#anlise-do-estado-atual-migrado)
  - [~~O Que Funciona ✅~~ ✅](#o-que-funciona)
  - [~~O Que NÃO Funciona ❌~~ ✅](#o-que-no-funciona)
  - [~~Anti-Patterns Identificados~~ ✅](#anti-patterns-identificados)
- [~~🏗️ Arquitetura Proposta~~ ✅ MIGRADO](#arquitetura-proposta-migrado)
  - [~~Visão Geral V2~~ ✅](#viso-geral-v2)
  - [~~FlextMixins.CQRS (Nova Classe Nested)~~ 📋 SPEC PENDENTE](#flextmixinscqrs-nova-classe-nested-spec-pendente)
  - [~~Protocol-Based Manager Interfaces~~ 📋 SPEC PENDENTE](#protocol-based-manager-interfaces-spec-pendente)
  - [~~FlextDispatcher V2 Refactored~~ 📋 SPEC PENDENTE](#flextdispatcher-v2-refactored-spec-pendente)
  - [~~FlextHandlers V2 Refactored~~ 📋 SPEC PENDENTE](#flexthandlers-v2-refactored-spec-pendente)
- [~~🔗 Padrões de Integração~~ ✅ MIGRADO](#padres-de-integrao-migrado)
  - [~~Fronteiras Arquiteturais~~ ✅](#fronteiras-arquiteturais)
  - [~~Quando Usar Cada Camada~~ ✅](#quando-usar-cada-camada)
  - [~~Pattern 1: Service Chamado de Handler~~ ✅](#pattern-1-service-chamado-de-handler)
  - [~~Pattern 2: Dispatcher Roteando para Services~~ ✅](#pattern-2-dispatcher-roteando-para-services)
  - [~~Pattern 3: Handler com Full Observability~~ 📋 SPEC PENDENTE](#pattern-3-handler-com-full-observability-spec-pendente)
- [~~⚙️ Infraestrutura Avançada~~ ✅ MIGRADO](#infraestrutura-avanada-migrado)
  - [~~FlextHandlers Pipeline~~ ✅](#flexthandlers-pipeline)
  - [~~FlextDispatcher Reliability Patterns~~ ✅](#flextdispatcher-reliability-patterns)
  - [~~Manager Extraction (V2)~~ 📋 SPEC PENDENTE](#manager-extraction-v2-spec-pendente)
- [~~📖 Guia de Implementação~~ ✅ MIGRADO](#guia-de-implementao-migrado)
  - [~~Setup Básico de Handler (V2)~~ ✅](#setup-bsico-de-handler-v2)
  - [~~Setup de Dispatcher com DI (V2)~~ 📋 SPEC PENDENTE](#setup-de-dispatcher-com-di-v2-spec-pendente)
  - [~~Criando Custom Reliability Policy~~ 📋 SPEC PENDENTE](#criando-custom-reliability-policy-spec-pendente)
- [~~🎯 Padrões de Uso~~ ✅ MIGRADO](#padres-de-uso-migrado)
  - [~~Simple Command Handling~~ ✅](#simple-command-handling)
  - [~~Query with Caching~~ ✅](#query-with-caching)
  - [~~Event Processing with Audit~~ ✅](#event-processing-with-audit)
  - [~~Multi-Operation Handler~~ ✅](#multi-operation-handler)
- [~~🔄 Guia de Migração~~ ✅ MIGRADO](#guia-de-migrao-migrado)
  - [~~De Métricas Manuais para FlextMixins.CQRS~~ ✅](#de-mtricas-manuais-para-flextmixinscqrs)
  - [~~De Managers Hardcoded para DI~~ ✅](#de-managers-hardcoded-para-di)
  - [~~Deprecation Timeline~~ ✅ MIGRADO](#deprecation-timeline-migrado)
  - [~~Warnings Durante Migração~~ ✅](#warnings-durante-migrao)
- [~~📝 Exemplos~~ 📋 EXEMPLOS PRESERVADOS](#exemplos-exemplos-preservados)
  - [~~Exemplo 1: CQRS Application Completo~~ 📋](#exemplo-1-cqrs-application-completo)
  - [Exemplo 2: Custom Circuit Breaker](#exemplo-2-custom-circuit-breaker)
  - [Exemplo 3: Handler com Full Observability](#exemplo-3-handler-com-full-observability)
- [~~📊 Estudos de Caso~~ 📋 EXEMPLOS PRESERVADOS](#estudos-de-caso-exemplos-preservados)
  - [~~Estudo de Caso: flext-ldif~~ 📋](#estudo-de-caso-flext-ldif)
  - [Estudo de Caso: flext-api](#estudo-de-caso-flext-api)
  - [Estudo de Caso: client-a-oud-mig](#estudo-de-caso-client-a-oud-mig)
- [~~✅ Validação e Testes~~ 📋 EXEMPLOS DE TESTES PRESERVADOS](#validao-e-testes-exemplos-de-testes-preservados)
  - [~~Estrutura de Testes CQRS~~](#estrutura-de-testes-cqrs)
  - [Testes para x.CQRS](#testes-para-xcqrs)
  - [Testes para FlextDispatcher DI](#testes-para-flextdispatcher-di)
  - [Performance Benchmarks](#performance-benchmarks)
- [~~📚 Referências~~ ✅ MIGRADO](#referncias-migrado)
- [~~📋 Plano de Execução - CQRS Modernization~~ 📋 SPEC PENDENTE](#plano-de-execuo-cqrs-modernization-spec-pendente)
  - [~~Classes Cross-Cutting e Integração CQRS (25 Nov 2025)~~](#classes-cross-cutting-e-integrao-cqrs-25-nov-2025)
  - [Validação vs Código (25 Nov 2025)](#validao-vs-cdigo-25-nov-2025)
  - [Plano de Execução Detalhado](#plano-de-execuo-detalhado)
  - [Métricas de Sucesso](#mtricas-de-sucesso)
  - [Timeline Estimada](#timeline-estimada)
- [~~📅 Histórico de Versões~~ 📋 METADADO](#histrico-de-verses-metadado)
<!-- TOC END -->

**Status:** ✅ MIGRADO para `flext-core/docs/architecture/cqrs.md`

Este documento foi migrado para a documentação oficial do flext-core.

## Documentação de destino

- **CQRS Architecture:** [`flext-core/docs/architecture/cqrs.md`](https://github.com/organization/flext/tree/main/flext-core/docs/architecture/cqrs.md)
- **Service Patterns:** [`flext-core/docs/guides/service-patterns.md`](https://github.com/organization/flext/tree/main/flext-core/docs/guides/service-patterns.md)

## TODOs migrados para código

Os seguintes TODOs foram adicionados diretamente nos arquivos de código:

1. **`handlers.py`** - Module docstring com referência a Phase 1 (FlextMixins.CQRS)
2. **`handlers.py`** - Comentário em `_context_stack` e `_metrics` sobre migração
3. **`dispatcher.py`** - Module docstring com referência a Phase 2 (DI via container)
4. **`result.py`** - Já contém TODO sobre `and_then()` helper

## Conteúdo restante (pendente de implementação)

As seguintes seções descrevem funcionalidades **não implementadas** que podem
servir como referência futura para implementação:

---

## ~~Snapshot~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#overview`

~~- `flext_core.handlers.h` defines the generic handler base with lifecycle hooks (`before_handle`, `handle`, `after_handle`, `on_error`).~~
~~- `flext_core.dispatcher.FlextDispatcher` orchestrates handler execution, retry logic, and telemetry wiring.~~
~~- Reliability helpers (circuit breaker, retry, timeout, rate limiting) live under `flext_core._dispatcher`; they are being refactored to rely on dependency injection instead of hard-coded globals.~~
~~- Observability helpers (logger, metrics, tracking) are exposed through `mixins.x.CQRS`, although V1 handlers still carry manual instrumentation.~~

---

## ~~Current Capabilities (V1 Baseline)~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#current-state-v1`

### ~~Handler lifecycle~~

~~1. Handlers derive from `h[TMessage, TResult]` and implement `handle(self, message) -> FlextResult[TResult]`.~~
~~2. The `_run_pipeline` helper wraps execution with validation, hooks, and error handling.~~
~~3. Manual bookkeeping for metrics/context (`self._metrics`, `self._context_stack`) remains common across projects.~~

### ~~Dispatcher responsibilities~~

~~- Routes commands, queries, and events based on explicit registration.~~
~~- Applies retry/timeout logic via `_dispatcher.reliability` modules.~~
~~- Propagates correlation IDs through `FlextContext` scopes.~~
~~- Emits structured logs via `FlextLogger`, though many call sites still need metadata cleanup.~~

### ~~Infrastructure gaps~~

~~- Manager instances (circuit breaker, rate limiter, timeout) are still constructed internally.~~
~~- Handler instrumentation is duplicated and difficult to test.~~
~~- Dependency injection into handlers is optional rather than the default path.~~

---

## ~~Modernisation Roadmap~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#modernization-roadmap`

~~| Phase | Focus | Target date | Notes |~~
~~| --- | --- | --- | --- |~~
~~| **Phase 1** | Document current stack and migrate docs to English | ✅ Nov 2025 | Complete with this merge |~~
~~| **Phase 2** | Make dispatcher managers injectable through `FlextContainer` | 🟡 In progress | Constructors accept `container=...`; update remaining call sites |~~
~~| **Phase 3** | Promote `mixins.x.CQRS` helpers (metrics, tracking, logging) to default usage | 🔜 Jan 2026 | Remove manual stacks from handlers |~~
~~| **Phase 4** | Align reliability policies with upcoming `FlextResult.and_then` helper | 🔜 Feb 2026 | Depends on service-level TODO |~~
~~| **Phase 5** | Deliver zero-ceremony handler scaffolding/templates | 🔜 Mar 2026 | Finalise cross-repo generators |~~

---

## ~~Handler Patterns~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#handler-patterns`

---

## ~~Dispatcher Evolution~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#flextdispatcher`

---

## ~~Integration With FlextService~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#integration-with-flextservice`

---

## ~~Testing Guidance~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#testing-guidance`

---

## ~~TODO Backlog~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#todo-backlog`

~~- Migrate handlers to use `self.logger`, `self.track`, and `self.cqrs_metrics` (Phase 3).~~
~~- Enforce container-based dispatcher construction once all call sites are migrated (Phase 2).~~
~~- Update `_dispatcher.reliability` to consume the forthcoming `FlextResult.and_then` helper for naming parity (Phase 4).~~
~~- Draft CLI scaffolding that generates zero-ceremony handlers (Phase 5).~~

---

## ~~References~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#references`

~~- `flext_core/handlers.py`~~
~~- `flext_core/dispatcher.py`~~
~~- `flext_core/_dispatcher/reliability.py`~~
~~- `flext_core/_dispatcher/timeout.py`~~
~~- `flext_core/mixins.py`~~
~~- `docs/FLEXT_SERVICE_ARCHITECTURE.md`~~

---

## ~~🗺️ Roadmap de Evolução CQRS~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#modernization-roadmap`

~~### Comparativo V1 → V2~~ ✅

~~| Aspecto | V1 (Atual) | V2 (Target) |~~
~~| ------------------------- | ----------------------------------------- | ---------------------------------- |~~
~~| **Métricas** | `self._metrics` manual (50+ linhas) | `self.cqrs_metrics` via x |~~
~~| **Contexto** | `self._context_stack` manual (30+ linhas) | `self.context` via x |~~
~~| **Logging** | Inconsistente, pouco usado | `self.logger` automático |~~
~~| **Tracking** | Manual ou inexistente | `self.track()` automático |~~
~~| **Managers (Dispatcher)** | Hardcoded (700+ linhas) | Injetados via FlextContainer |~~
~~| **Circuit Breaker** | `self._circuit_breaker` interno | `container.get("circuit_breaker")` |~~
~~| **Rate Limiter** | `self._rate_limiter` interno | `container.get("rate_limiter")` |~~

~~### Linha do Tempo~~ ✅

~~```~~
~~V1 (Atual) V2 Integration V2 Complete~~
~~ │ │ │~~
~~ │ Manual metrics │ x.CQRS │ Full observability~~
~~ │ Manual context │ DI │ Auto-discovery~~
~~ │ Hardcoded managers │ Protocol-based │ Zero ceremony~~
~~ │ │ │~~
~~────┼──────────────────────┼──────────────────────┼─────────────────→~~
~~ │ │ │~~
~~ Nov 2025 Jan 2026 (Phase 1-2) Mar 2026 (Phase 3-5)~~
~~```~~

---

## ~~📊 Sumário Executivo~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#modernization-roadmap`
> Seção "Problems Addressed" e "Solution Strategy"

~~### O Problema~~ ✅

~~**h (Tier 3.1):**~~

~~- ❌ **50+ linhas** de métricas manuais (`self._metrics` dict)~~
~~- ❌ **30+ linhas** de contexto manual (`self._context_stack` list)~~
~~- ❌ **Logging não utilizado** (self.logger nunca chamado em \_run_pipeline)~~
~~- ❌ **Tracking não utilizado** (self.track() nunca chamado)~~
~~- ❌ **Validação duplicada** entre handlers~~

~~**FlextDispatcher (Tier 3.2):**~~

~~- ❌ **700+ linhas** de managers hardcoded no `__init__`~~
~~- ❌ **Sem DI** - impossível injetar managers customizados~~
~~- ❌ **100+ linhas** de cache manual~~
~~- ⚠️ **Logging moderado** (18 chamadas) mas inconsistente~~
~~- ⚠️ **Tracking mínimo** (2 chamadas) insuficiente~~

~~**Impacto:**~~

~~- 🔴 Duplicação de código em 32+ projetos dependentes~~
~~- 🔴 Impossibilidade de customizar comportamento de reliability~~
~~- 🔴 Métricas inconsistentes entre projetos~~
~~- 🔴 Difícil debugging sem logging estruturado~~

~~### A Solução~~ ✅

~~**Estratégia de Modernização:**~~

~~1. **x.CQRS** (Fase 1):~~
~~ - Extrair métricas para `self.cqrs_metrics`~~
~~ - Extrair contexto para `self.context`~~
~~ - Integrar logging/tracking no pipeline~~
~~ - Deprecar métodos manuais com grace period~~

~~2. **FlextDI** (Fase 2):~~
~~ - Definir protocols para managers~~
~~ - Extrair managers para módulo `_managers/`~~
~~ - Refatorar `FlextDispatcher.__init__()` para aceitar container~~
~~ - Registrar managers default no container~~

~~**Benefícios:**~~

~~- ✅ **Zero ceremony** - infraestrutura automática~~
~~- ✅ **Customização** - managers injetáveis via DI~~
~~- ✅ **Consistência** - métricas/logging unificados~~
~~- ✅ **Testabilidade** - mock de managers via container~~
~~- ✅ **Observabilidade** - tracking automático~~

---

## ~~🔍 Análise do Ecossistema CQRS~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#overview` (diagrama de Tiers)
> Veja também: `flext-core/docs/architecture/overview.md` para visão geral da arquitetura

### ~~Arquitetura de Tiers~~ ✅

~~```~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ Application Layer │~~
~~├─────────────────────────────────────────────────────────────────┤~~
~~│ Tier 3.2: FlextDispatcher │~~
~~│ ├── Orchestration and routing │~~
~~│ ├── Reliability patterns (circuit breaker, retry, timeout) │~~
~~│ └── Manager coordination │~~
~~├─────────────────────────────────────────────────────────────────┤~~
~~│ Tier 3.1: h │~~
~~│ ├── Command/Query/Event handlers │~~
~~│ ├── Validation pipeline │~~
~~│ └── Message processing │~~
~~├─────────────────────────────────────────────────────────────────┤~~
~~│ Tier 2.5: FlextService │~~
~~│ ├── Domain services with business logic │~~
~~│ ├── Execute via .result property │~~
~~│ └── Self-contained operations │~~
~~├─────────────────────────────────────────────────────────────────┤~~
~~│ Tier 2: Domain Foundation │~~
~~│ ├── FlextModels - Domain entities │~~
~~│ ├── u - Validation, conversion │~~
~~│ └── x - Reusable behaviors │~~
~~├─────────────────────────────────────────────────────────────────┤~~
~~│ Tier 1.5: FlextLogger │~~
~~│ └── Structured logging with context │~~
~~├─────────────────────────────────────────────────────────────────┤~~
~~│ Tier 1: Core Abstractions │~~
~~│ ├── FlextResult - Railway pattern │~~
~~│ └── FlextExceptions - Error handling │~~
~~├─────────────────────────────────────────────────────────────────┤~~
~~│ Tier 0.5: FlextRuntime │~~
~~│ └── Runtime utilities │~~
~~├─────────────────────────────────────────────────────────────────┤~~
~~│ Tier 0.1: FlextSettings │~~
~~│ └── Configuration management │~~
~~├─────────────────────────────────────────────────────────────────┤~~
~~│ Tier 0: Pure Foundation │~~
~~│ ├── FlextConstants - Error codes, defaults │~~
~~│ ├── t - Type aliases │~~
~~│ └── p - Interfaces │~~
~~└─────────────────────────────────────────────────────────────────┘~~
~~```~~

### ~~FlextHandlers (Tier 3.1)~~ ✅

> Migrado para: `flext-core/docs/architecture/cqrs.md#flexthandlers`

~~**Responsabilidades:**~~

~~- Processar Commands, Queries e Events~~
~~- Validar mensagens via pipeline~~
~~- Aplicar pre/post processors~~
~~- Gerenciar contexto de execução~~

~~**Estrutura Atual:**~~

~~```Python~~
~~class h(x, Generic[TCommand_contra, TResult_co]):~~
~~ """Base class for CQRS message handlers."""~~

~~ # ⚠️ Infraestrutura manual (será deprecated)~~
~~ \_metrics: dict[str, int | float]~~
~~\_context_stack: list[dict[str, object]]~~

~~ # ✅ Pipeline methods~~
~~ def handle(self, message: TCommand_contra) -> FlextResult[TResult_co]: ...~~
~~ def \_run_pipeline(self, message: TCommand_contra) -> FlextResult[TResult_co]: ...~~

~~ # ⚠️ Métodos manuais (serão deprecated em V2)~~
~~ def record_metric(self, key: str, value: int | float) -> None: ...~~
~~ def get_metrics(self) -> dict[str, int | float]: ...~~
~~ def push_context(self, ctx: dict[str, object]) -> None: ...~~
~~ def pop_context(self) -> dict[str, object] | None: ...~~
~~```~~

~~**Dependências:**~~

~~- `x` → logging, tracking, config, container (NÃO USADOS!)~~
~~- `FlextConstants` → status codes, messages~~
~~- `FlextExceptions` → error handling~~
~~- `FlextModels` → message types~~

### ~~FlextDispatcher (Tier 3.2)~~ ✅

> Migrado para: `flext-core/docs/architecture/cqrs.md#flextdispatcher`

~~**Responsabilidades:**~~

~~- Rotear mensagens para handlers~~
~~- Aplicar reliability patterns (circuit breaker, retry, timeout, rate limiter)~~
~~- Coordenar managers~~
~~- Gerenciar cache de handlers~~

~~**Estrutura Atual:**~~

~~```Python~~
~~class FlextDispatcher:~~
~~ """CQRS dispatcher with reliability patterns."""~~

~~ # ⚠️ Managers hardcoded (serão extraídos para DI)~~
~~ \_circuit_breaker_manager: CircuitBreakerManager # ~200 linhas~~
~~\_rate_limiter_manager: RateLimiterManager # ~150 linhas~~
~~ \_timeout_enforcer: TimeoutEnforcer # ~100 linhas~~
~~ \_retry_policy_manager: RetryPolicyManager # ~150 linhas~~
~~\_cache: dict[str, object] # ~100 linhas~~

~~ # ✅ Core methods~~
~~ def dispatch(self, message: object) -> FlextResult[object]: ...~~
~~ def register_command(self, cmd_type: type, handler: h) -> None: ...~~
~~ def register_query(self, query_type: type, handler: h) -> None: ...~~
~~ def register_event(self, event_type: type, handler: h) -> None: ...~~
~~```~~

~~**Dependências:**~~

~~- `FlextConstants` → configuration values~~
~~- `FlextContext` → execution context~~
~~- `h` → registered handlers~~
~~- `x` → logging (pouco usado)~~
~~- `FlextModels` → message models~~
~~- `FlextResult` → return type~~
~~- `u` → helper functions~~

### ~~Integração com FlextContainer (Target)~~ ✅

> Migrado para: `flext-core/docs/architecture/cqrs.md#modernization-roadmap` (Phase 2)

~~**Atual:** FlextContainer NÃO é usado pelo CQRS tier.~~

~~**Target:** Managers registrados e injetados via FlextContainer.~~

~~```Python~~
~~# Target: Registro de managers default~~
~~container = FlextContainer.get_global()~~
~~container.register("circuit_breaker", CircuitBreakerManager())~~
~~container.register("rate_limiter", RateLimiterManager())~~
~~container.register("timeout_enforcer", TimeoutEnforcer())~~
~~container.register("retry_policy", RetryPolicyManager())~~

~~# Target: Dispatcher aceita container~~
~~dispatcher = FlextDispatcher(container=container)~~
~~```~~

---

## ~~📈 Análise do Estado Atual~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#modernization-roadmap` (Problems Addressed)

### ~~O Que Funciona ✅~~ ✅

~~**FlextHandlers:**~~

~~- ✅ Pipeline de validação robusto~~
~~- ✅ Suporte a pre/post processors~~
~~- ✅ Type safety com generics~~
~~- ✅ Herança de x (infraestrutura disponível)~~

~~**FlextDispatcher:**~~

~~- ✅ Circuit breaker funcional~~
~~- ✅ Rate limiting funcional~~
~~- ✅ Retry com backoff exponencial~~
~~- ✅ Timeout enforcement~~
~~- ✅ Registro de handlers por tipo~~

### ~~O Que NÃO Funciona ❌~~ ✅

~~**FlextHandlers:**~~

~~| Problema | Impacto | Linhas | Solução |~~
~~| ----------------- | -------------------------- | ------ | -------------------- |~~
~~| Métricas manuais | Duplicação em 32+ projetos | 50+ | x.CQRS |~~
~~| Contexto manual | Inconsistência | 30+ | self.context |~~
~~| Logger não usado | Sem observabilidade | 0 | Integrar no pipeline |~~
~~| Tracker não usado | Sem performance data | 0 | Integrar no pipeline |~~

~~**FlextDispatcher:**~~

~~| Problema | Impacto | Linhas | Solução |~~
~~| --------------------- | --------------------- | -------- | ------------------ |~~
~~| Managers hardcoded | Impossível customizar | 700+ | FlextDI |~~
~~| Cache manual | Duplicação | 100+ | u.Caching |~~
~~| Logging inconsistente | Debugging difícil | 18 calls | FlextLogger padrão |~~
~~| Tracking mínimo | Sem métricas | 2 calls | x.track() |~~

### ~~Anti-Patterns Identificados~~ ✅

> Migrado para: `flext-core/docs/architecture/cqrs.md#modernization-roadmap` (Problems Addressed)

~~**1. Hardcoded Dependencies (FlextDispatcher):**~~

~~```python~~
~~# ❌ Anti-pattern: Managers criados internamente~~
~~class FlextDispatcher:~~
~~ def **init**(self):~~
~~ self.\_circuit_breaker = CircuitBreakerManager(~~
~~ default_failure_threshold=5,~~
~~ default_recovery_timeout=30.0,~~
~~ # ... 200+ linhas de configuração~~
~~ )~~
~~ self.\_rate_limiter = RateLimiterManager(~~
~~ default_max_requests=100,~~
~~ default_time_window=60.0,~~
~~ # ... 150+ linhas de configuração~~
~~ )~~
~~ # ... mais managers~~
~~```~~

~~**2. Manual State Management (FlextHandlers):**~~

~~```Python~~
~~# ❌ Anti-pattern: Estado gerenciado manualmente~~
~~class FlextHandlers:~~
~~ def **init**(self):~~
~~ self.\_metrics: dict[str, int | float] = {} # Manual!~~
~~ self.\_context_stack: list[dict] = [] # Manual!~~

    def record_metric(self, key: str, value: int | float) -> None:
        self._metrics[key] = self._metrics.get(key, 0) + value

~~ def push_context(self, ctx: dict) -> None:~~
~~ self.\_context_stack.append(ctx)~~
~~```~~

~~**3. Unused Infrastructure (FlextHandlers):**~~

~~```Python~~
~~# ❌ Anti-pattern: Herda x mas não usa~~
~~class FlextHandlers(FlextMixins, Generic[TCommand, TResult]):~~
~~ # Disponível mas NUNCA usado:~~
~~ # - self.logger → 0 chamadas em \_run_pipeline~~
~~ # - self.track() → 0 chamadas em \_run_pipeline~~
~~ # - self.config → 0 chamadas em \_run_pipeline~~
~~ # - self.container → 0 chamadas em \_run_pipeline~~

~~ def \_run_pipeline(self, message: TCommand) -> FlextResult[TResult]:~~
~~ # Manual em vez de usar infraestrutura!~~
~~ self.\_metrics["processed"] += 1 # Em vez de self.track()~~
~~```~~

---

## ~~🏗️ Arquitetura Proposta~~ ✅ MIGRADO

> Migrado parcialmente para: `flext-core/docs/architecture/cqrs.md#modernization-roadmap`
> **NOTA:** Esta seção contém especificações detalhadas de implementação futura.
> Manter como referência até implementação das Fases 1-5.

### ~~Visão Geral V2~~ ✅

> Diagrama de arquitetura V2 referenciado em cqrs.md

~~```~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ FlextDispatcher V2 │~~
~~│ ┌─────────────────────────────────────────────────────────┐ │~~
~~│ │ FlextContainer │ │~~
~~│ │ ┌─────────────┐ ┌──────────────┐ ┌────────────────┐ │ │~~
~~│ │ │ Circuit │ │ Rate │ │ Timeout │ │ │~~
~~│ │ │ Breaker │ │ Limiter │ │ Enforcer │ │ │~~
~~│ │ └─────────────┘ └──────────────┘ └────────────────┘ │ │~~
~~│ │ ┌─────────────┐ ┌──────────────┐ ┌────────────────┐ │ │~~
~~│ │ │ Retry │ │ Cache │ │ Custom │ │ │~~
~~│ │ │ Policy │ │ Manager │ │ Managers... │ │ │~~
~~│ │ └─────────────┘ └──────────────┘ └────────────────┘ │ │~~
~~│ └─────────────────────────────────────────────────────────┘ │~~
~~│ │ │~~
~~│ ▼ │~~
~~│ ┌─────────────────────────────────────────────────────────┐ │~~
~~│ │ Handler Registry │ │~~
~~│ │ ┌─────────────┐ ┌──────────────┐ ┌────────────────┐ │ │~~
~~│ │ │ Command │ │ Query │ │ Event │ │ │~~
~~│ │ │ Handlers │ │ Handlers │ │ Handlers │ │ │~~
~~│ │ └─────────────┘ └──────────────┘ └────────────────┘ │ │~~
~~│ └─────────────────────────────────────────────────────────┘ │~~
~~└─────────────────────────────────────────────────────────────────┘~~
~~ │~~
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ FlextHandlers V2 │~~
~~│ ┌─────────────────────────────────────────────────────────┐ │~~
~~│ │ FlextMixins │ │~~
~~│ │ ┌─────────────┐ ┌──────────────┐ ┌────────────────┐ │ │~~
~~│ │ │ self.config │ │ self.logger │ │ self.container │ │ │~~
~~│ │ └─────────────┘ └──────────────┘ └────────────────┘ │ │~~
~~│ │ ┌─────────────┐ ┌──────────────┐ ┌────────────────┐ │ │~~
~~│ │ │ self.context│ │ self.track() │ │ FlextMixins │ │ │~~
~~│ │ │ │ │ │ │ .CQRS │ │ │~~
~~│ │ └─────────────┘ └──────────────┘ └────────────────┘ │ │~~
~~│ └─────────────────────────────────────────────────────────┘ │~~
~~└─────────────────────────────────────────────────────────────────┘~~
~~```~~

### ~~FlextMixins.CQRS (Nova Classe Nested)~~ 📋 SPEC PENDENTE

> **STATUS:** Especificação de implementação futura (Phase 1)
> **TODO:** Implementar conforme roadmap em `cqrs.md#modernization-roadmap`

~~**Localização:** `flext_core/mixins.py`~~

~~**Propósito:** Fornecer funcionalidades CQRS-específicas que complementam as capacidades base de FlextMixins.~~

~~```Python~~
~~class FlextMixins(BaseModel, ABC):~~
~~ """Existing mixin class with infrastructure properties."""~~

~~ class CQRS:~~
~~ """CQRS-specific utilities extracted from FlextHandlers."""~~

~~ class MetricsTracker:~~
~~ """Thread-safe metrics tracking for handlers."""~~

~~ def **init**(self) -> None:~~
~~ self.\_metrics: dict[str, int | float] = {}~~
~~ self.\_lock = threading.Lock()~~

~~ def record(self, key: str, value: int | float) -> None:~~
~~ """Record a metric value (thread-safe)."""~~
~~ with self.\_lock:~~
~~ current = self.\_metrics.get(key, 0)~~
~~ self.\_metrics[key] = current + value~~

~~ def get(self, key: str) -> int | float:~~
~~ """Get metric value."""~~
~~ return self.\_metrics.get(key, 0)~~

~~ def all(self) -> dict[str, int | float]:~~
~~ """Get all metrics."""~~
~~ return dict(self.\_metrics)~~

~~ def reset(self) -> None:~~
~~ """Reset all metrics."""~~
~~ with self.\_lock:~~
~~ self.\_metrics.clear()~~

~~ class ContextStack:~~
~~ """Thread-safe context stack for handlers."""~~

~~ def **init**(self) -> None:~~
~~ self.\_stack: list[dict[str, object]] = []~~

~~ def push(self, ctx: dict[str, object]) -> None:~~
~~ """Push context onto stack."""~~
~~ self.\_stack.append(ctx)~~

~~ def pop(self) -> dict[str, object] | None:~~
~~ """Pop context from stack."""~~
~~ return self.\_stack.pop() if self.\_stack else None~~

~~ def current(self) -> dict[str, object]:~~
~~ """Get current context (merged stack)."""~~
~~ result: dict[str, object] = {}~~
~~ for ctx in self.\_stack:~~
~~ result.update(ctx)~~
~~ return result~~
~~```~~

### ~~Protocol-Based Manager Interfaces~~ 📋 SPEC PENDENTE

> **STATUS:** Especificação de implementação futura (Phase 2)
> **TODO:** Implementar conforme roadmap em `cqrs.md#modernization-roadmap`

~~**Localização:** `flext_core/protocols.py`~~

~~**Propósito:** Definir interfaces para managers que podem ser injetados via DI.~~

~~```Python~~
~~class FlextProtocols:~~
~~ """Protocol definitions for flext-core."""~~

~~ class CircuitBreakerProtocol(Protocol):~~
~~ """Protocol for circuit breaker managers."""~~

~~ def is_open(self, key: str) -> bool:~~
~~ """Check if circuit is open (failing)."""~~
~~ ...~~

~~ def record_success(self, key: str) -> None:~~
~~ """Record successful call."""~~
~~ ...~~

~~ def record_failure(self, key: str) -> None:~~
~~ """Record failed call."""~~
~~ ...~~

~~ def reset(self, key: str) -> None:~~
~~ """Reset circuit state."""~~
~~ ...~~

~~ class RateLimiterProtocol(Protocol):~~
~~ """Protocol for rate limiter managers."""~~

~~ def acquire(self, key: str, permits: int = 1) -> bool:~~
~~ """Try to acquire permits."""~~
~~ ...~~

~~ def remaining(self, key: str) -> int:~~
~~ """Get remaining permits."""~~
~~ ...~~

~~ class TimeoutEnforcerProtocol(Protocol):~~
~~ """Protocol for timeout enforcement."""~~

~~ def execute_with_timeout(~~
~~ self,~~
~~ func: Callable[[], T],~~
~~ timeout_seconds: float,~~
~~ ) -> FlextResult[T]:~~
~~ """Execute function with timeout."""~~
~~ ...~~

~~ class RetryPolicyProtocol(Protocol):~~
~~ """Protocol for retry policies."""~~

~~ def execute_with_retry(~~
~~ self,~~
~~ func: Callable[[], FlextResult[T]],~~
~~ max_attempts: int,~~
~~ backoff_factor: float,~~
~~ ) -> FlextResult[T]:~~
~~ """Execute function with retry logic."""~~
~~ ...~~
~~```~~

### ~~FlextDispatcher V2 Refactored~~ 📋 SPEC PENDENTE

> **STATUS:** Especificação de implementação futura (Phase 2)

~~```Python~~
~~class FlextDispatcher:~~
~~ """CQRS dispatcher with dependency injection."""~~

~~ def **init**(~~
~~ self,~~
~~ container: FlextContainer | None = None,~~
~~ \*,~~
~~ # Legacy support - deprecated, use container instead~~
~~ circuit_breaker: FlextProtocols.CircuitBreakerProtocol | None = None,~~
~~ rate_limiter: FlextProtocols.RateLimiterProtocol | None = None,~~
~~ timeout_enforcer: FlextProtocols.TimeoutEnforcerProtocol | None = None,~~
~~ retry_policy: FlextProtocols.RetryPolicyProtocol | None = None,~~
~~ ) -> None:~~
~~ """Initialize dispatcher with optional container.~~

~~ Args:~~
~~ container: FlextContainer for dependency injection.~~
~~ If provided, managers are resolved from container.~~
~~ If None, uses default implementations.~~

~~ circuit_breaker: Deprecated. Use container.register() instead.~~
~~ rate_limiter: Deprecated. Use container.register() instead.~~
~~ timeout_enforcer: Deprecated. Use container.register() instead.~~
~~ retry_policy: Deprecated. Use container.register() instead.~~
~~ """~~
~~ self.\_container = container or FlextContainer.get_global()~~

~~ # Resolve managers from container or use defaults~~
~~ self.\_circuit_breaker = self.\_resolve_manager(~~
~~ "circuit_breaker",~~
~~ circuit_breaker,~~
~~ CircuitBreakerManager,~~
~~ )~~
~~ self.\_rate_limiter = self.\_resolve_manager(~~
~~ "rate_limiter",~~
~~ rate_limiter,~~
~~ RateLimiterManager,~~
~~ )~~
~~ # ... etc~~

~~ def \_resolve_manager(~~
~~ self,~~
~~ key: str,~~
~~ explicit: T | None,~~
~~ default_factory: Callable[[], T],~~
~~ ) -> T:~~
~~ """Resolve manager from container, explicit, or default."""~~
~~ if explicit is not None:~~
~~ import warnings~~
~~ warnings.warn(~~
~~ f"Passing {key} directly is deprecated. "~~
~~ f"Use container.register('{key}', ...) instead.",~~
~~ DeprecationWarning,~~
~~ stacklevel=3,~~
~~ )~~
~~ return explicit~~

~~ result = self.\_container.get(key)~~
~~ if result.is_success:~~
~~ return result.unwrap()~~

~~ # Create default and register for future use~~
~~ default = default_factory()~~
~~ self.\_container.register(key, default)~~
~~ return default~~
~~```~~

### ~~FlextHandlers V2 Refactored~~ 📋 SPEC PENDENTE

> **STATUS:** Especificação de implementação futura (Phase 1)

~~```Python~~
~~class FlextHandlers(FlextMixins, Generic[TCommand_contra, TResult_co]):~~
~~ """CQRS message handler with automatic infrastructure."""~~

~~ # ✅ V2: CQRS utilities via FlextMixins.CQRS~~
~~ \_cqrs_metrics: FlextMixins.CQRS.MetricsTracker | None = None~~
~~ \_cqrs_context: FlextMixins.CQRS.ContextStack | None = None~~

~~ @property~~
~~ def cqrs_metrics(self) -> FlextMixins.CQRS.MetricsTracker:~~
~~ """Get metrics tracker (lazy initialized)."""~~
~~ if self.\_cqrs_metrics is None:~~
~~ self.\_cqrs_metrics = FlextMixins.CQRS.MetricsTracker()~~
~~ return self.\_cqrs_metrics~~

~~ @property~~
~~ def cqrs_context(self) -> FlextMixins.CQRS.ContextStack:~~
~~ """Get context stack (lazy initialized)."""~~
~~ if self.\_cqrs_context is None:~~
~~ self.\_cqrs_context = FlextMixins.CQRS.ContextStack()~~
~~ return self.\_cqrs_context~~

~~ # ⚠️ Legacy methods - deprecated in V2~~
~~ def record_metric(self, key: str, value: int | float) -> None:~~
~~ """Record a metric value.~~

~~ .. deprecated:: 1.0~~
~~ Use `self.cqrs_metrics.record(key, value)` instead.~~
~~ """~~
~~ import warnings~~
~~ warnings.warn(~~
~~ "record_metric() is deprecated. Use self.cqrs_metrics.record() instead.",~~
~~ DeprecationWarning,~~
~~ stacklevel=2,~~
~~ )~~
~~ self.cqrs_metrics.record(key, value)~~

~~ def get_metrics(self) -> dict[str, int | float]:~~
~~ """Get all recorded metrics.~~

~~ .. deprecated:: 1.0~~
~~ Use `self.cqrs_metrics.all()` instead.~~
~~ """~~
~~ import warnings~~
~~ warnings.warn(~~
~~ "get_metrics() is deprecated. Use self.cqrs_metrics.all() instead.",~~
~~ DeprecationWarning,~~
~~ stacklevel=2,~~
~~ )~~
~~ return self.cqrs_metrics.all()~~

~~ # ... similar deprecation for push_context, pop_context~~

~~ def \_run_pipeline(~~
~~ self,~~
~~ message: TCommand_contra,~~
~~ ) -> FlextResult[TResult_co]:~~
~~ """Run handler pipeline with automatic observability.~~

~~ V2 Enhancement: Automatically uses FlextMixins infrastructure.~~
~~ """~~
~~ # ✅ V2: Automatic logging~~
~~ self.logger.info(~~
~~ f"Processing {type(message).**name**}",~~
~~ extra={"message_type": type(message).**name**},~~
~~ )~~

~~ # ✅ V2: Automatic tracking~~
~~ with self.track(f"handle\_{type(message).**name**}"):~~
~~ # ✅ V2: Automatic context~~
~~ self.cqrs_context.push({"message_id": getattr(message, "id", "unknown")})~~
~~ try:~~
~~ # Run pre-processors~~
~~ for processor in self.\_pre_processors:~~
~~ processor(message)~~

~~ # Execute handler~~
~~ result = self.handle(message)~~

~~ # ✅ V2: Automatic metrics~~
~~ self.cqrs_metrics.record("messages_processed", 1)~~
~~ if result.is_failure:~~
~~ self.cqrs_metrics.record("messages_failed", 1)~~

~~ # Run post-processors~~
~~ for processor in self.\_post_processors:~~
~~ processor(result)~~

~~ return result~~
~~ finally:~~
~~ self.cqrs_context.pop()~~
~~```~~

---

## ~~🔗 Padrões de Integração~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#integration-with-flextservice`
> e `flext-core/docs/guides/service-patterns.md`

### ~~Fronteiras Arquiteturais~~ ✅

~~**FlextService (Tier 2.5):**~~

~~- Serviços de domínio com lógica de negócio~~
~~- Execução via `.result` property~~
~~- Operações auto-contidas~~
~~- Usado por: API endpoints, CLI commands, batch jobs~~

~~**FlextHandlers (Tier 3.1):**~~

~~- Handlers de mensagens para commands/queries/events~~
~~- Pipeline de validação e roteamento~~
~~- Usado por: FlextDispatcher para operações CQRS~~

~~**FlextDispatcher (Tier 3.2):**~~

~~- Orquestração e roteamento~~
~~- Padrões de reliability (circuit breaker, retry, timeout)~~
~~- Usado por: Aplicações com messaging complexo~~

### ~~Quando Usar Cada Camada~~ ✅

> Migrado para: `flext-core/docs/guides/service-patterns.md#when-to-use`

~~| Cenário | Use | Não Use | Racional |~~
~~| --------------------------------- | -------------------------------- | -------------------- | ------------------------------- |~~
~~| Operação de domínio simples | FlextService[T] | FlextHandlers | Sem overhead de messaging |~~
~~| CRUD com validação | FlextService[T] | FlextDispatcher | Execução direta é mais rápida |~~
~~| Command com retry/circuit breaker | FlextDispatcher + Handler | FlextService sozinho | Precisa de reliability patterns |~~
~~| Event sourcing | FlextDispatcher + Event handlers | FlextService | Event routing necessário |~~
~~| HTTP API endpoint | FlextService[T] wrapped | FlextHandlers diret. | Services são API units |~~

### ~~Pattern 1: Service Chamado de Handler~~ ✅

> Migrado para: `flext-core/docs/guides/service-patterns.md#handler-integration`

~~```Python~~
~~class CreateUserCommandHandler(FlextHandlers[CreateUserCommand, User]):~~
~~ """Handler que orquestra, service que executa."""~~

~~ def handle(self, command: CreateUserCommand) -> FlextResult[User]:~~
~~ # Handler orquestra, service executa lógica de domínio~~
~~ validation_service = ValidateEmailService(email=command.email)~~
~~ if validation_service.result.is_failure:~~
~~ return validation_service.result~~

~~ # Use service para criação real~~
~~ creation_service = CreateUserService(~~
~~ name=command.name,~~
~~ email=command.email,~~
~~ )~~
~~ return creation_service.result~~
~~```~~

### ~~Pattern 2: Dispatcher Roteando para Services~~ ✅

~~```Python~~
~~# Register service-based handlers~~
~~dispatcher = FlextDispatcher(container=FlextContainer.get_global())~~

~~dispatcher.register_command(~~
~~ CreateUserCommand,~~
~~ lambda cmd: CreateUserService(name=cmd.name, email=cmd.email).result~~
~~)~~

~~dispatcher.register_query(~~
~~ GetUserQuery,~~
~~ lambda query: GetUserService(user_id=query.user_id).result~~
~~)~~
~~```~~

### ~~Pattern 3: Handler com Full Observability~~ 📋 SPEC PENDENTE

> **STATUS:** Exemplo de implementação futura (Phase 3)

~~```Python~~
~~class ProcessOrderCommandHandler(FlextHandlers[ProcessOrderCommand, Order]):~~
~~ """Handler com observabilidade completa via FlextMixins."""~~

~~ def handle(self, command: ProcessOrderCommand) -> FlextResult[Order]:~~
~~ # ✅ Logging automático via FlextMixins~~
~~ self.logger.info(f"Processing order {command.order_id}")~~

~~ # ✅ Tracking automático via FlextMixins~~
~~ with self.track("process_order"):~~
~~ # ✅ Contexto via FlextMixins.CQRS~~
~~ self.cqrs_context.push({~~
~~ "order_id": command.order_id,~~
~~ "customer_id": command.customer_id,~~
~~ })~~

~~ try:~~
~~ # Business logic~~
~~ order = self.\_process_order(command)~~

~~ # ✅ Métricas via FlextMixins.CQRS~~
~~ self.cqrs_metrics.record("orders_processed", 1)~~
~~ self.cqrs_metrics.record("order_total", order.total)~~

~~ return FlextResult.ok(order)~~
~~ except OrderProcessingError as e:~~
~~ self.cqrs_metrics.record("orders_failed", 1)~~
~~ return FlextResult.fail(str(e))~~
~~ finally:~~
~~ self.cqrs_context.pop()~~
~~```~~

---

## ~~⚙️ Infraestrutura Avançada~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md` (diagramas simplificados)
> **NOTA:** Diagramas detalhados mantidos para referência de implementação

### ~~FlextHandlers Pipeline~~ ✅

~~```~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ Message Input │~~
~~└─────────────────────────┬───────────────────────────────────────┘~~
~~ │~~
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ Pre-Processors │~~
~~│ ┌─────────────┐ ┌──────────────┐ ┌────────────────┐ │~~
~~│ │ Validation │ │ Authorization │ │ Logging │ │~~
~~│ └─────────────┘ └──────────────┘ └────────────────┘ │~~
~~└─────────────────────────┬───────────────────────────────────────┘~~
~~ │~~
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ \_run_pipeline() │~~
~~│ ┌─────────────────────────────────────────────────────────┐ │~~
~~│ │ with self.track("handle_message"): │ │~~
~~│ │ self.logger.info("Processing message") │ │~~
~~│ │ self.cqrs_context.push({"message_id": ...}) │ │~~
~~│ │ result = self.handle(message) │ │~~
~~│ │ self.cqrs_metrics.record("processed", 1) │ │~~
~~│ │ self.cqrs_context.pop() │ │~~
~~│ └─────────────────────────────────────────────────────────┘ │~~
~~└─────────────────────────┬───────────────────────────────────────┘~~
~~ │~~
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ Post-Processors │~~
~~│ ┌─────────────┐ ┌──────────────┐ ┌────────────────┐ │~~
~~│ │ Audit │ │ Notification │ │ Cleanup │ │~~
~~│ └─────────────┘ └──────────────┘ └────────────────┘ │~~
~~└─────────────────────────┬───────────────────────────────────────┘~~
~~ │~~
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ FlextResult[T] │~~
~~└─────────────────────────────────────────────────────────────────┘~~
~~```~~

### ~~FlextDispatcher Reliability Patterns~~ ✅

~~```~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ Message Dispatch │~~
~~└─────────────────────────┬───────────────────────────────────────┘~~
~~ │~~
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ Rate Limiter Check │~~
~~│ ┌─────────────────────────────────────────────────────────┐ │~~
~~│ │ if not rate_limiter.acquire(handler_key): │ │~~
~~│ │ return FlextResult.fail("Rate limit exceeded") │ │~~
~~│ └─────────────────────────────────────────────────────────┘ │~~
~~└─────────────────────────┬───────────────────────────────────────┘~~
│
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ Circuit Breaker Check │~~
~~│ ┌─────────────────────────────────────────────────────────┐ │~~
~~│ │ if circuit_breaker.is_open(handler_key): │ │~~
~~│ │ return FlextResult.fail("Circuit open") │ │~~
~~│ └─────────────────────────────────────────────────────────┘ │~~
~~└─────────────────────────┬───────────────────────────────────────┘~~
~~ │~~
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ Timeout + Retry Execution │~~
~~│ ┌─────────────────────────────────────────────────────────┐ │~~
~~│ │ retry_policy.execute_with_retry( │ │~~
~~│ │ lambda: timeout_enforcer.execute_with_timeout( │ │~~
~~│ │ lambda: handler.handle(message), │ │~~
~~│ │ timeout_seconds, │ │~~
~~│ │ ), │ │~~
~~│ │ max_attempts=3, │ │~~
~~│ │ backoff_factor=2.0, │ │~~
~~│ │ ) │ │~~
~~│ └─────────────────────────────────────────────────────────┘ │~~
~~└─────────────────────────┬───────────────────────────────────────┘~~
~~ │~~
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ Circuit Breaker Update │~~
~~│ ┌─────────────────────────────────────────────────────────┐ │~~
~~│ │ if result.is_success: │ │~~
~~│ │ circuit_breaker.record_success(handler_key) │ │~~
~~│ │ else: │ │~~
~~│ │ circuit_breaker.record_failure(handler_key) │ │~~
~~│ └─────────────────────────────────────────────────────────┘ │~~
~~└─────────────────────────┬───────────────────────────────────────┘~~
~~ │~~
~~ ▼~~
~~┌─────────────────────────────────────────────────────────────────┐~~
~~│ FlextResult[T] │~~
~~└─────────────────────────────────────────────────────────────────┘~~
~~```~~

### ~~Manager Extraction (V2)~~ 📋 SPEC PENDENTE

> **STATUS:** Especificação de implementação futura (Phase 2)

~~**Estrutura de Módulos:**~~

~~```~~
~~flext_core/~~
~~├── \_managers/~~
~~│ ├── **init**.py # Re-exports all managers~~
~~│ ├── circuit_breaker.py # CircuitBreakerManager~~
~~│ ├── rate_limiter.py # RateLimiterManager~~
~~│ ├── timeout_enforcer.py # TimeoutEnforcer~~
~~│ └── retry_policy.py # RetryPolicyManager~~
~~├── dispatcher.py # FlextDispatcher (refactored)~~
~~└── protocols.py # Manager protocols~~
~~```~~

~~**Registro Default no Container:**~~

~~```Python~~
~~# flext_core/\_managers/**init**.py~~
~~from flext_core.container import FlextContainer~~

~~def register_default_managers() -> None:~~
~~ """Register default managers in global container."""~~
~~ container = FlextContainer.get_global()~~

~~ # Only register if not already present~~
~~ if container.get("circuit_breaker").is_failure:~~
~~ from flext_core.\_managers.circuit_breaker import CircuitBreakerManager~~
~~ container.register("circuit_breaker", CircuitBreakerManager())~~

~~ if container.get("rate_limiter").is_failure:~~
~~ from flext_core.\_managers.rate_limiter import RateLimiterManager~~
~~ container.register("rate_limiter", RateLimiterManager())~~

~~ if container.get("timeout_enforcer").is_failure:~~
~~ from flext_core.\_managers.timeout_enforcer import TimeoutEnforcer~~
~~ container.register("timeout_enforcer", TimeoutEnforcer())~~

~~ if container.get("retry_policy").is_failure:~~
~~ from flext_core.\_managers.retry_policy import RetryPolicyManager~~
~~ container.register("retry_policy", RetryPolicyManager())~~
~~```~~

---

## ~~📖 Guia de Implementação~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#handler-patterns`
> e `flext-core/docs/guides/service-patterns.md`

### ~~Setup Básico de Handler (V2)~~ ✅

~~```Python~~
~~from flext_core import FlextHandlers, FlextResult~~

~~class MyCommandHandler(FlextHandlers[MyCommand, MyResult]):~~
~~ """Handler com setup mínimo."""~~

~~ def handle(self, command: MyCommand) -> FlextResult[MyResult]:~~
~~ # Infraestrutura automática via FlextMixins:~~
~~ # - self.logger: FlextLogger~~
~~ # - self.config: FlextSettings~~
~~ # - self.container: FlextContainer~~
~~ # - self.context: FlextContext~~
~~ # - self.track(): Performance tracking~~
~~ # - self.cqrs_metrics: MetricsTracker~~
~~ # - self.cqrs_context: ContextStack~~

~~ self.logger.info(f"Processing {command.id}")~~

~~ with self.track("handle_command"):~~
~~ result = self.\_process(command)~~

~~ self.cqrs_metrics.record("commands_processed", 1)~~

~~ return FlextResult.ok(result)~~
~~```~~

### ~~Setup de Dispatcher com DI (V2)~~ 📋 SPEC PENDENTE

> **STATUS:** Especificação de implementação futura (Phase 2)

~~```Python~~
~~from flext_core import FlextDispatcher, FlextContainer~~

~~# Option 1: Use default managers (auto-registered)~~
~~dispatcher = FlextDispatcher()~~

~~# Option 2: Provide custom container~~
~~container = FlextContainer.get_global()~~
~~container.register("circuit_breaker", CustomCircuitBreaker())~~
~~container.register("rate_limiter", CustomRateLimiter())~~
~~dispatcher = FlextDispatcher(container=container)~~

~~# Register handlers~~
~~dispatcher.register_command(CreateUserCommand, CreateUserHandler())~~
~~dispatcher.register_query(GetUserQuery, GetUserHandler())~~
~~dispatcher.register_event(UserCreatedEvent, UserCreatedHandler())~~

~~# Dispatch messages~~
~~result = dispatcher.dispatch(CreateUserCommand(name="John", email="<john@example.com>"))~~
~~```~~

### ~~Criando Custom Reliability Policy~~ 📋 SPEC PENDENTE

> **STATUS:** Especificação de implementação futura (Phase 2)

~~```Python~~
~~from flext_core import FlextProtocols, FlextResult~~

~~class CustomCircuitBreaker:~~
~~ """Custom circuit breaker implementation."""~~

~~ def **init**(~~
~~ self,~~
~~ failure_threshold: int = 5,~~
~~ recovery_timeout: float = 30.0,~~
~~ ) -> None:~~
~~ self.\_failure_threshold = failure_threshold~~
~~ self.\_recovery_timeout = recovery_timeout~~
~~ self.\_failures: dict[str, int] = {}~~
~~ self.\_last_failure: dict[str, float] = {}~~

~~ def is_open(self, key: str) -> bool:~~
~~ """Check if circuit is open."""~~
~~ failures = self.\_failures.get(key, 0)~~
~~ if failures < self.\_failure_threshold:~~
~~ return False~~

~~ last = self.\_last_failure.get(key, 0)~~
~~ if time.time() - last > self.\_recovery_timeout:~~
~~ # Half-open: allow one attempt~~
~~ return False~~

~~ return True~~

~~ def record_success(self, key: str) -> None:~~
~~ """Record successful call - reset failures."""~~
~~ self.\_failures[key] = 0~~

~~ def record_failure(self, key: str) -> None:~~
~~ """Record failed call."""~~
~~ self.\_failures[key] = self.\_failures.get(key, 0) + 1~~
~~ self.\_last_failure[key] = time.time()~~

~~# Register custom implementation~~
~~container = FlextContainer.get_global()~~
~~container.register("circuit_breaker", CustomCircuitBreaker(~~
~~ failure_threshold=10,~~
~~ recovery_timeout=60.0,~~
~~))~~
~~```~~

---

## ~~🎯 Padrões de Uso~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#handler-patterns`
> e `flext-core/docs/guides/service-patterns.md`

### ~~Simple Command Handling~~ ✅

~~```Python~~
~~from dataclasses import dataclass~~
~~from flext_core import FlextHandlers, FlextResult, FlextDispatcher~~

~~@dataclass~~
~~class CreateUserCommand:~~
~~ name: str~~
~~ email: str~~

~~@dataclass~~
~~class User:~~
~~ id: str~~
~~ name: str~~
~~ email: str~~

~~class CreateUserHandler(FlextHandlers[CreateUserCommand, User]):~~
~~ def handle(self, command: CreateUserCommand) -> FlextResult[User]:~~
~~ self.logger.info(f"Creating user: {command.name}")~~

~~ # Business logic~~
~~ user = User(~~
~~ id=str(uuid.uuid4()),~~
~~ name=command.name,~~
~~ email=command.email,~~
~~ )~~

~~ self.cqrs_metrics.record("users_created", 1)~~

~~ return FlextResult.ok(user)~~

~~# Usage~~
~~dispatcher = FlextDispatcher()~~
~~dispatcher.register_command(CreateUserCommand, CreateUserHandler())~~

~~result = dispatcher.dispatch(CreateUserCommand(name="John", email="<john@example.com>"))~~
~~if result.is_success:~~
~~ user = result.unwrap()~~
~~ print(f"Created user: {user.id}")~~
~~```~~

### ~~Query with Caching~~ ✅

~~```Python~~
~~@dataclass~~
~~class GetUserQuery:~~
~~ user_id: str~~

~~class GetUserHandler(FlextHandlers[GetUserQuery, User]):~~
~~ \_cache: dict[str, User] = {}~~

~~ def handle(self, query: GetUserQuery) -> FlextResult[User]:~~
~~ # Check cache first~~
~~ if query.user_id in self.\_cache:~~
~~ self.cqrs_metrics.record("cache_hits", 1)~~
~~ return FlextResult.ok(self.\_cache[query.user_id])~~

~~ self.cqrs_metrics.record("cache_misses", 1)~~

~~ # Fetch from repository~~
~~ with self.track("fetch_user"):~~
~~ user = self.\_fetch_user(query.user_id)~~

~~ if user is None:~~
~~ return FlextResult.fail(f"User not found: {query.user_id}")~~

~~ # Cache result~~
~~ self.\_cache[query.user_id] = user~~

~~ return FlextResult.ok(user)~~
~~```~~

### ~~Event Processing with Audit~~ ✅

~~```Python~~
~~@dataclass~~
~~class UserCreatedEvent:~~
~~ user_id: str~~
~~ name: str~~
~~ email: str~~
~~ created_at: datetime~~

~~class UserCreatedHandler(FlextHandlers[UserCreatedEvent, None]):~~
~~ def handle(self, event: UserCreatedEvent) -> FlextResult[bool]:~~
~~ self.cqrs_context.push({~~
~~ "event_type": "UserCreated",~~
~~ "user_id": event.user_id,~~
~~ "timestamp": event.created_at.isoformat(),~~
~~ })~~

~~ try:~~
~~ # Send welcome email~~
~~ self.\_send_welcome_email(event)~~
~~ self.cqrs_metrics.record("welcome_emails_sent", 1)~~

~~ # Update analytics~~
~~ self.\_update_analytics(event)~~

~~ # Audit log~~
~~ self.logger.info(~~
~~ "User created event processed",~~
~~ extra=self.cqrs_context.current(),~~
~~ )~~

~~ return FlextResult.| ok(value=True)~~
~~ except Exception as e:~~
~~ self.cqrs_metrics.record("event_processing_errors", 1)~~
~~ return FlextResult.fail(str(e))~~
~~ finally:~~
~~ self.cqrs_context.pop()~~
~~```~~

### ~~Multi-Operation Handler~~ ✅

~~```Python~~
~~@dataclass~~
~~class ProcessOrderCommand:~~
~~ order_id: str~~
~~ customer_id: str~~
~~ items: list[OrderItem]~~

~~class ProcessOrderHandler(FlextHandlers[ProcessOrderCommand, Order]):~~
~~ def handle(self, command: ProcessOrderCommand) -> FlextResult[Order]:~~
~~ self.cqrs_context.push({~~
~~ "order_id": command.order_id,~~
~~ "customer_id": command.customer_id,~~
~~ "item_count": len(command.items),~~
~~ })~~

~~ try:~~
~~ # Step 1: Validate inventory~~
~~ with self.track("validate_inventory"):~~
~~ for item in command.items:~~
~~ if not self.\_check_inventory(item):~~
~~ return FlextResult.fail(f"Item out of stock: {item.product_id}")~~

~~ # Step 2: Reserve inventory~~
~~ with self.track("reserve_inventory"):~~
~~ reservation_ids = self.\_reserve_items(command.items)~~

~~ # Step 3: Process payment~~
~~ with self.track("process_payment"):~~
~~ payment_result = self.\_process_payment(command)~~
~~ if payment_result.is_failure:~~
~~ # Rollback reservations~~
~~ self.\_release_reservations(reservation_ids)~~
~~ return payment_result~~

~~ # Step 4: Create order~~
~~ with self.track("create_order"):~~
~~ order = self.\_create_order(command, payment_result.unwrap())~~

~~ # Record metrics~~
~~ self.cqrs_metrics.record("orders_processed", 1)~~
~~ self.cqrs_metrics.record("items_processed", len(command.items))~~
~~ self.cqrs_metrics.record("order_total", order.total)~~

~~ return FlextResult.ok(order)~~

~~ except Exception as e:~~
~~ self.cqrs_metrics.record("orders_failed", 1)~~
~~ self.logger.error(f"Order processing failed: {e}")~~
~~ return FlextResult.fail(str(e))~~
~~ finally:~~
~~ self.cqrs_context.pop()~~
~~```~~

---

## ~~🔄 Guia de Migração~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#handler-patterns` (Migration Path)

### ~~De Métricas Manuais para FlextMixins.CQRS~~ ✅

~~**Antes (V1):**~~

~~```Python~~
~~class MyHandler(FlextHandlers[MyCommand, MyResult]):~~
~~ def handle(self, command: MyCommand) -> FlextResult[MyResult]:~~
~~ # ❌ V1: Métricas manuais~~
~~ self.record_metric("commands_processed", 1)~~

~~ result = self.\_process(command)~~

~~ if result.is_failure:~~
~~ self.record_metric("commands_failed", 1)~~

~~ return result~~
~~```~~

~~**Depois (V2):**~~

~~```Python~~
~~class MyHandler(FlextHandlers[MyCommand, MyResult]):~~
~~ def handle(self, command: MyCommand) -> FlextResult[MyResult]:~~
~~ # ✅ V2: Métricas via FlextMixins.CQRS~~
~~ self.cqrs_metrics.record("commands_processed", 1)~~

~~ result = self.\_process(command)~~

~~ if result.is_failure:~~
~~ self.cqrs_metrics.record("commands_failed", 1)~~

~~ return result~~
~~```~~

### ~~De Managers Hardcoded para DI~~ ✅

~~**Antes (V1):**~~

~~```python~~
~~# ❌ V1: Não é possível customizar managers~~
~~dispatcher = FlextDispatcher()~~
~~# Managers são criados internamente com configuração default~~
~~```~~

~~**Depois (V2):**~~

~~```Python~~
~~# ✅ V2: Managers via DI~~
~~from flext_core import FlextContainer, FlextDispatcher~~

~~# Option A: Use defaults (registered automatically)~~
~~dispatcher = FlextDispatcher()~~

~~# Option B: Custom managers~~
~~container = FlextContainer.get_global()~~
~~container.register("circuit_breaker", CustomCircuitBreaker(~~
~~ failure_threshold=10,~~
~~ recovery_timeout=60.0,~~
~~))~~
~~container.register("rate_limiter", CustomRateLimiter(~~
~~ max_requests=1000,~~
~~ time_window=60.0,~~
~~))~~
~~dispatcher = FlextDispatcher(container=container)~~
~~```~~

### ~~Deprecation Timeline~~ ✅ MIGRADO

> Migrado para: `flext-core/docs/architecture/cqrs.md#handler-patterns` (Migration Path)

~~| Método | Status V1 | Status V2 | Remoção |~~
~~| -------------------------------------- | ------------ | ------------- | ------------- |~~
~~| `record_metric()` | ✅ Funcional | ⚠️ Deprecated | V3 (6+ meses) |~~
~~| `get_metrics()` | ✅ Funcional | ⚠️ Deprecated | V3 (6+ meses) |~~
~~| `push_context()` | ✅ Funcional | ⚠️ Deprecated | V3 (6+ meses) |~~
~~| `pop_context()` | ✅ Funcional | ⚠️ Deprecated | V3 (6+ meses) |~~
~~| `FlextDispatcher(circuit_breaker=...)` | ✅ Funcional | ⚠️ Deprecated | V3 (6+ meses) |~~
~~| `FlextDispatcher(rate_limiter=...)` | ✅ Funcional | ⚠️ Deprecated | V3 (6+ meses) |~~

### ~~Warnings Durante Migração~~ ✅

~~```Python~~
~~# O que você verá durante o grace period:~~

~~>>> handler.record_metric("key", 1)~~
~~DeprecationWarning: record_metric() is deprecated.~~
~~Use self.cqrs_metrics.record() instead.~~
~~Will be removed in version 3.0.~~

~~>>> dispatcher = FlextDispatcher(circuit_breaker=custom_cb)~~
~~DeprecationWarning: Passing circuit_breaker directly is deprecated.~~
~~Use container.register('circuit_breaker', ...) instead.~~
~~Will be removed in version 3.0.~~
~~```~~

---

## ~~📝 Exemplos~~ 📋 EXEMPLOS PRESERVADOS

> **NOTA:** Esta seção contém exemplos extensivos de implementação.
> Mantida como referência até implementação completa do V2.
> Exemplos básicos migrados para `cqrs.md` e `service-patterns.md`.

### ~~Exemplo 1: CQRS Application Completo~~ 📋

> Exemplo extensivo - manter como referência de implementação

~~```Python~~
~~"""Complete CQRS application with FlextHandlers and FlextDispatcher."""~~

~~from dataclasses import dataclass~~
~~from datetime import datetime~~
~~from typing import ClassVar~~
~~import uuid~~

~~from flext_core import (~~
~~ FlextContainer,~~
~~ FlextDispatcher,~~
~~ FlextHandlers,~~
~~ FlextResult,~~
~~)~~

~~# Domain Models~~
~~@dataclass~~
~~class User:~~
~~ id: str~~
~~ name: str~~
~~ email: str~~
~~ created_at: datetime~~

~~# Commands~~
~~@dataclass~~
~~class CreateUserCommand:~~
~~ name: str~~
~~ email: str~~

~~@dataclass~~
~~class UpdateUserCommand:~~
~~ user_id: str~~
~~ name: str | None = None~~
~~ email: str | None = None~~

~~# Queries~~
~~@dataclass~~
~~class GetUserQuery:~~
~~ user_id: str~~

~~@dataclass~~
~~class ListUsersQuery:~~
~~ limit: int = 100~~
~~ offset: int = 0~~

~~# Events~~
~~@dataclass~~
~~class UserCreatedEvent:~~
~~ user_id: str~~
~~ name: str~~
~~ email: str~~
~~ created_at: datetime~~

~~# In-memory repository (for demo)~~
~~class UserRepository:~~
~~ \_users: ClassVar[dict[str, User]] = {}~~

~~ @classmethod~~
~~ def save(cls, user: User) -> None:~~
~~ cls.\_users[user.id] = user~~

~~ @classmethod~~
~~ def get(cls, user_id: str) -> User | None:~~
~~ return cls.\_users.get(user_id)~~

~~ @classmethod~~
~~ def list(cls, limit: int, offset: int) -> list[User]:~~
~~ users = list(cls.\_users.values())~~
~~ return users[offset:offset + limit]~~

~~# Command Handlers~~
~~class CreateUserHandler(FlextHandlers[CreateUserCommand, User]):~~
~~ def handle(self, command: CreateUserCommand) -> FlextResult[User]:~~
~~ self.logger.info(f"Creating user: {command.name}")~~

~~ with self.track("create_user"):~~
user = User(
id=str(uuid.uuid4()),
name=command.name,
email=command.email,
created_at=datetime.now(),
)
UserRepository.save(user)

        self.cqrs_metrics.record("users_created", 1)

        # Publish event (in real app, use event bus)
        self.logger.info(f"User created: {user.id}")

        return FlextResult.ok(user)

class UpdateUserHandler(h[UpdateUserCommand, User]):
def handle(self, command: UpdateUserCommand) -> FlextResult[User]:
self.logger.info(f"Updating user: {command.user_id}")

        user = UserRepository.get(command.user_id)
        if user is None:
            return FlextResult.fail(f"User not found: {command.user_id}")

        with self.track("update_user"):
            if command.name is not None:
                user.name = command.name
            if command.email is not None:
                user.email = command.email
            UserRepository.save(user)

        self.cqrs_metrics.record("users_updated", 1)

        return FlextResult.ok(user)

# Query Handlers

class GetUserHandler(h[GetUserQuery, User]):
def handle(self, query: GetUserQuery) -> FlextResult[User]:
self.logger.debug(f"Getting user: {query.user_id}")

        with self.track("get_user"):
            user = UserRepository.get(query.user_id)

        if user is None:
            self.cqrs_metrics.record("users_not_found", 1)
            return FlextResult.fail(f"User not found: {query.user_id}")

        self.cqrs_metrics.record("users_found", 1)
        return FlextResult.ok(user)

class ListUsersHandler(h[ListUsersQuery, list[User]]):
def handle(self, query: ListUsersQuery) -> FlextResult[list[User]]:
self.logger.debug(f"Listing users: limit={query.limit}, offset={query.offset}")

        with self.track("list_users"):
            users = UserRepository.list(query.limit, query.offset)

        self.cqrs_metrics.record("users_listed", len(users))
        return FlextResult.ok(users)

# Event Handlers

class UserCreatedHandler(h[UserCreatedEvent, None]):
def handle(self, event: UserCreatedEvent) -> FlextResult[bool]:
self.logger.info(f"Processing UserCreatedEvent: {event.user_id}")

        self.cqrs_context.push({
            "event": "UserCreated",
            "user_id": event.user_id,
        })

        try:
            # Simulate sending welcome email
            with self.track("send_welcome_email"):
                self.logger.info(f"Sending welcome email to {event.email}")

            self.cqrs_metrics.record("welcome_emails_sent", 1)
            return FlextResult.| ok(value=True)
        finally:
            self.cqrs_context.pop()

# Application Setup

def create_dispatcher() -> FlextDispatcher:
"""Create and configure dispatcher."""
container = FlextContainer.get_global()
dispatcher = FlextDispatcher(container=container)

    # Register command handlers
    dispatcher.register_command(CreateUserCommand, CreateUserHandler())
    dispatcher.register_command(UpdateUserCommand, UpdateUserHandler())

    # Register query handlers
    dispatcher.register_query(GetUserQuery, GetUserHandler())
    dispatcher.register_query(ListUsersQuery, ListUsersHandler())

    # Register event handlers
    dispatcher.register_event(UserCreatedEvent, UserCreatedHandler())

    return dispatcher

# Usage

if **name** == "**main**":
dispatcher = create_dispatcher()

    # Create user
    result = dispatcher.dispatch(CreateUserCommand(
        name="John Doe",
        email="john@example.com",
    ))

    if result.is_success:
        user = result.unwrap()
        print(f"Created user: {user.id}")

        # Get user
        get_result = dispatcher.dispatch(GetUserQuery(user_id=user.id))
        if get_result.is_success:
            found_user = get_result.unwrap()
            print(f"Found user: {found_user.name}")

        # List users
        list_result = dispatcher.dispatch(ListUsersQuery(limit=10))
        if list_result.is_success:
            users = list_result.unwrap()
            print(f"Total users: {len(users)}")
    else:
        print(f"Error: {result.error}")

````

### Exemplo 2: Custom Circuit Breaker

```python
"""Custom circuit breaker with metrics and logging."""

import time
from dataclasses import dataclass, field
from typing import Callable

from flext_core import FlextLogger, FlextResult


@dataclass
class CircuitState:
    """State of a circuit."""
    failures: int = 0
    successes: int = 0
    last_failure_time: float = 0
    state: str = "closed"  # closed, open, half_open


class CustomCircuitBreaker:
    """Circuit breaker with configurable thresholds and metrics."""

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        recovery_timeout: float = 30.0,
        logger: FlextLogger | None = None,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._success_threshold = success_threshold
        self._recovery_timeout = recovery_timeout
        self._circuits: dict[str, CircuitState] = {}
        self._logger = logger or FlextLogger(__name__)

    def _get_circuit(self, key: str) -> CircuitState:
        if key not in self._circuits:
            self._circuits[key] = CircuitState()
        return self._circuits[key]

    def is_open(self, key: str) -> bool:
        circuit = self._get_circuit(key)

        if circuit.state == "closed":
            return False

        if circuit.state == "open":
            # Check if recovery timeout has passed
            if time.time() - circuit.last_failure_time > self._recovery_timeout:
                circuit.state = "half_open"
                self._logger.info(f"Circuit {key} transitioning to half_open")
                return False
            return True

        # half_open: allow one request through
        return False

    def record_success(self, key: str) -> None:
        circuit = self._get_circuit(key)
        circuit.successes += 1

        if circuit.state == "half_open":
            if circuit.successes >= self._success_threshold:
                circuit.state = "closed"
                circuit.failures = 0
                circuit.successes = 0
                self._logger.info(f"Circuit {key} closed after recovery")
        elif circuit.state == "closed":
            # Reset failure count on success
            circuit.failures = 0

    def record_failure(self, key: str) -> None:
        circuit = self._get_circuit(key)
        circuit.failures += 1
        circuit.last_failure_time = time.time()

        if circuit.state == "half_open":
            # Immediately re-open on failure during half_open
            circuit.state = "open"
            circuit.successes = 0
            self._logger.warning(f"Circuit {key} re-opened during half_open")
        elif circuit.failures >= self._failure_threshold:
            circuit.state = "open"
            self._logger.warning(f"Circuit {key} opened after {circuit.failures} failures")

    def reset(self, key: str) -> None:
        if key in self._circuits:
            del self._circuits[key]

    def get_state(self, key: str) -> str:
        return self._get_circuit(key).state

    def get_metrics(self, key: str) -> dict[str, int | float | str]:
        circuit = self._get_circuit(key)
        return {
            "state": circuit.state,
            "failures": circuit.failures,
            "successes": circuit.successes,
            "last_failure_time": circuit.last_failure_time,
        }


# Register with container
from flext_core import FlextContainer

container = FlextContainer.get_global()
container.register("circuit_breaker", CustomCircuitBreaker(
    failure_threshold=10,
    recovery_timeout=60.0,
))
````

### Exemplo 3: Handler com Full Observability

```python
"""Handler with comprehensive observability."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from flext_core import h, FlextResult


@dataclass
class ProcessPaymentCommand:
    order_id: str
    amount: float
    currency: str
    payment_method: str
    customer_id: str


@dataclass
class PaymentResult:
    transaction_id: str
    status: str
    amount: float
    currency: str
    processed_at: datetime


class ProcessPaymentHandler(h[ProcessPaymentCommand, PaymentResult]):
    """Payment handler with full observability."""

    def handle(self, command: ProcessPaymentCommand) -> FlextResult[PaymentResult]:
        # Setup context for tracing
        self.cqrs_context.push({
            "operation": "process_payment",
            "order_id": command.order_id,
            "customer_id": command.customer_id,
            "amount": command.amount,
            "currency": command.currency,
        })

        try:
            # Log start
            self.logger.info(
                "Processing payment",
                extra={
                    "order_id": command.order_id,
                    "amount": command.amount,
                    "currency": command.currency,
                },
            )

            # Step 1: Validate payment method
            with self.track("validate_payment_method"):
                validation_result = self._validate_payment_method(command)
                if validation_result.is_failure:
                    self.cqrs_metrics.record("payment_validation_failures", 1)
                    return validation_result

            # Step 2: Check fraud
            with self.track("fraud_check"):
                fraud_result = self._check_fraud(command)
                if fraud_result.is_failure:
                    self.cqrs_metrics.record("fraud_rejections", 1)
                    self.logger.warning(
                        "Payment rejected due to fraud check",
                        extra={"order_id": command.order_id},
                    )
                    return fraud_result

            # Step 3: Process with payment gateway
            with self.track("payment_gateway"):
                gateway_result = self._process_with_gateway(command)
                if gateway_result.is_failure:
                    self.cqrs_metrics.record("gateway_failures", 1)
                    return gateway_result

            transaction_id = gateway_result.unwrap()

            # Step 4: Create result
            result = PaymentResult(
                transaction_id=transaction_id,
                status="completed",
                amount=command.amount,
                currency=command.currency,
                processed_at=datetime.now(),
            )

            # Record success metrics
            self.cqrs_metrics.record("payments_processed", 1)
            self.cqrs_metrics.record("payment_amount_total", command.amount)

            # Log success
            self.logger.info(
                "Payment processed successfully",
                extra={
                    "order_id": command.order_id,
                    "transaction_id": transaction_id,
                    "amount": command.amount,
                },
            )

            return FlextResult.ok(result)

        except Exception as e:
            # Record failure metrics
            self.cqrs_metrics.record("payment_errors", 1)

            # Log error with full context
            self.logger.error(
                f"Payment processing failed: {e}",
                extra={
                    **self.cqrs_context.current(),
                    "error": str(e),
                },
            )

            return FlextResult.fail(str(e))
        finally:
            self.cqrs_context.pop()

    def _validate_payment_method(
        self,
        command: ProcessPaymentCommand,
    ) -> FlextResult[bool]:
        """Validate payment method is supported."""
        supported = ["credit_card", "debit_card", "pix", "boleto"]
        if command.payment_method not in supported:
            return FlextResult.fail(f"Unsupported payment method: {command.payment_method}")
        return FlextResult.| ok(value=True)

    def _check_fraud(
        self,
        command: ProcessPaymentCommand,
    ) -> FlextResult[bool]:
        """Check for potential fraud."""
        # Simplified fraud check
        if command.amount > 10000:
            return FlextResult.fail("Amount exceeds fraud threshold")
        return FlextResult.| ok(value=True)

    def _process_with_gateway(
        self,
        command: ProcessPaymentCommand,
    ) -> FlextResult[str]:
        """Process payment with external gateway."""
        # Simulated gateway call
        import uuid
        transaction_id = str(uuid.uuid4())
        return FlextResult.ok(transaction_id)
```

---

## ~~📊 Estudos de Caso~~ 📋 EXEMPLOS PRESERVADOS

> **NOTA:** Estudos de caso com implementações específicas para flext-ldif e flext-api.
> Manter como referência até implementação completa do V2.

### ~~Estudo de Caso: flext-ldif~~ 📋

> Exemplo extensivo - manter como referência

~~**Contexto:** Processamento em batch de arquivos LDIF com handlers CQRS.~~

~~**Antes (V1):**~~

~~- Métricas manuais em cada handler~~
~~- Contexto gerenciado manualmente~~
~~- Sem logging estruturado~~

~~**Depois (V2):**~~

~~- FlextMixins.CQRS para métricas unificadas~~
~~- Contexto automático via FlextMixins~~
~~- Logging estruturado com correlation IDs~~

~~```Python~~
~~# flext-ldif: Batch processing handler V2~~
~~class ProcessLdifBatchHandler(FlextHandlers[ProcessLdifBatchCommand, BatchResult]):~~
~~ def handle(self, command: ProcessLdifBatchCommand) -> FlextResult[BatchResult]:~~
~~ self.cqrs_context.push({~~
~~ "batch_id": command.batch_id,~~
~~ "file_count": len(command.files),~~
~~ })~~

~~ try:~~
~~ processed = 0~~
~~ errors = 0~~

~~ for file*path in command.files:~~
~~ with self.track(f"process_file*{file_path.name}"):~~
~~ result = self.\_process_file(file_path)~~
if result.is_success:
processed += 1
else:
errors += 1
self.logger.warning(f"Failed to process {file_path}: {result.error}")

            self.cqrs_metrics.record("files_processed", processed)
            self.cqrs_metrics.record("files_failed", errors)
            self.cqrs_metrics.record("batches_completed", 1)

            return FlextResult.ok(BatchResult(processed=processed, errors=errors))
        finally:
            self.cqrs_context.pop()

````

### Estudo de Caso: flext-api

**Contexto:** HTTP endpoints como Commands/Queries via dispatcher.

**Arquitetura:**

- FastAPI endpoints delegam para FlextDispatcher
- Commands para operações de escrita (POST, PUT, DELETE)
- Queries para operações de leitura (GET)

```python
# flext-api: HTTP endpoint to CQRS bridge
from fastapi import APIRouter, HTTPException
from flext_core import FlextDispatcher

router = APIRouter()
dispatcher = FlextDispatcher()

@router.post("/users")
async def create_user(request: CreateUserRequest) -> UserResponse:
    """Create user via CQRS command."""
    command = CreateUserCommand(
        name=request.name,
        email=request.email,
    )

    result = dispatcher.dispatch(command)

    if result.is_failure:
        raise HTTPException(status_code=400, detail=result.error)

    user = result.unwrap()
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
    )

@router.get("/users/{user_id}")
async def get_user(user_id: str) -> UserResponse:
    """Get user via CQRS query."""
    query = GetUserQuery(user_id=user_id)

    result = dispatcher.dispatch(query)

    if result.is_failure:
        raise HTTPException(status_code=404, detail=result.error)

    user = result.unwrap()
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
    )
````

### Estudo de Caso: client-a-oud-mig

**Contexto:** Pipeline de migração OUD com audit trail completo.

**Requisitos:**

- Rastreabilidade completa de cada operação
- Métricas detalhadas para relatórios
- Contexto persistido para debugging

```python
# client-a-oud-mig: Migration pipeline handler
class MigrateEntryHandler(h[MigrateEntryCommand, MigrationResult]):
    def handle(self, command: MigrateEntryCommand) -> FlextResult[MigrationResult]:
        self.cqrs_context.push({
            "migration_id": command.migration_id,
            "entry_dn": command.entry.dn,
            "entry_type": command.entry.object_class,
            "phase": "migration",
        })

        try:
            # Phase 1: Validate entry
            with self.track("validate_entry"):
                validation = self._validate_entry(command.entry)
                if validation.is_failure:
                    self.cqrs_metrics.record("validation_failures", 1)
                    return validation

            # Phase 2: Transform entry
            with self.track("transform_entry"):
                transformed = self._transform_entry(command.entry)

            # Phase 3: Apply to target
            with self.track("apply_to_target"):
                apply_result = self._apply_to_target(transformed)
                if apply_result.is_failure:
                    self.cqrs_metrics.record("apply_failures", 1)
                    return apply_result

            # Phase 4: Verify migration
            with self.track("verify_migration"):
                verification = self._verify_migration(command.entry.dn)
                if verification.is_failure:
                    self.cqrs_metrics.record("verification_failures", 1)
                    return verification

            # Record success
            self.cqrs_metrics.record("entries_migrated", 1)
            self.cqrs_metrics.record(f"migrated_{command.entry.object_class}", 1)

            # Audit log
            self.logger.info(
                "Entry migrated successfully",
                extra={
                    **self.cqrs_context.current(),
                    "status": "success",
                },
            )

            return FlextResult.ok(MigrationResult(
                entry_dn=command.entry.dn,
                status="migrated",
                verification_passed=True,
            ))

        except Exception as e:
            self.cqrs_metrics.record("migration_errors", 1)
            self.logger.error(
                f"Migration failed: {e}",
                extra={
                    **self.cqrs_context.current(),
                    "error": str(e),
                },
            )
            return FlextResult.fail(str(e))
        finally:
            self.cqrs_context.pop()
```

---

## ~~✅ Validação e Testes~~ 📋 EXEMPLOS DE TESTES PRESERVADOS

> _Esta seção contém exemplos de código de testes. A estrutura foi migrada para cqrs.md._
> Veja: `flext-core/docs/architecture/cqrs.md` → Testing Structure

### ~~Estrutura de Testes CQRS~~

```
tests/
├── unit/
│   ├── test_handlers.py           # h unit tests
│   ├── test_dispatcher.py         # FlextDispatcher unit tests
│   ├── test_mixins_cqrs.py        # x.CQRS tests
│   └── test_managers/
│       ├── test_circuit_breaker.py
│       ├── test_rate_limiter.py
│       ├── test_timeout_enforcer.py
│       └── test_retry_policy.py
├── integration/
│   ├── test_dispatcher_handlers.py # Dispatcher + Handlers
│   ├── test_container_di.py        # DI integration
│   └── test_full_pipeline.py       # End-to-end tests
└── performance/
    ├── test_handler_throughput.py
    └── test_dispatcher_latency.py
```

### Testes para x.CQRS

```python
"""Tests for x.CQRS utilities."""

import pytest
from flext_core.mixins import x


class TestMetricsTracker:
    """Tests for x.CQRS.MetricsTracker."""

    def test_record_metric(self) -> None:
        tracker = x.CQRS.MetricsTracker()

        tracker.record("key", 1)
        tracker.record("key", 2)

        assert tracker.get("key") == 3

    def test_get_nonexistent_metric(self) -> None:
        tracker = x.CQRS.MetricsTracker()

        assert tracker.get("nonexistent") == 0

    def test_all_metrics(self) -> None:
        tracker = x.CQRS.MetricsTracker()

        tracker.record("a", 1)
        tracker.record("b", 2)

        assert tracker.all() == {"a": 1, "b": 2}

    def test_reset_metrics(self) -> None:
        tracker = x.CQRS.MetricsTracker()

        tracker.record("key", 1)
        tracker.reset()

        assert tracker.all() == {}

    def test_thread_safety(self) -> None:
        import threading

        tracker = x.CQRS.MetricsTracker()
        threads = []

        def increment() -> None:
            for _ in range(1000):
                tracker.record("counter", 1)

        for _ in range(10):
            t = threading.Thread(target=increment)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert tracker.get("counter") == 10000


class TestContextStack:
    """Tests for x.CQRS.ContextStack."""

    def test_push_pop(self) -> None:
        stack = x.CQRS.ContextStack()

        stack.push({"a": 1})
        stack.push({"b": 2})

        assert stack.pop() == {"b": 2}
        assert stack.pop() == {"a": 1}
        assert stack.pop() is None

    def test_current_context(self) -> None:
        stack = x.CQRS.ContextStack()

        stack.push({"a": 1, "b": 2})
        stack.push({"b": 3, "c": 4})  # b overrides

        current = stack.current()

        assert current == {"a": 1, "b": 3, "c": 4}
```

### Testes para FlextDispatcher DI

```python
"""Tests for FlextDispatcher dependency injection."""

import pytest
from flext_core import FlextContainer, FlextDispatcher, h, FlextResult


class MockCircuitBreaker:
    """Mock circuit breaker for testing."""

    def __init__(self) -> None:
        self.is_open_calls: list[str] = []
        self.record_success_calls: list[str] = []
        self.record_failure_calls: list[str] = []
        self._open_circuits: set[str] = set()

    def is_open(self, key: str) -> bool:
        self.is_open_calls.append(key)
        return key in self._open_circuits

    def record_success(self, key: str) -> None:
        self.record_success_calls.append(key)
        self._open_circuits.discard(key)

    def record_failure(self, key: str) -> None:
        self.record_failure_calls.append(key)

    def force_open(self, key: str) -> None:
        self._open_circuits.add(key)


class TestDispatcherDI:
    """Tests for dispatcher dependency injection."""

    def test_dispatcher_uses_container_managers(self) -> None:
        # Setup
        container = FlextContainer()
        mock_cb = MockCircuitBreaker()
        container.register("circuit_breaker", mock_cb)

        dispatcher = FlextDispatcher(container=container)

        # Register a simple handler
        class TestHandler(h[str, str]):
            def handle(self, message: str) -> FlextResult[str]:
                return FlextResult.ok(f"processed: {message}")

        dispatcher.register_command(str, TestHandler())

        # Dispatch
        dispatcher.dispatch("test")

        # Verify mock was used
        assert len(mock_cb.is_open_calls) > 0
        assert len(mock_cb.record_success_calls) > 0

    def test_dispatcher_with_open_circuit(self) -> None:
        # Setup
        container = FlextContainer()
        mock_cb = MockCircuitBreaker()
        mock_cb.force_open("str")  # Force circuit open
        container.register("circuit_breaker", mock_cb)

        dispatcher = FlextDispatcher(container=container)

        class TestHandler(h[str, str]):
            def handle(self, message: str) -> FlextResult[str]:
                return FlextResult.ok(f"processed: {message}")

        dispatcher.register_command(str, TestHandler())

        # Dispatch should fail due to open circuit
        result = dispatcher.dispatch("test")

        assert result.is_failure
        assert "circuit" in result.error.lower()
```

### Performance Benchmarks

```python
"""Performance benchmarks for CQRS tier."""

import time
from dataclasses import dataclass

import pytest
from flext_core import FlextDispatcher, h, FlextResult


@dataclass
class BenchmarkCommand:
    value: int


class BenchmarkHandler(h[BenchmarkCommand, int]):
    def handle(self, command: BenchmarkCommand) -> FlextResult[int]:
        return FlextResult.ok(command.value * 2)


class TestHandlerThroughput:
    """Throughput benchmarks for handlers."""

    def test_handler_throughput(self) -> None:
        """Benchmark handler execution throughput."""
        handler = BenchmarkHandler()
        iterations = 10000

        start = time.perf_counter()
        for i in range(iterations):
            handler.handle(BenchmarkCommand(value=i))
        elapsed = time.perf_counter() - start

        throughput = iterations / elapsed

        # Assert minimum throughput (adjust based on requirements)
        assert throughput > 50000, f"Throughput {throughput:.0f} ops/sec below minimum"

        print(f"Handler throughput: {throughput:.0f} ops/sec")


class TestDispatcherLatency:
    """Latency benchmarks for dispatcher."""

    def test_dispatcher_latency(self) -> None:
        """Benchmark dispatcher latency."""
        dispatcher = FlextDispatcher()
        dispatcher.register_command(BenchmarkCommand, BenchmarkHandler())

        # Warmup
        for i in range(100):
            dispatcher.dispatch(BenchmarkCommand(value=i))

        # Measure
        iterations = 1000
        latencies = []

        for i in range(iterations):
            start = time.perf_counter()
            dispatcher.dispatch(BenchmarkCommand(value=i))
            elapsed = (time.perf_counter() - start) * 1000  # ms
            latencies.append(elapsed)

        avg_latency = sum(latencies) / len(latencies)
        p99_latency = sorted(latencies)[int(iterations * 0.99)]

        # Assert maximum latency (adjust based on requirements)
        assert avg_latency < 1.0, f"Avg latency {avg_latency:.3f}ms above maximum"
        assert p99_latency < 5.0, f"P99 latency {p99_latency:.3f}ms above maximum"

        print(f"Dispatcher latency: avg={avg_latency:.3f}ms, p99={p99_latency:.3f}ms")
```

---

## ~~📚 Referências~~ ✅ MIGRADO

> _Seção migrada para `flext-core/docs/architecture/cqrs.md` → External References_

~~### Documentos Relacionados~~

~~- [FLEXT_SERVICE_ARCHITECTURE.md](./FLEXT_SERVICE_ARCHITECTURE.md) - Arquitetura de serviços (Tier 2.5)~~
~~- [flext-core/CLAUDE.md](../flext-core/CLAUDE.md) - Guidelines do projeto core~~
~~- [README.md](../flext-core/README.md) - Visão geral do flext-core~~

~~### Padrões CQRS~~

~~- [Martin Fowler - CQRS](https://martinfowler.com/bliki/CQRS.html)~~
~~- [Microsoft - CQRS Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)~~
~~- [Greg Young - CQRS Documents](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf)~~

~~### Padrões de Reliability~~

~~- [Microsoft - Circuit Breaker Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)~~
~~- [Microsoft - Retry Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)~~
~~- [Netflix - Hystrix (Circuit Breaker)](https://github.com/Netflix/Hystrix/wiki)~~

---

## ~~📋 Plano de Execução - CQRS Modernization~~ 📋 SPEC PENDENTE

> _Esta seção contém o plano de execução detalhado. Mantida como referência para implementação futura._
> Roadmap resumido disponível em: `flext-core/docs/architecture/cqrs.md` → Modernization Roadmap

### ~~Classes Cross-Cutting e Integração CQRS (25 Nov 2025)~~

> 📚 **Análise validada contra código:** flext-core v0.9.9

#### Como FlextDecorators Integra com CQRS

FlextDecorators fornece 10 decorators que podem ser usados diretamente em handlers:

```python
class CreateUserHandler(h[CreateUserCommand, User]):
    """Handler usando FlextDecorators para cross-cutting concerns."""

    @FlextDecorators.track_performance("create_user")  # Performance automático
    @FlextDecorators.with_context(handler="CreateUserHandler")  # Context automático
    @FlextDecorators.retry(max_attempts=3)  # Retry automático
    def handle(self, command: CreateUserCommand) -> FlextResult[User]:
        # Lógica focada - infraestrutura via decorators
        self.logger.info(f"Creating user: {command.name}")
        return FlextResult.ok(self._create(command))
```

**Benefício:** Separação de concerns - handler foca na lógica, decorators adicionam infraestrutura.

#### Como FlextContext Integra com CQRS

FlextContext.Performance é usado internamente por x.track():

```python
# x.track() internamente usa:
with FlextContext.Performance.timed_operation(operation_name) as metrics:
    # ...execução...
```

**Oportunidade:** h DEVERIA usar `self.track()` em vez de `_context_stack` manual.

#### Como FlextRegistry Integra com CQRS

FlextRegistry trabalha com FlextDispatcher para tracking de handlers:

```python
dispatcher = FlextDispatcher()
registry = FlextRegistry(dispatcher)

# Registrar múltiplos handlers com tracking
summary = registry.register_handlers([
    CreateUserHandler(),
    UpdateUserHandler(),
    DeleteUserHandler(),
])
print(f"Registered: {summary.successful_count}, Failed: {summary.failed_count}")
```

### Validação vs Código (25 Nov 2025)

> 📚 **Documento Relacionado:** [FLEXT_SERVICE_ARCHITECTURE.md](./FLEXT_SERVICE_ARCHITECTURE.md) - Plano de serviços (Tier 2.5)

**✅ h - PARCIALMENTE VALIDADO:**

- `handlers.py:31`: Herda `x[MessageT_contra, ResultT], ABC` ✅
- `handlers.py:85-116`: Métodos abstratos `handle()`, `validate()`, `pre_handle()`, `post_handle()` ✅
- `handlers.py:118-119`: `_context_stack` e `_metrics` manuais ❌ (deveria usar x)
- `handlers.py:426-471`: `push_context()`, `pop_context()`, `record_metric()` manuais ❌
- `handlers.py:495-584`: `_run_pipeline()` NÃO usa `self.logger` nem `self.track()` ❌

**⚠️ FlextDispatcher - PARCIALMENTE VALIDADO:**

- `dispatcher.py:45-80`: Construtor recebe managers hardcoded ❌ (deveria aceitar container)
- `dispatcher.py:85-120`: Registry interno implementado ✅
- `dispatcher.py:125-200`: Dispatch methods implementados ✅
- `dispatcher.py:300-450`: Reliability patterns (circuit breaker, retry) ✅

**🔴 Problemas Identificados:**

| Componente      | Problema                       | Impacto                   | Solução                  |
| --------------- | ------------------------------ | ------------------------- | ------------------------ |
| h               | 80+ linhas de métricas manuais | Duplicação com x          | x.CQRS                   |
| h               | \_context_stack manual         | Não usa self.context      | Integrar x               |
| FlextDispatcher | 700+ linhas managers hardcoded | Sem DI, sem testabilidade | FlextDI                  |
| FlextDispatcher | Todos managers internos        | Não reutilizável          | Extrair para \_managers/ |

### Plano de Execução Detalhado

#### Fase 0: Documentação ✅ COMPLETA

| Item                          | Status        | Arquivo                    | Descrição          |
| ----------------------------- | ------------- | -------------------------- | ------------------ |
| FLEXT_CQRS_ARCHITECTURE.md    | ✅ Criado     | docs/                      | Este documento     |
| FLEXT_SERVICE_ARCHITECTURE.md | ✅ Atualizado | docs/                      | Cross-ref com CQRS |
| Validação código vs docs      | ✅ Completo   | handlers.py, dispatcher.py | Line references    |

#### Fase 1: x.CQRS (Estimativa: 3-5 dias)

| Item                        | Status      | Arquivo             | Linhas | Descrição                          |
| --------------------------- | ----------- | ------------------- | ------ | ---------------------------------- |
| Criar x.CQRS                | 🔴 Pendente | mixins.py           | +80    | Nested class com métricas/contexto |
| cqrs_metrics property       | 🔴 Pendente | mixins.py           | +20    | Acessor para métricas CQRS         |
| cqrs_context property       | 🔴 Pendente | mixins.py           | +20    | Acessor para contexto CQRS         |
| Integrar self.logger        | 🔴 Pendente | handlers.py:495-584 | ~10    | Usar FlextLogger existente         |
| Integrar self.track()       | 🔴 Pendente | handlers.py:495-584 | ~10    | Usar tracking existente            |
| Deprecar record_metric()    | 🔴 Pendente | handlers.py:459-471 | +5     | DeprecationWarning                 |
| Deprecar push/pop_context() | 🔴 Pendente | handlers.py:426-448 | +5     | DeprecationWarning                 |
| test_mixins_cqrs.py         | 🔴 Pendente | tests/unit/         | +150   | 100% coverage                      |

**Código Target Fase 1:**

```python
# Em mixins.py
class x:
    class CQRS:
        """Mixin for CQRS handlers with metrics and context."""

        @property
        def cqrs_metrics(self) -> CQRSMetrics:
            """Access CQRS-specific metrics."""
            if not hasattr(self, "_cqrs_metrics"):
                self._cqrs_metrics = CQRSMetrics(self)
            return self._cqrs_metrics

        @property
        def cqrs_context(self) -> CQRSContext:
            """Access CQRS-specific context."""
            if not hasattr(self, "_cqrs_context"):
                self._cqrs_context = CQRSContext(self)
            return self._cqrs_context
```

#### Fase 2: FlextDispatcher DI (Estimativa: 5-7 dias)

| Item                           | Status      | Arquivo             | Linhas | Descrição              |
| ------------------------------ | ----------- | ------------------- | ------ | ---------------------- |
| CircuitBreakerProtocol         | 🔴 Pendente | protocols.py        | +30    | Interface manager      |
| RateLimiterProtocol            | 🔴 Pendente | protocols.py        | +25    | Interface manager      |
| RetryPolicyProtocol            | 🔴 Pendente | protocols.py        | +25    | Interface manager      |
| TimeoutEnforcerProtocol        | 🔴 Pendente | protocols.py        | +20    | Interface manager      |
| \_managers/circuit_breaker.py  | 🔴 Pendente | \_managers/         | +150   | Manager extraído       |
| \_managers/rate_limiter.py     | 🔴 Pendente | \_managers/         | +120   | Manager extraído       |
| \_managers/retry_policy.py     | 🔴 Pendente | \_managers/         | +100   | Manager extraído       |
| \_managers/timeout_enforcer.py | 🔴 Pendente | \_managers/         | +80    | Manager extraído       |
| FlextDispatcher(container=)    | 🔴 Pendente | dispatcher.py:45-80 | ~50    | Aceitar container      |
| Default manager registration   | 🔴 Pendente | dispatcher.py       | +30    | Auto-register defaults |
| test_dispatcher_di.py          | 🔴 Pendente | tests/unit/         | +200   | DI tests               |

**Código Target Fase 2:**

```python
# Em dispatcher.py
class FlextDispatcher:
    def __init__(
        self,
        container: FlextContainer | None = None,
        *,
        # V1 API mantida para backward compat (deprecated)
        circuit_breaker: CircuitBreaker | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self._container = container or FlextContainer.get_global()

        # V2: Obter managers do container
        if circuit_breaker is None:
            circuit_breaker = self._container.get("circuit_breaker").value_or(
                DefaultCircuitBreaker()
            )
        else:
            warnings.warn(
                "Passing circuit_breaker directly is deprecated. "
                "Use container.register('circuit_breaker', ...) instead.",
                DeprecationWarning,
                stacklevel=2,
            )
```

#### Fase 3: Migração Projetos Dependentes (Estimativa: 5-10 dias)

| Projeto       | Arquivos | Handlers | Status      | Prioridade |
| ------------- | -------- | -------- | ----------- | ---------- |
| flext-api     | ~8-10    | 5        | 🔴 Pendente | Alta       |
| flext-ldif    | ~5-8     | 3        | 🔴 Pendente | Alta       |
| flext-ldap    | ~6-10    | 4        | 🔴 Pendente | Média      |
| client-a-oud-mig | ~5-8     | 3        | 🔴 Pendente | Média      |
| flext-cli     | ~3-5     | 2        | 🔴 Pendente | Baixa      |

#### Fase 4: Remoção Legacy (Após 6+ meses)

| Item                              | Versão Removal | Dependências  |
| --------------------------------- | -------------- | ------------- |
| record_metric() manual            | V3.0           | 0 após Fase 3 |
| push/pop_context() manual         | V3.0           | 0 após Fase 3 |
| FlextDispatcher(circuit_breaker=) | V3.0           | 0 após Fase 3 |
| FlextDispatcher(rate_limiter=)    | V3.0           | 0 após Fase 3 |
| \_context_stack interno           | V3.0           | 0 após Fase 3 |
| \_metrics interno                 | V3.0           | 0 após Fase 3 |

### Métricas de Sucesso

| Métrica                | Antes | Target V2 | Target V3 |
| ---------------------- | ----- | --------- | --------- |
| Linhas h               | 604   | ~500      | ~400      |
| Linhas FlextDispatcher | 1200+ | ~900      | ~700      |
| % duplicação código    | 30%   | 15%       | 5%        |
| Coverage handlers.py   | 65%   | 85%       | 95%       |
| Coverage dispatcher.py | 60%   | 80%       | 90%       |

### Timeline Estimada

```
┌─────────────────────────────────────────────────────────────────┐
│  Nov 2025          │  Dez 2025       │  Jan-Jun 2026  │  V3.0  │
├─────────────────────────────────────────────────────────────────┤
│  Fase 0 ✅          │  Fase 1 🔴       │  Fase 2-3 🔴   │  Fase 4│
│  Documentação      │  x.CQRS│  DI + Migração │  Remove│
│  Validação código  │  Integração      │  Legacy        │  Legacy│
└─────────────────────────────────────────────────────────────────┘
```

---

## ~~📅 Histórico de Versões~~ 📋 METADADO

> _Histórico do documento original - para referência._

| Versão | Data        | Mudanças                                                      |
| ------ | ----------- | ------------------------------------------------------------- |
| 1.2    | 25 Nov 2025 | Análise profunda FlextDecorators, FlextContext, FlextRegistry |
| 1.1    | 25 Nov 2025 | Adicionado Plano de Execução detalhado com validação código   |
| 1.0    | 25 Nov 2025 | Documento inicial - V2 em desenvolvimento                     |

---

~~**Status:** 🚧 EM DESENVOLVIMENTO - Fase 0 ✅ Completa~~
~~**Próximo Update:** Início Fase 1 (x.CQRS implementation)~~

> **⚠️ DOCUMENTO EM PROCESSO DE MIGRAÇÃO**
> Conteúdo sendo progressivamente movido para `flext-core/docs/architecture/cqrs.md`
> Este documento será removido quando a migração estiver completa.
