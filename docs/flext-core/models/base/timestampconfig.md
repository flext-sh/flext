# TimestampConfig (`FlextModels.Base.TimestampConfig`)

<!-- TOC START -->

- [Visão geral](#viso-geral)
- [Contrato detalhado](#contrato-detalhado)
- [Arquitetura e dependências](#arquitetura-e-dependncias)
  - [Conexões mapeadas](#conexes-mapeadas)
- [Situação atual no código](#situao-atual-no-cdigo)
- [Fluxo pretendido](#fluxo-pretendido)
- [Pontos fortes x limitações](#pontos-fortes-x-limitaes)
- [Backlog recomendado](#backlog-recomendado)
<!-- TOC END -->

## Visão geral

DTO configurável para sincronizar campos de data/hora em entidades, agregados ou objetos externos antes de persistência. A classe está definida em `flext_core/_models/base.py:149-165` e herda todo o comportamento de `FlextModelsCollections.Config`, o que significa validação estrita e utilitários como `merge`, `diff`, `with_updates`.

## Contrato detalhado

| Campo              | Tipo             | Padrão / Observações                                                              |
| ------------------ | ---------------- | --------------------------------------------------------------------------------- |
| `obj`              | `object`         | Destino a ser sincronizado. Hoje aceita qualquer tipo, dificultando validação.    |
| `use_utc`          | `bool`           | `True` – direciona uso de `u.Generators.generate_datetime_utc`.                   |
| `auto_update`      | `bool`           | `True` – permite atualizar `updated_at` automaticamente quando mudanças ocorrem.  |
| `format`           | `str`            | `%Y-%m-%dT%H:%M:%S.%fZ`.                                                          |
| `timezone`         | `str \| None`    | Permite sobrescrever o fuso horário padrão.                                       |
| `created_at_field` | `str`            | Regex `^[a-zA-Z_][a-zA-Z0-9_]*$`, garantindo nomes válidos para atributos Python. |
| `updated_at_field` | `str`            | Mesmo contrato do campo anterior.                                                 |
| `field_names`      | `dict[str, str]` | Mapa livre para renomear atributos em objetos legados.                            |

## Arquitetura e dependências

- Baseia-se no namespace Collections (`Config`), alinhando-se com outros DTOs de configuração (HandlerExecutionConfig, RetryConfiguration, etc.).
- Foi planejado para ser aplicado em objetos que não herdam `TimestampableMixin` (por exemplo, modelos `attrs`, `dataclasses` ou DTOs externos).
- Deveria conversar diretamente com `FlextModelsEntity.TimestampableMixin`, `u.Generators` e `u.Validation`, mas essa integração ainda não existe.

### Conexões mapeadas

- `flext_core/src/flext_core/_models/entity.py:94-205` define `TimestampableMixin` e `IdentifiableMixin`; `TimestampConfig` é o complemento configurável para objetos que não herdam essas mixins.
- `flext_core/src/flext_core/context.py:470-620` normaliza timestamps de contexto; aplicar `TimestampConfig` nesse trecho evitaria duplicação de lógica de formatação/timezone.
- `flext_core/src/flext_core/constants.py:1278-1308` lista defaults de timestamp e formatos; `TimestampConfig` deveria reutilizar esses valores em vez de declarar strings manualmente.
- `flext-ldif/src/flext_ldif/_models/domain.py` contém múltiplos campos `created_at`/`updated_at` com regras custom; `TimestampConfig` poderia padronizar esses contratos antes de exportar LDIF.

## Situação atual no código

- `rg -n "TimestampConfig" --glob "*.py" --glob "!*tests*"` retorna apenas as declarações (em `_models/base.py` e `models.py`). Não há instâncias do DTO no runtime.
- `FlextService` e `h` continuam manipulando timestamps manualmente (via mixins ou `datetime.utcnow()`), o que gera divergência quando o objeto não usa `TimestampableMixin`.

## Fluxo pretendido

1. Criar `TimestampConfig` para cada objeto não Pydantic que precise de `created_at/updated_at` antes de persistência.
2. Executar `u.Timestamp.apply(config)` (utilitário ainda não implementado) para atualizar os campos indicados (respeitando `use_utc/auto_update`).
3. Em pipelines LDIF/targets, usar `field_names` para mapear atributos esperados pelo destino (ex.: `{"created_at": "entryCreated", "updated_at": "entryUpdated"}`).

## Pontos fortes x limitações

- **Fortes**: contrato declarativo para renomear campos, escolher timezone, ativar/desativar update automático; base Config oferece `diff()` para comparar configurações (útil em auditorias/diagnósticos).
- **Limitações**: `obj` não é tipado; não cobre campos adicionais (deleted_at, synced_at); ausência total de aplicadores; valores padrão estão engessados no formato ISO e podem divergir de destinos que usam epoch.

## Backlog recomendado

1. **Aplicador oficial**: implementar `u.Timestamp.apply(config: TimestampConfig)` utilizando `setattr` seguro, validação dos campos definidos e respeito a `field_names`.
2. **Tipagem mais forte**: permitir `obj: BaseModel | TimestampableMixin | Protocol` para habilitar validações estáticas e oferecer `bind_model(type[BaseModel])`.
3. **Ampliação de campos**: estender `field_names`/config para incluir `deleted_at`, `synced_at`, `expires_at` e permitir múltiplos formatos (ISO, epoch, ms).
4. **Integração com projetos**: documentar cenários como `flext-ldif` (normalização de entradas com timestamps customizados) e `flext-target-oracle` (campos `creation_date`/`last_update`), mostrando como `TimestampConfig` evita duplicação.
