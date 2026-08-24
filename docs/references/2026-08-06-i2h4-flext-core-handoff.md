# Handoff: i2h4 flext-core Refactor — Session State 2026-08-06

## Contexto

Epic `mro-sb3q.1` — refatoração tipo i2h4 do ai-hub em flext-core.
Objetivo: cortes profundos, atômico, sem compatibilidade, dead code exterminado,
codemod governance universal (ast-grep + make mod + CRG como lei),
ADRs arrumados, lean patterns propagados para 38 projetos.

**Proibição absoluta de rollback. Tudo fix-forward.**

---

## Estado Atual (o que foi feito)

### Beads criados (12 beads, 0 completos)

Epic: `mro-sb3q.1` (P1, OPEN)
Parent: `mro-sb3q` (codemod governance)

**P(-1) — PRIORIDADE MÁXIMA (P0):**

- `mro-sb3q.1.7` — Empacotar flext-infra codemod rules como package data
- `mro-sb3q.1.8` — Discovery cascata importlib.resources
- `mro-sb3q.1.9` — make mod usa cascata
- `mro-sb3q.1.10` — sgconfig.yml condicional
- `mro-sb3q.1.11` — Remover projeção ast-grep-rules do codegen
- `mro-sb3q.1.12` — Validar make mod sem projeção

**W1-W6 (P1):**

- `mro-sb3q.1.1` — W1: ADRs arrumados + docs atualizadas
- `mro-sb3q.1.2` — W2: ast-grep enforcement rules (error gates)
- `mro-sb3q.1.3` — W3: Rewire 11 imports privados (atômico)
- `mro-sb3q.1.4` — W4: Dead code purge
- `mro-sb3q.1.5` — W5: Skills + AGENTS + prompts alinhados
- `mro-sb3q.1.6` — W6: Landing + validação fleet-wide

### Git state (submódulos)

| Submodule | Branch | SHA | Status |
|---|---|---|---|
| flext-infra | 0.12.0-dev | 735a20c1 | ✓ sincronizado (reset feito) |
| flext-core | 0.12.0-dev | f17751e86 | ✓ sincronizado |
| flext-tests | 0.12.0-dev | 75dfa4c | ✓ pull FF feito |
| flext-quality | 0.12.0-dev | 3f213bd | ✓ pull FF feito |
| outros 27 | 0.12.0-dev | — | ✓ sincronizados |

**Mudanças pendentes no root:**

- `M flext-cli`, `M flext-dbt-ldap`, `M flext-grpc`, `M flext-infra`, etc. (gitlink drift)
- `M uv.lock`
- 4 arquivos novos não tracked (docs references + superpowers plans)

### ast-grep-rules state

| Local | Status |
|---|---|
| Root `ast-grep-rules/` | ✓ intacto (5 rules) |
| `flext-infra/codemod/rules/` | ✓ intacto (SSOT, 5 rules + refactor/) |
| Submodules `ast-grep-rules/` | ✗ deletados (eram cópias codegen — regenerar) |

---

## O Que Precisa Ser Feito (ordem de prioridade)

### P(-1): ast-grep Rules Empacotadas em Cascata (BLOQUEADOR)

> **Problema:** `make gen` copia `ast-grep-rules/` para cada projeto.
> Deve ser: rules empacotadas nas bibliotecas, descobertas via cascata.

**Design correto:**
```
flext-infra: regras em flext_infra.codemod.rules (importlib.resources)
flext-core: regras em flext_core.codemod.rules (importlib.resources)
flext-cli: regras em flext_cli.codemod.rules (importlib.resources)

sgconfig.yml: SÓ se projeto tem rules próprias
make mod: descobre regras em cascata de pacotes instalados
```

**Implementação (6 beads):**

1. **`mro-sb3q.1.7` — Empacotar rules como package data**
   - Em `flext-infra/src/flext_infra/codemod/rules/`: adicionar `__init__.py`
   - Em `flext-infra/pyproject.toml`: adicionar force-include de rules
   - Verificar: `importlib.resources.files('flext_infra.codemod') / 'rules'` acessível

2. **`mro-sb3q.1.8` — Discovery cascata**
   - Criar `flext-infra/src/flext_infra/codemod/discovery.py`
   - Função `discover_rules(*extra_packages) -> list[Path]`
   - Cascade: flext_core → flext_cli → flext_infra → projeto local

3. **`mro-sb3q.1.9` — make mod usa cascata**
   - Ajustar `FlextInfraCodemodBatchApply` em `batch_apply.py`
   - Usar `discover_rules()` em vez de ler `sgconfig.yml`
   - Manter safety circuit (checkpoint → apply → measure → rollback)

4. **`mro-sb3q.1.10` — sgconfig.yml condicional**
   - Template `sgconfig.yml.j2`: só renderizar se projeto tem rules próprias
   - Se não tem: não criar sgconfig.yml

