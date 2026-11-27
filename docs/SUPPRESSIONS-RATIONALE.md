# Política de supressões (Ruff / Pyrefly)

<!-- TOC START -->

- [O que foi feito (correção na raiz)](#o-que-foi-feito-correcao-na-raiz)
- [Atualizações (continuação do plano)](#atualizacoes-continuacao-do-plano)

<!-- TOC END -->

**Regras (AGENTS.md + decisão do repositório):**

0. **Overrides** — Seguir sempre o modelo padrão de `pyproject.toml` projetado de
   `config/tooling.yaml` por `make check`. Não adicionar overrides de Ruff ou Pyrefly fora
   desse padrão. Ruff é o único formatador e linter e Pyrefly o único verificador de
   tipos (ordem do operador 2026-11-13 `ag-6w7a`).

1. **Any** — Uso de `Any` é **terminantemente proibido** sem exceções.

2. **Unreachable** — Não suprimir `unreachable`. flext-core não usa override para isso;
   corrigir o fluxo no código (estrutura de validadores/ramificações) em vez de desligar
   a regra.

3. **Supressões inline** — Não usar `# type: ignore`, `# pyrefly: ignore`, `# noqa` ou
   equivalentes para contornar o linter. Corrigir pela **causa raiz** usando os padrões
   e skills do flext e as regras de AGENTS.md.

4. **Dict em create*for*\*** — Não usar contratos de dicionário genérico para settings.
   Usar modelos Pydantic de boundary (`m.SettingsOverridesModel`) e materializar
   `dict(...)` apenas no ponto local de mutação antes de `model_validate(...)`, alinhado
   ao padrão de flext-core (`from_kwargs`, `merge_defaults`).

---

## O que foi feito (correção na raiz)

- **flext-dbt-ldap**

  - `reportUntypedBaseClass`: base tipada em flext-core; em `protocols.py` passamos a
    usar `p_core.Service[...]` (import de `flext_core.protocols.FlextProtocols`) em vez
    de `p_ldap.Service[...]`, para o tipo da base ser resolvido.

- **flext-tap-ldif**

  - Settings: `create_for_development` / `create_for_production` / `create_for_testing`
    passam a usar `overrides: p.SettingsOverridesModel` e defaults em modelos
    explícitos, mantendo `model_validate(...)` sem interfaces genéricas.
  - Utilities: erro pyrefly “bad-assignment / breaking cycles” resolvido na raiz
    extraindo a construção do record para `build_record_from_lines()` com tipagem forte;
    sem supressão inline e sem promover fronteiras genéricas.

- **Stubs de terceiros**: a projeção `typings/generated` foi retirada. Bibliotecas
  sem tipagem são consumidas por protocolos `p.*` na fronteira (como `ldap3`).
  Nenhum stub `.pyi` próprio é mantido.

---

## Atualizações (continuação do plano)

- **flext-core**
  - **FlextSettings.**init\*\*\*\*: Removida abordagem permissiva de cast em fronteira
    de biblioteca; fronteira segue contrato de modelo explícito e validação direta.
- **flext-dbt-ldap**
  - **Unreachable**: Helper `_entry_attrs_mapping(entry)` no módulo;
    `normalize_attributes` / `_get_object_classes` e `dbt_client._matches_schema` usam
    esse helper. Import de `_entry_attrs_mapping` movido para o topo de `dbt_client.py`
    (lint PLC0415).
- **flext-tap-ldif**
  - **Unreachable**: removido `return` inalcançável em `ldif_processor.py`. **tests**:
    `t` em `**all**` de `tests/typings.py`. **Singer\*Message**: `model_validate({...})`
    em `utilities.py`. Check passa sem override adicional.

Regra: qualquer novo override deve ser um axioma declarado no SSOT de tooling
(`flext-infra/config/tooling.yaml`); este documento não é um registro de exceções.
