# Política de supressões (mypy / pyright / pyrefly)

**Regras (AGENTS.md + decisão do repositório):**

0. **Overrides** — Seguir sempre o modelo padrão de `pyproject.toml` sincronizado do repositório FLEXT por `make upgrade`. Não adicionar overrides de mypy/pyright fora desse padrão.

1. **Any** — Uso de `Any` é **terminantemente proibido**, exceto quando exigido por biblioteca externa. Nesses casos: **evidência** (ex.: assinatura da lib) e **comentário** no código explicando a exceção.

2. **Unreachable** — Não suprimir `unreachable`. flext-core não usa override para isso; corrigir o fluxo no código (estrutura de validadores/ramificações) em vez de desligar a regra.

3. **Supressões inline** — Não usar `# pyright: ignore`, `# pyrefly: ignore` ou equivalentes para contornar o linter. Corrigir pela **causa raiz** usando os padrões e skills do flext e as regras de AGENTS.md.

4. **Dict em create*for*\*** — Não usar `dict[str, t.GeneralValueType]` para construir settings. Usar `**overrides: object` e `dict[str, object]` com `model_validate(...)`, alinhado ao padrão de flext-core (`from_kwargs`, `merge_defaults`).

---

## O que foi feito (correção na raiz)

- **flext-dbt-ldap**
  - Removido `[[tool.mypy.overrides]]` por completo.
  - `reportUntypedBaseClass`: base tipada em flext-core; em `protocols.py` passamos a usar `p_core.Service[...]` (import de `flext_core.protocols.FlextProtocols`) em vez de `p_ldap.Service[...]`, para o pyright resolver o tipo da base.

- **flext-tap-ldif**
  - Removido override de mypy em `pyproject.toml`.
  - Settings: `create_for_development` / `create_for_production` / `create_for_testing` passam a usar `**overrides: object` e `defaults: dict[str, object]` com `model_validate(defaults)` (sem dict genérico de GeneralValueType).
  - Utilities: erro pyrefly “bad-assignment / breaking cycles” resolvido na raiz extraindo a construção do record para `build_record_from_lines()` (tipo de retorno concreto `dict[str, str | list[str]]`), sem supressão inline; conversão para `dict[str, t.GeneralValueType]` só no retorno de `convert_ldif_entry_to_record`.

- **typings**
  - Corrigido stub `typings/generated/sqlalchemy/sql/visitors.pyi`: parâmetros duplicados `self` em `__call__` substituídos por nomes únicos (`visitable`, `target`) para mypy não falhar ao analisar dependentes.

---

## Atualizações (continuação do plano)

- **flext-core**
  - **FlextSettings.**init\*\*\*\*: Mantido `cast("dict[str, Any]", kwargs)` para `BaseSettings.__init__` com comentário de exceção de política (AGENTS.md): fronteira de biblioteca; pydantic_settings espera kwargs dinâmicos.
- **flext-dbt-ldap**
  - **Unreachable**: Helper `_entry_attrs_mapping(entry)` no módulo; `normalize_attributes` / `_get_object_classes` e `dbt_client._matches_schema` usam esse helper. Import de `_entry_attrs_mapping` movido para o topo de `dbt_client.py` (lint PLC0415).
  - **Fronteira Pydantic (SSOT)**: Um único `[[tool.mypy.overrides]]` em `pyproject.toml` para `module = "flext_dbt_ldap.models"` com `disallow_any_explicit = false`. Causa: membro sintético `__mypy-replace` na cadeia Value → BaseModel; limitação conhecida mypy/Pydantic. Override documentado no próprio `pyproject.toml` e aqui; não adicionar outros overrides fora desse padrão.
- **flext-tap-ldif**
  - **Unreachable**: removido `return` inalcançável em `ldif_processor.py`. **tests**: `t` em `__all__` de `tests/typings.py`. **Singer\*Message**: `model_validate({...})` em `utilities.py`. **Stub**: `typings/generated/singer_sdk/__init__.pyi` com `Stream`, `Tap` e `Tap.cli`. **Check script**: `MYPYPATH` com `ROOT/typings/generated` para o stub ser usado. Check passa sem override adicional.

Regra: qualquer novo override deve seguir o padrão (módulo específico, comentário de fronteira, registro aqui).
