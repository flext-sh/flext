# SerializationRequest (`FlextModels.Base.SerializationRequest`)

## Visão geral
DTO para encapsular políticas de serialização (formato, encoding, compressão, ordenação, uso de `model_dump`). A implementação vive em `flext_core/_models/base.py:166-194` e deveria substituir as tuplas/dicionários ad-hoc usados hoje em handlers, serviços e targets Singer.

## Contrato detalhado
| Campo          | Tipo                  | Padrão / Observações |
| -------------- | --------------------- | -------------------- |
| `data`         | `object`              | Objeto a ser serializado (entities, payloads, dicts, etc.). |
| `format`       | `str`                 | Default `FlextConstants.Cqrs.SerializationFormat.JSON`. |
| `encoding`     | `str`                 | `"utf-8"`. |
| `compression`  | `str \| None`        | Algoritmo opcional (`gzip`, `zstd`, etc.). |
| `pretty_print` | `bool`                | `False` (podendo habilitar identação). |
| `use_model_dump` | `bool`              | `True` – chama `model_dump()` antes de serializar quando presente. |
| `indent`       | `int \| None`        | Espacos para formatação humana. |
| `sort_keys`    | `bool`                | Ordena chaves de dicts para determinismo. |
| `ensure_ascii` | `bool`                | Replica parâmetro do `json.dumps`. |

## Arquitetura e dependências
- Acompanha o mesmo núcleo de `FlextConstants.Cqrs.SerializationFormat`, garantindo que as opções batam com o que os handlers suportam.
- Complementa `FlextRuntime.is_dict_like` e `FlextHandlers._try_common_serialization_methods` (`flext_core/src/flext_core/handlers.py:439-520`), oferecendo metadados para o pipeline decidir como serializar.
- Se integra naturalmente com `FlextContext.Serialization` (`flext_core/src/flext_core/context.py:1666-1810`), que hoje expõe apenas funções globais.

## Situação atual
- `rg -n "SerializationRequest" --glob "*.py" --glob "!*tests*"` retorna somente as definições nas camadas `_models`/`models`. Ainda não há instâncias em `src/`.
- Isso significa que os métodos `_serialize_message` e `_serialize_result` recebem inputs heterogêneos (`dict`, `BaseModel`, `attrs`) sem informação explícita sobre formato desejado.

## Fluxo pretendido
1. `FlextHandlers` recebe `SerializationRequest` contendo `data` e preferências (ex.: `format="json"`, `pretty_print=False`).
2. `_serialize_message` usa `request.use_model_dump` para escolher entre `model_dump`, `dict` ou `vars`, e depois aplica `FlextRuntime`/`json`/`orjson` de acordo com `request.format`.
3. Projetos Singer (targets/taps) constroem instâncias com `format="ldif"` ou `"jsonl"`, garantindo que `compression` e `encoding` estejam documentados.

## Exemplo (integração com handlers)
```python
request = FlextModels.SerializationRequest(
    data=command,
    format=FlextConstants.Cqrs.SerializationFormat.JSON,
    encoding="utf-8",
    sort_keys=True,
)
serialized = FlextHandlers.Serialization.serialize_message(request)
```
> `serialize_message` representa `_serialize_message` + `_try_common_serialization_methods` em `flext_core/src/flext_core/handlers.py:439-520`, que hoje não recebe nenhum DTO.

## Pontos fortes x limitações
- **Fortes**: centraliza políticas de serialização, reduz duplicação de opções (`pretty_print`, `indent`), torna comportamento previsível e auditável.
- **Limitações**: ausência de adoção; campos `format`/`compression` aceitam qualquer `str`; não há integração com `FlextUtilities.Serialization` (ex.: compressão real); não expõe métodos auxiliares (`to_json_kwargs`) que facilitem uso.

## Backlog recomendado
1. **Adotar no core**: alterar `flext_core/src/flext_core/handlers.py` para receber `SerializationRequest` (tanto em `_serialize_message` quanto `_serialize_result`).
2. **Builders específicos**: liberar `SerializationRequest.json(data, *, indent=None, sort_keys=False)` e `SerializationRequest.ldif(...)` para alinhar com formatos suportados por `FlextConstants`.
3. **Enums e validação**: converter `format` e `compression` em `Literal`/`Enum` usando `FlextConstants`, prevenindo valores inválidos.
4. **Integração com projetos**: documentar no README dos targets (`flext-target-oracle`, `flext-target-ldif`) que `SerializationRequest` substitui dicionários de opções antes de escrever arquivos/streams.
