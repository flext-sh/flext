# Metadata (`FlextModels.Base.Metadata`)

## Visão geral

`Metadata` é a peça fundadora do namespace Base. O modelo vive em `flext_core/_models/metadata.py`, não importa outros módulos do flext-core e, por isso, pode ser importado por qualquer serviço, decorator ou plugin sem risco de ciclos. Toda a cadeia de Dispatcher → Registry → Handlers → Targets depende dele para transportar autoria, timestamps, tags e atributos auditáveis.

## Contrato detalhado

Herda diretamente de `pydantic.BaseModel` (`frozen=True`, `extra="forbid"`, validação de atribuição). O uso de `datetime.now(UTC)` preserva o princípio de zero dependências.

| Campo        | Tipo                | Padrão                | Observações |
| ------------ | ------------------- | --------------------- | ----------- |
| `created_by` | `str \| None`       | `None`                | Usuário/serviço que originou o recurso. |
| `created_at` | `datetime` (UTC)    | `datetime.now(UTC)`   | Sempre UTC, não depende de `FlextUtilities` para evitar ciclos. |
| `modified_by`| `str \| None`       | `None`                | Último agente que alterou o recurso. |
| `modified_at`| `datetime \| None`  | `None`                | Mantém `None` enquanto o objeto for imutável. |
| `tags`       | `list[str]`         | `[]`                  | Coleção imutável (modelo congelado). |
| `attributes` | `dict[str, object]` | `{}`                  | Dicionário serializável usado como lingua franca entre módulos. |

## Arquitetura e dependências

- **Context namespace**: `FlextModelsContext.ContextData` aceita `Metadata` diretamente, converte para dict e valida serialização (`flext_core/src/flext_core/_models/context.py:299-315`).
- **Dispatcher**: `_extract_dispatch_configuration` trata `Metadata` como primeira classe e expõe `attributes` para validação (`flext_core/src/flext_core/dispatcher.py:2753-2775`).
- **Registry/Container**: `FlextRegistry.register` e `FlextContainer._store_service` persistem `Metadata` junto às entradas de DI (`flext_core/src/flext_core/registry.py:930-964`, `flext_core/src/flext_core/container.py:353-374`).
- **Handlers**: quando há falha de validação, `FlextHandlers` anexa um `Metadata` rico à exceção para rastreabilidade (`flext_core/src/flext_core/handlers.py:319-333`).
- **Decorators/Services**: `FlextDecorators.railway` cria `Metadata` para registrar steps (`flext_core/src/flext_core/decorators.py:1134-1165`), enquanto `FlextService` injeta `Metadata` em `OperationExecutionRequest` e contextos.

## Uso em projetos satélite

- **flext-ldif**: `FlextLdifApi._register_components` registra serviços com `Metadata` categorizando domínio e tipo (`flext-ldif/src/flext_ldif/api.py:420-449`). `flext-ldif/_utilities/metadata.py` converte dicts genéricos vindos de LDIF em `Metadata` polido antes de reenviar ao dispatcher (`linhas 137 e 220`).
- **flext-target-oracle**: `OracleTargetCommandHandler` injeta `Metadata` ao registrar handlers Singer (`flext-target-oracle/src/flext_target_oracle/target_commands.py:259-270`).
- **Outros targets/taps**: projetos `flext-target-oracle-oic`, `flext-target-oracle-wms` e `flext-tap-*` seguem o padrão `Metadata(attributes={...})` para registrar configurações em contêineres DI (consultar `rg -n "Metadata" flext-target-oracle-wms/src`).

## Relação com outros modelos

- **FlextModels.Base.Payload**: o campo `metadata` do payload usa apenas tipos primitivos; futuras migrações devem aceitar `Metadata` completo para manter consistência com dispatcher/registry.
- **FlextModels.Collections.Config**: muitos configs carregam `metadata: Metadata` para contextualizar validações (ex.: `HandlerExecutionConfig`).
- **FlextContext.Export**: snapshots de contexto exportam `metadata: Metadata`, garantindo que atributos e tags sejam preservados em logs ou transportes.

## Exemplos conectados ao runtime

`flext_core/src/flext_core/dispatcher.py:2753`

```python
if metadata is None:
    validated_metadata = {}
elif FlextRuntime.is_dict_like(metadata):
    validated_metadata = dict(metadata)
elif isinstance(metadata, FlextModels.Metadata):
    validated_metadata = metadata.attributes
else:
    return FlextResult[dict[str, object]].fail(...)
```

`flext_core/src/flext_core/container.py:353`

```python
service_registration = FlextModels.ServiceRegistration(
    name=name,
    service=service,
    service_type=type(service).__name__,
    tags=[],
    metadata=FlextModels.Metadata(attributes={}),
)
```

`flext-ldif/src/flext_ldif/api.py:420`

```python
self._registry.register(
    "ldif_parser_service",
    self._parser_service,
    metadata=FlextModels.Metadata(
        attributes={"type": "service", "domain": "parser", "description": "Unified LDIF parsing"},
    ),
)
```

## Pontos fortes x riscos

- **Fortes**: única fonte de verdade; sem dependências; aceita conversão bidirecional (dict ↔ Metadata) em múltiplas camadas; já adotado por dispatcher, registry, LDIF, targets e decorators.
- **Riscos**: `attributes` é amorfo, obrigando consumidores a revalidarem manualmente; `tags` não tem taxonomia oficial; timestamps dependem de `datetime.now(UTC)` — servidores sem clock sincronizado podem gerar divergências; não há versão especializada para operações críticas (ex.: compliance, segurança).

## Próximos passos e recomendações

1. **Padronizar atributos**: publicar um schema sugerido (ex.: `{"domain": ..., "owner": ..., "type": ...}`) e disponibilizar validadores em `FlextUtilities.Validation`.
2. **Factories oficiais**: expor helpers (`Metadata.for_service`, `Metadata.for_handler`, `Metadata.audit`) preenchedo tags/atributos padrão e reduzindo divergências entre projetos.
3. **Integração com observability**: mover geração de timestamps para `FlextUtilities.Generators` e propagar `correlation_id` automaticamente nos atributos.
4. **Migração gradual**: exigir `Metadata` em novos registries/handlers (`flext-target-*`) para substituir dicionários soltos, garantindo que TOTVS, Oracle OIC e LDIF usem o mesmo contrato.
