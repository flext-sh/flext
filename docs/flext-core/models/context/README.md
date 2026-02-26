# FlextModels · Contexto e Observabilidade

<!-- TOC START -->

- [Componentes](#componentes)
  - [`StructlogProxyToken`](#structlogproxytoken)
  - [`StructlogProxyContextVar`](#structlogproxycontextvar)
  - [`Token`](#token)
  - [`ContextData`](#contextdata)
  - [`ContextExport`](#contextexport)
  - [`ContextScopeData`](#contextscopedata)
  - [`ContextStatistics`](#contextstatistics)
  - [`ContextMetadata`](#contextmetadata)
  - [`ContextDomainData`](#contextdomaindata)
  <!-- TOC END -->

Modelos responsáveis por propagar dados de contexto, tokens e estatísticas de execução. Todos foram extraídos de `flext_core/models.py` via AST e tiveram seu uso real verificado com busca estática (testes ignorados).

Cada componente abaixo traz motivação, funcionamento interno, aplicações recomendadas no negócio, adoções atuais, benefícios e decisões sugeridas (adotar, mover para experimento ou arquivar).

## Componentes

### `StructlogProxyToken`

**Por que existe / qual problema resolve**

- Permite restaurar o estado de variáveis de contexto gerenciadas pelo structlog quando `StructlogProxyContextVar` altera valores. Sem esse token seria impossível desfazer alterações de forma segura (ex.: ao sair de um escopo).

**Como funciona**

- Value object imutável (`FlextModelsEntity.Value`) com campos `key` (validação por regex) e `previous_value`. Usado como retorno de `StructlogProxyContextVar.set` e argumento de `reset`.

**Aplicações esperadas**

- Qualquer camada que precise empilhar/destacar contextos, principalmente `flext_core/context.py` quando aplica `with FlextContext.operation_scope()`.

**Adoções atuais**

- Ainda não referenciado diretamente fora do módulo base, embora `StructlogProxyContextVar` (que o cria) seja usado intensamente pelo `FlextContext`.

**Benefícios / decisões**

- Garante reentrância segura e evita vazamento de contexto entre threads. Recomenda-se documentar explicitamente seu uso em `FlextContext` para que squads não reimplementem tokens manuais.

### `StructlogProxyContextVar`

**Por que existe / qual problema resolve**

- Centraliza o armazenamento de variáveis de contexto no structlog, garantindo fonte única de verdade entre `FlextContext` e `FlextLogger`. Elimina divergência entre `contextvars` e loggers.

**Como funciona**

- Classe genérica que delega `get/set/reset` para `structlog.contextvars`. O método `set` retorna `StructlogProxyToken` para possibilitar rollback. Mantém `_default` e faz cast seguro no `get`.

**Aplicações esperadas**

- Utilizada diretamente em `flext-core/src/flext_core/context.py` (helpers `_StructlogProxyStr`, `_StructlogProxyDatetime`, `_StructlogProxyDict`) para armazenar correlação, timestamps e dicionários de metadados.

**Adoções atuais**

- Ativamente usada em `flext_core/context.py` para todas as operações de contexto.

**Benefícios / decisões**

- Garante que toda alteração de contexto apareça automaticamente nos logs. Manter como padrão oficial e desencorajar o uso direto de `contextvars.ContextVar`.

### `Token`

**Por que existe / qual problema resolve**

- Complementa `StructlogProxyContextVar` para contextos genéricos que não usam structlog (ex.: dicionários locais). Armazena `key` e `old_value` para restaurar valores ao sair de escopos.

**Como funciona**

- Value object com validação de chave (`Field(min_length=1)`) e `old_value`. Consumido por utilitários de contexto quando não estamos usando structlog diretamente.

**Aplicações esperadas**

- Scopes locais dentro de `FlextContext` que manipulam dicionários em memória.

**Adoções atuais**

- Ainda não há referência direta fora do módulo base.

**Benefícios / decisões**

- Ajuda a padronizar tokens mesmo em contextos que não usam structlog. Recomenda-se ligá-lo aos helpers de `FlextContext` para que deixe de ser “APIs sem uso”.

### `ContextData`

**Por que existe / qual problema resolve**

- Fornece envelope imutável para inicializar `FlextContext` com dados e metadados validados/serializáveis. Evita que inicializações aceitem estruturas inválidas ou não serializáveis.

**Como funciona**

- Value object com campos `data` e `metadata` (aceita `Metadata`, dict ou outro BaseModel). Validadores `validate_dict_serializable`/`validate_metadata` garantem JSON-serializabilidade e convertem Pydantic models em dict automaticamente.

**Aplicações esperadas**

- Construtor de `FlextContext` (`flext_core/context.py:174`) aceita `ContextData` ou dict. Permite importar snapshots de contextos remotos com validação.

**Adoções atuais**

- Usado diretamente em `flext_core/context.py` e seus testes de cobertura.

**Benefícios / decisões**

- Garante que qualquer contexto inicial compartilhado entre serviços siga padrões de serialização, simplificando auditoria e exportação. Manter como formato oficial para inicialização.

### `ContextExport`

**Por que existe / qual problema resolve**

- Representa snapshot completo do contexto (dados + metadados + estatísticas) pronto para persistência ou transmissão. Sem esse DTO cada exportação retornaria dicts inconsistentes.

**Como funciona**

- Value object com validação rigorosa (`check_json_serializable`) para `data` e `statistics`. `metadata` é normalizada para `FlextModels.Metadata`. Inclui validadores para aceitar Pydantic models e convertê-los automaticamente.

**Aplicações esperadas**

- Método `export_snapshot` do `FlextContext` (`flext_core/context.py:1066`) devolve essa estrutura para logs, auditoria ou replicação de contexto para outros processos.

**Adoções atuais**

- Utilizado no próprio `flext_core/context.py` e em todos os testes associados.

**Benefícios / decisões**

- Padroniza exportações, garante serialização JSON e evita que informações sensíveis sejam perdidas. Continuar exigindo esse formato para qualquer API que precise clonar contexto.

### `ContextScopeData`

**Por que existe / qual problema resolve**

- Normaliza o armazenamento de dados por escopo (`request`, `operation`, etc.), permitindo descrever tipo, dados e metadados de cada camada sem recorrer a dicionários dispersos.

**Como funciona**

- `BaseModel` com campos `scope_name`, `scope_type`, `data` e `metadata`. Validadores aceitam dict ou BaseModel e convertem via `model_dump`, garantindo consistência.

**Aplicações esperadas**

- Serialização de escopos em `FlextContext` (ex.: exportar apenas o escopo de operação) ou ferramentas que desejam mostrar estado por camada.

**Adoções atuais**

- Ainda não é referenciado fora do módulo base.

**Benefícios / decisões**

- Oficia o formato de scopes e abre espaço para dashboards. Recomenda-se integrá-lo à API pública de `FlextContext` (listar scopes) para evitar que continue sem uso.

### `ContextStatistics`

**Por que existe / qual problema resolve**

- Substitui dicts genéricos para métricas do contexto (quantidade de `set`, `get`, etc.). Ajuda a monitorar desempenho e detectar gargalos.

**Como funciona**

- `BaseModel` com counters (`sets`, `gets`, `removes`, `clears`) e dicionário `operations`. Validadores aceitam dict/BaseModel e convertem automaticamente.

**Aplicações esperadas**

- `flext_core/context.py` popula estatísticas antes de exportar snapshots, além de permitir que observabilidade monitore operações.

**Adoções atuais**

- Usado dentro de `flext_core/context.py`.

**Benefícios / decisões**

- Facilita criação de métricas e alertas sobre uso de contexto. Manter e incentivar squads a preencher `operations` com dados relevantes (latências, itens processados).

### `ContextMetadata`

**Por que existe / qual problema resolve**

- Modelo tipado para metadados de contexto (IDs, tenant, handler mode, message info). Sem ele, cada módulo define dicionários com chaves diferentes, dificultando correlação.

**Como funciona**

- `BaseModel` com campos opcionais (`user_id`, `correlation_id`, `tenant_id`, `message_type`, etc.) e `custom_fields`. Validator converte BaseModels em dict e garante que `custom_fields` sempre seja dicionário.

**Aplicações esperadas**

- `flext_core/context.py` utiliza ao criar/atualizar metadados e exportar contextos. Pode ser usado também por handlers/dispatchers ao anexar informações aos logs.

**Adoções atuais**

- Referenciado em `flext_core/context.py`.

**Benefícios / decisões**

- Garante consistência para campos críticos (correlation_id, tenant) e viabiliza traceabilidade multi-tenant. Sugere-se adotá-lo em toda funcionalidade que manipula metadados (ex.: decorator `@log_operation`).

### `ContextDomainData`

**Por que existe / qual problema resolve**

- Contêiner tipado para dados específicos de domínio (nome, tipo, payload, metadados). Evita espalhar dicionários `domain_*` sem contrato e melhora a clareza quando múltiplos domínios compartilham o mesmo contexto.

**Como funciona**

- `BaseModel` com campos `domain_name`, `domain_type`, `domain_data`, `domain_metadata`, todos opcionais exceto os dicionários (que têm `default_factory`).

**Aplicações esperadas**

- Camadas que inserem informações próprias (ex.: domínios LDAP vs. LDIF) dentro do contexto e gostariam de documentar o conteúdo para exportação.

**Adoções atuais**

- Ainda não utilizado fora do módulo base.

**Benefícios / decisões**

- Fornece padrão para squads adicionarem dados específicos sem improvisar. Recomendável expor helpers no `FlextContext` para popular/ler `ContextDomainData`; caso contrário, considere arquivá-lo como experimental para reduzir backlog.