5. **`mro-sb3q.1.11` — Remover projeção do codegen**
   - Em `conform.py:_plan_ast_grep_surfaces`: remover cópia de rules
   - Manter renderização condicional de sgconfig.yml

6. **`mro-sb3q.1.12` — Validar**
   - `make gen` não cria `ast-grep-rules/`
   - `make mod WHAT=check` descobre rules via cascata
   - `make mod WHAT=apply APPLY=Y` funciona

### F0: Desbloquear CI (após P(-1))

```bash
git submodule foreach --recursive 'git checkout 0.12.0-dev && git pull --ff-only origin 0.12.0-dev 2>/dev/null || true'
git submodule foreach 'git checkout -- . 2>/dev/null || true'
make gen WHAT=apply APPLY=Y
make check && make test
```

### F1-F8 (resto do plano)

- F1: Abrir lane `make work`
- F2: Governança universal (ADR-012 + AGENTS.md + hooks instalados)
- F3: 7 ast-grep error gates
- F4: Rewire 14 imports privados
- F5: 12 lean patterns (cached_property, AliasGenerator, u.service, etc.)
- F6: Dead code exterminado
- F7: Skills + AGENTS + prompts
- F8: Validação + landing

---

## Descobertas da Pesquisa (para referência)

### 14 imports privados em flext-core

| Arquivo | Imports | Facade |
|---|---|---|
| `loggings.py:23-28` | 6 (`_constants`, `_exceptions`, `_models`, `_utilities`) | `c/e/m/u` |
| `mixins.py:15-16` | 2 (`_models`, `_typings`) | `m/t` |
| `dispatcher.py:15` | 1 (`_utilities.dispatcher_execute`) | inline + delete |
| `dispatcher_execute.py:18-19` | 2 (`_utilities.guards_*`) | `u` |
| `_models/cqrs.py:23-27` | 3 (`_models.base`, `_runtime`, `_utilities`) | `m/u` |
| `_handlers_parts/` | 3 (`_utilities.handler`) | `u` |

### Dead code candidates

- `_fixtures/__init__.py` — vazio
- `_utilities/dispatcher_execute.py` — 1 ref (mover para dispatcher.py)
- `FLEXT_SERVICE_ARCHITECTURE.md` — dead doc

### ADRs

- ADR-016 → renumerar para ADR-011
- `settings-config-canonical-pattern.md` → ADR-012 (estender)
- `config-ssot-migration-plan.md` → ADR-013
- Deletar: FLEXT_SERVICE_ARCHITECTURE.md, clean-architecture.md pointer

### Market research 2025-2026

- Services são funções (Prefect, Dagster, Airflow, Temporal, Celery)
- Config é model Pydantic compartilhado
- DI via container, não singleton
- FLEXT `r`/`p`/`u` já ahead do mercado

### Lean libraries

- Adotar: cached_property+computed_field, AliasGenerator, NoDecode+BeforeValidator, syrupy, dirty-equals, time-machine
- Rejeitar: dishka/svcs/rodi, returns, msgspec, anyio/trio, bowler, fixit, freezegun

---

## Arquivos-Chave

| Arquivo | Propósito |
|---|---|
| `flext-infra/src/flext_infra/codemod/rules/` | SSOT das ast-grep rules |
| `flext-infra/src/flext_infra/codemod/batch_apply.py` | make mod batch apply |
| `flext-infra/src/flext_infra/codegen/conform.py:1355` | _plan_ast_grep_surfaces (remover cópia) |
| `flext-infra/src/flext_infra/templates/project/base/sgconfig.yml.j2` | sgconfig template (condicional) |
| `flext-core/src/flext_core/loggings.py:23-28` | 6 imports privados (rewire) |
| `flext-core/src/flext_core/mixins.py:15-16` | 2 imports privados (rewire) |
| `flext-core/src/flext_core/dispatcher.py:15` | 1 import privado (mover inline) |
| `flext-core/src/flext_core/_models/cqrs.py:23-27` | 3 imports privados (rewire) |
| `docs/architecture/adr/` | ADRs a arrumar |
| `docs/standards/development.md` | Atualizar (remover skill inexistente) |
| `.github/prompts/flext-aggressive-scale-refactor.prompt.md` | Corrigir (9 skills inexistentes) |

---

## Planos Salvos

- Plano principal: `.kimi-code/sessions/.../plans/rictor-venom-impulse.md`
- P(-1) plano: `.kimi-code/sessions/.../plans/shadowcat-barry-allen-domino.md`

---

## Princípios do Operador (invioláveis)

1. ast-grep + make mod + CRG = LEI UNIVERSAL de refatoração
2. Pre-commit e pre-push INSTALADOS e ENFORÇADOS
3. Sem compatibilidade: zero shims, adapters, wrappers
4. Dead code exterminado
5. Codemod bans = error gates de make check
6. NÃO criar documentos novos — arrumar ADRs atuais
7. Cada biblioteca/padrão = bead de ciclo atômico propagado em 38 projetos
8. Fix-forward sempre, proibição absoluta de rollback
