# StateInitializationRequest (`FlextModels.Base.StateInitializationRequest`)

<!-- TOC START -->

- [Visão geral](#viso-geral)
- [Contrato detalhado](#contrato-detalhado)
- [Arquitetura e dependências](#arquitetura-e-dependncias)
  - [Locais candidatos imediatos](#locais-candidatos-imediatos)
- [Situação atual](#situao-atual)
- [Cenários de uso sugeridos](#cenrios-de-uso-sugeridos)
- [Pontos fortes x riscos](#pontos-fortes-x-riscos)
- [Backlog recomendado](#backlog-recomendado)
<!-- TOC END -->

## Visão geral

DTO pensado para padronizar a inicialização de estados compartilhados (cache em memória, storage em disco/redis, estruturas internas de serviços). Está definido em `flext_core/_models/base.py:197-211` e herda de `FlextModelsEntity.ArbitraryTypesModel`, herdando `extra="forbid"`, validação de atribuição e compatibilidade com `model_dump`.

## Contrato detalhado

| Campo               | Tipo          | Observações                                                                          |
| ------------------- | ------------- | ------------------------------------------------------------------------------------ |
| `data`              | `object`      | Payload bruto usado para construir o estado.                                         |
| `state_key`         | `str`         | Identificador lógico (ex.: `"user_cache"`).                                          |
| `initial_value`     | `object`      | Valor inicial a ser aplicado se não houver estado prévio.                            |
| `ttl_seconds`       | `int \| None` | Expiração opcional do estado.                                                        |
| `persistence_level` | `str`         | Default `FlextConstants.Cqrs.PersistenceLevel.MEMORY` (enum `memory`, `disk`, etc.). |
| `field_name`        | `str`         | Nome do atributo que receberá o estado (default: `"state"`).                         |
| `state`             | `object`      | Representa o estado efetivo após inicialização.                                      |

## Arquitetura e dependências

- `persistence_level` deriva das constantes CQRS (`flext_core/src/flext_core/constants.py`), garantindo alinhamento com o restante do runtime.
- O DTO deveria conversar com `FlextService` e `FlextContext` para inicializar estruturas antes de executar comandos/queries. Contudo, ainda não há integração direta.
- Idealmente, o modelo seria usado em `FlextService` dentro de um método `initialize_state` que configurasse `self.state` (ou campo custom) antes do processamento.

### Locais candidatos imediatos

- `flext_core/src/flext_core/service.py:200-420` já mantém atributos como `self.state` e `self.context`; inserir um hook `initialize_state(request)` reduziria duplicação nas subclasses de serviço.
- `flext_core/src/flext_core/context.py:900-1100` trata `state` dentro do contexto (ex.: `ContextState`), oferecendo um ponto natural para aplicar `StateInitializationRequest` antes de compartilhar dados com handlers.
- `flext-core/examples/14_flext_handlers_complete.py:298-760` mostra handlers que constroem estado manualmente; reescrever os exemplos com o DTO demonstraria o fluxo recomendado.

## Situação atual

- Assim como `Payload`, `Url` e `SerializationRequest`, não existem ocorrências em `src/` além da definição; `rg -n "StateInitializationRequest" --glob "*.py" --glob "!*tests*"` retorna apenas `_models/base.py` e `models.py`.
- O único uso concreto encontra-se nos testes `flext-core/tests/unit/test_models.py:954`, que exercitam o construtor e garantem que campos obrigatórios foram incluídos.

## Cenários de uso sugeridos

1. **Handlers Singer**: antes de processar lotes, inicializar caches (`state_key="recent_records"`) em memória ou disco com TTL controlado.
2. **LDIF pipelines**: preparar `state` com dados de `FlextContext` antes de enviar para `ldif_parser_service`, garantindo persistência `persistence_level="disk"` quando necessário.
3. **Services com FSM**: `FlextService` poderia usar o DTO para configurar máquina de estados (e.g., `field_name="fsm_state"`).

## Pontos fortes x riscos

- **Fortes**: contrato claro para inicializar estado; integra com enums oficiais de persistência; campos `ttl_seconds` e `field_name` eliminam strings mágicas dispersas.
- **Riscos**: ausência de validação (`state_key`, `field_name` aceitam qualquer string); `state`/`initial_value` são `object`, portanto sem tipagem/validação; falta de integração com caches reais (Redis, memcached) torna o DTO teórico.

## Backlog recomendado

1. **Integração com `FlextService`**: adicionar método `initialize_state(request: StateInitializationRequest)` chamando `setattr(self, request.field_name, request.initial_value)` e respeitando `persistence_level`/`ttl` (possivelmente conectando a `FlextContext` ou `u.Cache`).
2. **Validação de campos**: aplicar regex `^[a-zA-Z_][a-zA-Z0-9_]*$` para `state_key`/`field_name`, evitando nomes inválidos.
3. **Serializer complementar**: permitir anexar um `SerializationRequest` para estados que precisam ser persistidos fora da memória.
4. **Implantações externas**: documentar no README dos targets (Oracle, LDIF) que `StateInitializationRequest` deve ser usado ao provisionar dicionários que guardam progresso de sync.
