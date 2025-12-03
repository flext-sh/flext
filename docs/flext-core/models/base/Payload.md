# Payload (`FlextModels.Base.Payload[T]`)

## Visão geral

Envelope fortemente tipado destinado a carregar entidades/comandos/respostas dentro do `FlextModels`. O modelo une validação dinâmica, rastreamento temporal e identificação automática para garantir que mensagens trafeguem pelo dispatcher e pelos handlers com contexto completo. A implementação encontra-se em `flext_core/_models/base.py` e é exposta como `FlextModels.Payload` em `flext_core/models.py`.

## Contrato detalhado

- Herda de `FlextModelsEntity.ArbitraryTypesModel`, `IdentifiableMixin` e `TimestampableMixin`; portanto, todos os payloads possuem `unique_id`, `created_at`, `updated_at` e validação estrita (`extra="forbid"`).
- `__class_getitem__`: cria subtipos dinamicamente (ex.: `Payload[User]`). Utiliza `u.Generators.create_dynamic_type_subclass` para definir `_expected_data_type` e preservar `__qualname__`.
- `model_validator(mode="after")`: garante que `data` corresponda ao tipo esperado. Usa `isinstance` ou `beartype.door.is_bearable` para suportar `typing.Protocol`/`TypedDict`.
- `computed_field is_expired`: compara `expires_at` com `u.Generators.generate_datetime_utc()`.

| Campo                 | Tipo                               | Observações                                                                       |
| --------------------- | ---------------------------------- | --------------------------------------------------------------------------------- |
| `_expected_data_type` | `type \| tuple[type, ...] \| None` | ClassVar preenchido automaticamente por `__class_getitem__`.                      |
| `data`                | `T`                                | Carga principal (command/event/entity).                                           |
| `metadata`            | `dict[str, str \| int \| float]`   | Cabeçalhos simples (correlação, tags) — ainda não utiliza `FlextModels.Metadata`. |
| `expires_at`          | `datetime \| None`                 | Suporte a TTL/expiração.                                                          |
| `correlation_id`      | `str \| None`                      | Deve acompanhar `FlextContext`.                                                   |
| `source_service`      | `str \| None`                      | Identifica produtor (tap, target, handler).                                       |
| `message_type`        | `str \| None`                      | Discriminador livre (command/query/event).                                        |

## Arquitetura e dependências

- Depende de `u.Generators` para timestamps e criação dinâmica, e de `beartype` para validação flexível.
- Compartilha mixins com `FlextModels.Entity`, permitindo que payloads e entidades passem pelos mesmos serializadores (`model_dump`).
- Foi desenhado para alimentar `FlextDispatcher` e `h`, substituindo dicionários “soltos” que hoje circulam pelos pipelines.

## Estado atual de adoção

- Não há ocorrências do modelo em `src/` (fora da definição). O comando `rg -n "FlextModels\.Payload" --glob "*.py" --glob "!*tests*"` retorna somente a declaração do namespace.
- Os únicos consumidores são os testes dedicados `flext-core/tests/unit/test_payload_runtime_validation.py`, que validam `__class_getitem__`, mensagens de erro e TTL.

## Integração pretendida com outros modelos

- **Dispatcher**: `flext_core/src/flext_core/dispatcher.py` manipula hoje `dict[str, object]`. O campo `metadata` + `correlation_id` do payload foi desenhado para alimentar `_extract_dispatch_configuration` diretamente, evitando conversões.
- **Handlers (CQRS)**: `h.handle` poderia exigir `Payload[FlextModels.Command]`, garantindo que todo handler receba envelope com `source_service` e `message_type` preenchidos.
- **Metadata**: existe esforço planejado para trocar `dict[str, str|int|float]` por `FlextModels.Metadata`, reforçando a ligação com registry/observability.

### Interações concretas no flext-core

