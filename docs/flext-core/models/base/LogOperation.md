# LogOperation (`FlextModels.Base.LogOperation`)

## Visão geral

Modelo pensado para capturar logs estruturados de operações, preservando contexto (nível, mensagem, dados complementares, origem e objeto associado). Implementado em `flext_core/_models/base.py`, ele herda de `FlextModelsEntity.ArbitraryTypesModel` e, portanto, usufrui de validação estrita e serialização consistente.

## Contrato

| Campo       | Tipo                | Detalhes |
| ----------- | ------------------- | -------- |
| `level`     | `str`               | Default `"INFO"` via lambda; aceita qualquer string atualmente. |
| `message`   | `str`               | Texto principal (obrigatório). |
| `context`   | `dict[str, object]` | Metadados adicionais (ex.: ids, métricas). |
| `timestamp` | `datetime`          | `FlextUtilities.Generators.generate_datetime_utc`, garantindo UTC. |
| `source`    | `str \| None`      | Subsistema/projeto emissor. |
| `operation` | `str \| None`      | Nome lógico (padrão: decorator `log_operation`). |
| `obj`       | `object \| None`   | Referência opcional ao objeto alvo (handler, service, etc.). |

## Arquitetura e dependências

- **Decorators**: `FlextDecorators.log_operation` (em `flext_core/src/flext_core/decorators.py:365-476`) é o principal candidato a produzir `LogOperation`. Hoje ele escreve direto no `FlextLogger`, mas os parâmetros recebidos são equivalentes aos campos do modelo.
- **Services**: `FlextService` delega logging ao mixin. Ao adotar `LogOperation`, seria possível propagar `obj` e `context` uniformemente em `execute_operation`, `execute_conditionally` e `execute_async`.
- **Observability**: `flext-observability` e `flext-quality` coletam métricas a partir de logs. Representar cada evento como `LogOperation` facilitaria conversão para `structlog` e pipelines (Elastic, New Relic).

## Situação atual

- `rg -n "FlextModels\.LogOperation" --glob "*.py" --glob "!*tests*"` retorna apenas declarações; o único uso concreto é no teste `flext-core/tests/unit/test_service.py:533`.
- O decorator `log_operation` e os handlers registram mensagens textuais, levando a duplicação de chaves e inconsistências na auditoria.

## Fluxo pretendido

1. `@FlextDecorators.log_operation` cria um `LogOperation` no início da execução, preenchendo `operation`, `source`, `context` (ex.: `correlation_id` via `FlextContext`).
2. O modelo é enviado ao logger/observability (ex.: `self.logger.emit_log_operation(log_op)`), garantindo formato consistente.
3. `FlextService` e `FlextHandlers` podem anexar `LogOperation` ao `FlextResult` em caso de falha, simplificando debugging em `flext-ldif`/`targets`.

## Pontos fortes x riscos

- **Fortes**: contrato claro para logging estruturado, timestamps UTC integrados, compatível com qualquer objeto (campo `obj`).
- **Riscos**: ausência de consumidores; falta enum/`Literal` para `level`; `context` aceita qualquer objeto (potencialmente não serializável); `obj` não possui serializer e pode quebrar pipelines JSON se usado de forma ingênua.

## Backlog recomendado

1. **Integração Decorator**: refatorar `FlextDecorators.log_operation` (linhas 365+) para montar `LogOperation` e delegar a serialização a um método comum.
2. **Normalização de níveis**: introduzir `FlextConstants.Logging.Level` ou `Literal["TRACE", "DEBUG", "INFO", ...]` com fallback configurável.
3. **Serialização segura**: fornecer `LogOperation.to_record()` ou `to_dict()` que serialize `obj` usando `repr`/`model_dump`, evitando exceções ao exportar.
4. **Adoção em projetos**: documentar que handlers `flext-target-*` devem usar `LogOperation` para registrar inícios/fins de sync; `flext-ldif` pode emitir `LogOperation` ao normalizar entradas.
5. **Observability**: conectar o modelo ao `flext-observability` para capturar dashboards padronizados (operation_started/completed/failure) com os mesmos campos em todos os projetos.
