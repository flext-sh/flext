# FlextModels · Entidades e Objetos de Valor

<!-- TOC START -->

- [Componentes](#componentes)
  - [`Entity`](#entity)
  - [`Value`](#value)
  - [`AggregateRoot`](#aggregateroot)
  - [`DomainEvent`](#domainevent)
  - [`ArbitraryTypesModel`](#arbitrarytypesmodel)
  - [`FrozenStrictModel`](#frozenstrictmodel)
  - [`IdentifiableMixin`](#identifiablemixin)
  - [`TimestampableMixin`](#timestampablemixin)
  - [`TimestampedModel`](#timestampedmodel)
  - [`VersionableMixin`](#versionablemixin)
  <!-- TOC END -->

Camada central de DDD que expõe entidades, objetos de valor, agregados e eventos com validação Pydantic. Dados levantados via AST (`flext_core/models.py`) e uso confirmado com busca estática (testes ignorados).

Para cada componente detalhamos motivação, funcionamento, usos recomendados, adoções atuais, benefícios e decisões sugeridas.

## Componentes

### `Entity`

**Motivação**

- Fornecer base única para entidades com identidade, timestamps e validação Pydantic, substituindo `BaseModel` genérico nas dezenas de projetos.

**Funcionamento**

- Herda `FlextModelsEntity.Entry` (que já incorpora mixins de ID, timestamps, validação) e habilita `FlextResult` como tipo de retorno padrão. Inclui métodos auxiliares para lifecycle (`is_valid`, `to_dict`).

**Usos recomendados**

- Toda entidade com identidade e lógica de domínio deve herdar daqui (ex.: `User`, `Plugin`, `Entry`).

**Adoções atuais**

- 32 arquivos em 22 projetos (lista completa ao lado), sendo o modelo mais difundido do ecossistema.

**Benefícios / decisões**

- Centraliza validação, logging, timestamps e integração com `FlextResult`. Manter como padrão oficial e migrar eventuais `BaseModel` legados.

### `Value`

**Motivação**

- Definir objetos de valor imutáveis e hasháveis, com igualdade baseada em atributos. Útil para emails, IDs compostos, snapshots.

**Funcionamento**

- Base `FlextModelsEntity.Value` (frozen Pydantic). Internamente aplica validação de campos e `model_copy(update=...)` para “alterações” seguras.

**Usos recomendados**

- Qualquer tipo comparado por valor (ex.: Email, Status, ConfigKey). Situações que exigem hashing (dicionários, sets).

**Adoções atuais**

- 20 arquivos em 9 projetos (flext-oud-mig, flext-api, flext-core, flext-ldif, flext-observability, flext-oracle-oic, flext-plugin, flext-meltano-native, scripts).

**Benefícios / decisões**

- Reduz bugs causados por mutações acidentais e padroniza serialização. Continuar incentivando uso quando o valor representar invariantes importantes.

### `AggregateRoot`

**Motivação**

- Implementa boundary de consistência agregando entidades/valores sob invariantes transacionais. Ideal para domínios complexos (ex.: PluginRegistry, OrderAggregate).

**Funcionamento**

- Herda `AggregateRoot` + `Entity`, adicionando suporte a eventos, invariantes e métodos de orquestração.

**Adoções atuais**

- `flext-core/examples/03_models_basics.py`, `flext-oracle-wms/src/flext_oracle_wms/models.py`, `flext-plugin/src/flext_plugin/entities.py`.

**Decisões**

- Expandir para domínios que já tratam consistência (LDIF pipelines, targets) em vez de reimplementar padrões manualmente.

### `DomainEvent`

**Motivação**

- Estrutura eventos imutáveis para event sourcing e auditoria.

**Funcionamento**

- Value object com `message_type="event"`, timestamps e mixins para compatibilidade com `MessageUnion`.

**Adoções atuais**

- `flext-ldif/_models/events.py`, `flext-plugin/src/flext_plugin/entities.py`.

**Decisões**

- Incentivar times que implementam histórico/auditoria a herdar deste modelo e não criar `BaseModel` custom.

### `ArbitraryTypesModel`

**Motivação**

- Base flexível para modelos que precisam aceitar tipos arbitrários (objeto, callable) sem abrir mão de validação/serialização personalizada.

**Funcionamento**

- Constrói `BaseModel` com `arbitrary_types_allowed=True`, validação estrita e integrações com `FlextResult`. Serve como “base genérica” usada em diversos submodelos (payloads, configs, etc.).

**Adoções atuais**

- 16 arquivos em 11 projetos (flext-cli, flext-core/service, flext-dbt-\*, flext-ldif, flext-meltano, targets, etc.).

**Decisões**

- Praticamente todo novo DTO deve herdar daqui em vez de criar `BaseModel` manual. Mantê-lo como peça fundamental da arquitetura.

### `FrozenStrictModel`

**Motivação**

- Fornecer modelo estrito e imutável para casos em que o mixin `Value` não é suficiente (ex.: objetos com validações especiais mas sem semantics de `Value`).

**Uso atual**

- Ainda não referenciado fora do módulo base.

**Decisão**

- Identificar casos onde precisamos de imutabilidade + validação estrita, caso contrário documentar como experimental.

### `IdentifiableMixin`

**Motivação**

- Mix-in para adicionar `unique_id` com geração automática e validações. Permite que modelos custom (não-entidades completas) ganhem ID sem herdar `Entity`.

**Funcionamento**

- `BaseModel` com `unique_id` e `ConfigDict` estrito; pensado para complementar classes custom.

**Uso atual**

- Sem referências externas (apenas via herança em `Entity` e outros modelos).

**Decisão**

- Deixar disponível para composições avançadas; comunicar aos times que precisam de IDs em DTOs (ex.: requests).

### `TimestampableMixin`

**Motivação**

- Adiciona campos `created_at`/`updated_at` com serialização ISO e helper `update_timestamp` para qualquer modelo que precise de histórico de alterações.

**Uso atual**

- Não usado diretamente (pois `Entity` já incorpora). Ainda assim útil para DTOs custom.

**Decisão**

- Documentar e incentivar uso em modelos que precisam apenas de timestamps sem o custo completo de `Entity`.

### `TimestampedModel`

**Motivação**

- Modelo pré-feito com timestamps para cenários em que o mixin não é suficiente ou queremos um objeto autônomo.

**Adoções atuais**

- `flext-meltano/src/flext_meltano/models.py` (uso direto).

**Decisão**

- Manter disponível para times que preferem compor em vez de herdar mixins manualmente.

### `VersionableMixin`

**Motivação**

- Fornecer versionamento otimista (`version` com limites) a qualquer modelo, permitindo controle de concorrência.

**Uso atual**

- Sem referências fora do módulo base.

**Decisão**

- Recomendar para entidades que fazem upsert em bancos e precisam validar versões. Caso siga sem uso, considerar remover ou mover para RFC.