- `flext_core/src/flext_core/models.py:333-365` expõe `Payload` como parte do namespace `FlextModels` e chama `model_rebuild` na sequência (`linhas 530-533`) para compatibilidade com Pydantic v2.
- `flext_core/src/flext_core/_models/base.py:46-145` mostra a implementação completa, incluindo `create_dynamic_type_subclass`, `model_validator` e `computed_field` — qualquer mudança nesses utilitários impacta diretamente `Payload`.
- `flext_core/src/flext_core/handlers.py:439-520` espera hoje objetos serializáveis (`dict`, `BaseModel`, `attrs`). `Payload` foi desenhado para encaixar nesse pipeline (via `model_dump`), entregando informações extras (`source_service`, `expires_at`).
- `flext_core/src/flext_core/context.py:430-520` manipula `FlextContext.ContextData` com `Metadata`; integrar `Payload.metadata` à mesma estrutura simplificaria a conversão de contexto → payload.

### Motivação detalhada

- **Traces completos**: `correlation_id`, `source_service` e `message_type` permitem reconstruir o caminho de uma mensagem, algo essencial para targets Singer e pipelines LDIF.
- **Compatibilidade com mixins**: por herdar `IdentifiableMixin` e `TimestampableMixin`, todo payload ganha `unique_id`, `created_at`, `updated_at`, atributos usados por `LogOperation` e `Metadata`.
- **Segurança em runtime**: `__class_getitem__` evita que um handler receba `Payload[User]` contendo `Product` — proteção útil em ambientes com plugins carregados dinamicamente onde MyPy não alcança.

### Exemplo adicional (trecho do módulo base)

`flext_core/src/flext_core/_models/base.py:64-112`

```python
typed_cls = u.Generators.create_dynamic_type_subclass(
    f"{cls_name}[{type_name}]",
    cls,
    {
        "_expected_data_type": actual_type,
        "__module__": cls.__module__,
        "__qualname__": f"{cls_qualname}[{type_name}]",
    },
)
```

Esse trecho reforça como o namespace Base depende de `u` para gerar tipos auxiliares preservando metadados (módulo, qualname), requisito importante para inspeção em logs/dashboards.

### Roteiro de adoção multi-projeto

1. **Dispatcher** – aceitar `Payload` diretamente, extraindo `metadata` e `correlation_id` antes de despachar para handlers.
2. **h** – atualizar assinaturas para `def handle(self, message: FlextModels.Payload[TMsg])` e expor adaptadores para quem ainda envia dicts.
3. **Targets/Taps** – encapsular comandos Singer (`flext-target-oracle`, `flext-target-ldif`) com `Payload`, garantindo que `source_service` e `message_type` viajem juntos.
4. **Observability** – usar `Payload.unique_id` como chave para correlacionar `LogOperation`, `Metadata` e métricas em `flext-observability`.

## Cenários concretos

- **Comandos Singer**: `flext-target-oracle/target_commands.py` cria handlers CQRS com metadados ricos; substituir `command` por `FlextModels.Payload[OracleTargetCommand]` eliminaria a duplicação de `correlation_id`/`source_service`.
- **LDIF pipelines**: APIs `flext-ldif` exportam objetos `ContextExport`. Ao envolvê-los em `Payload[ContextExport]`, ficaria mais fácil anexar TTL e `message_type="ldif_context"` para downstream consumers.

## Pontos fortes x riscos

- **Fortes**: validação real em runtime, prevenção de envelope inválido, instrumentação automática (timestamps, unique_id), pronto para tracing e TTL.
- **Riscos**: ausência total de adoção; metadata limitada a primitivos; geração ilimitada de subtipos pode pressionar o interpretador se não houver cache; sem integração com `FlextContext`, o campo `correlation_id` permanece manual.

## Backlog sugerido

1. **Adotar no Dispatcher**: alterar `FlextDispatcher` para aceitar `Payload[T]` como primeiro parâmetro e extrair `metadata/correlation_id` diretamente.
2. **Integrar com Handlers**: atualizar `h.handle` para aceitar `Payload[Command]` e fornecer adaptadores para projetos Singer (`flext-target-*`).
3. **Metadata rica**: substituir o campo `metadata` por `FlextModels.Metadata` (ou aceitar ambos) para padronizar atributos.
4. **Cache de subtipos**: adicionar cache em `u.Generators.create_dynamic_type_subclass` evitando re-criação de `Payload[MyEntity]` em cada chamada.
5. **Documentar fluxos**: criar exemplos reais (ex.: `flext-core/examples/handlers`) mostrando `Payload[UserCreatedEvent]` trafegando pelo bus e conectando com `FlextModels.Metadata`.
