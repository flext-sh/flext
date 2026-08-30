# Política de supressões (mypy / pyright / pyrefly / Pylance)

**Regras (AGENTS.md + decisão do repositório):**

0. **Overrides** — Seguir sempre o modelo padrão de `pyproject.toml` sincronizado do repositório FLEXT por
   `make upgrade`. Não adicionar overrides de mypy/pyright fora desse padrão. A exceção permitida é o override de UI
   em `.vscode/settings.json` para `python.analysis.diagnosticSeverityOverrides.reportUntypedBaseClass = "none"`:
   Pylance marca falsamente como autorreferente o padrão canônico de facade MRO `from flext_cli import m`;
   `class FlextPluginModels(m): ...`; `m = FlextPluginModels`. Esse override não altera os gates CLI
   (`pyright`, `pyrefly`, `mypy`).

1. **Any** — Uso de `Any` é **terminantemente proibido** sem exceções.

2. **Unreachable** — Não suprimir `unreachable`. flext-core não usa override para isso; corrigir o fluxo no código
   (estrutura de validadores/ramificações) em vez de desligar a regra.

3. **Supressões inline** — Não usar `# pyright: ignore`, `# pyrefly: ignore` ou equivalentes para contornar o linter.
   Corrigir pela **causa raiz** usando os padrões e skills do flext e as regras de AGENTS.md.

4. **Dict em create*for*\*** — Não usar contratos de dicionário genérico para settings. Usar modelos Pydantic de
   boundary (`m.SettingsOverridesModel`) e materializar `dict(...)` apenas no ponto local de mutação antes de
   `model_validate(...)`, alinhado ao padrão de flext-core (`from_kwargs`, `merge_defaults`).

---

## O que foi feito (correção na raiz)

- **flext-dbt-ldap**
  - Removido `[[tool.mypy.overrides]]` por completo.
  - `reportUntypedBaseClass`: base tipada em flext-core; em `protocols.py` passamos a usar `p_core.Service[...]`
    (import de `flext_core.protocols.FlextProtocols`) em vez de `p_ldap.Service[...]`, para o pyright resolver o
    tipo da base.

- **flext-tap-ldif**
  - Removido override de mypy em `pyproject.toml`.
  - Settings: `create_for_development` / `create_for_production` / `create_for_testing` passam a usar
    `overrides: m.SettingsOverridesModel` e defaults em modelos explícitos, mantendo `model_validate(...)` sem
    interfaces genéricas.
  - Utilities: erro pyrefly “bad-assignment / breaking cycles” resolvido na raiz extraindo a construção do record para
    `build_record_from_lines()` com tipagem forte; sem supressão inline e sem promover fronteiras genéricas.

- **typings**
  - Corrigido stub `typings/generated/sqlalchemy/sql/visitors.pyi`: parâmetros duplicados `self` em `**call**`
    substituídos por nomes únicos (`visitable`, `target`) para mypy não falhar ao analisar dependentes.

---

## Atualizações (continuação do plano)

- **flext-core**
  - **FlextSettings.**init****: Removida abordagem permissiva de cast em fronteira de biblioteca; fronteira segue
    contrato de modelo explícito e validação direta.
- **flext-dbt-ldap**
  - **Unreachable**: Helper `_entry_attrs_mapping(entry)` no módulo; `normalize_attributes` / `_get_object_classes` e
    `dbt_client._matches_schema` usam esse helper. Import de `_entry_attrs_mapping` movido para o topo de
    `dbt_client.py` (lint PLC0415).
  - **Fronteira Pydantic (SSOT)**: Um único `[[tool.mypy.overrides]]` em `pyproject.toml` para
    `module = "flext_dbt_ldap.models"` com `disallow_any_explicit = false`. Causa: membro sintético
    `**mypy-replace` na cadeia Value → BaseModel; limitação conhecida mypy/Pydantic. Override documentado no
    próprio `pyproject.toml` e aqui; não adicionar outros overrides fora desse padrão.
- **flext-tap-ldif**
  - **Unreachable**: removido `return` inalcançável em `ldif_processor.py`. **tests**: `t` em `**all**` de
    `tests/typings.py`. **Singer\*Message**: `model_validate({...})` em `utilities.py`. **Stub**:
    `typings/generated/singer_sdk/**init**.pyi` com `Stream`, `Tap` e `Tap.cli`. **Check script**: `MYPYPATH` com
    `ROOT/typings/generated` para o stub ser usado. Check passa sem override adicional.

Regra: qualquer novo override deve seguir o padrão (módulo específico, comentário de fronteira, registro aqui).
