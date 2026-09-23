# Plano — Estabilização flext → Deploy 0.12.0 (semver)

<!-- TOC START -->

- [Decisões pré-resolvidas (sem reabrir)](#decisoes-pre-resolvidas-sem-reabrir)
- [Âncoras (file:line, já verificadas)](#ancoras-fileline-ja-verificadas)
- [Passos (executar nesta ordem; checkpoint após cada slice verde)](#passos-executar-nesta-ordem-checkpoint-apos-cada-slice-verde)
  - [1. Absorver drift e fechar ciclo por membro (lane 0.12.0-dev)](#1-absorver-drift-e-fechar-ciclo-por-membro-lane-0120-dev)
  - [2. Carve-out NS-IMPORT = decisão A (dono flext-infra)](#2-carve-out-ns-import-decisao-a-dono-flext-infra)
  - [3. Estabilizar flext-api (47 violações; fechar flext-482u9)](#3-estabilizar-flext-api-47-violacoes-fechar-flext-482u9)
  - [4. Regras em fila na frota (uma por vez, com automação)](#4-regras-em-fila-na-frota-uma-por-vez-com-automacao)
  - [5. Gates full fleet](#5-gates-full-fleet)
  - [6. PR landing + integração](#6-pr-landing-integracao)
  - [7. Deploy semver 0.12.0](#7-deploy-semver-0120)
- [Validação (todo slice)](#validacao-todo-slice)
- [Guardrails (erros que custaram tempo — handoff §6)](#guardrails-erros-que-custaram-tempo-handoff-6)
- [Fora de escopo](#fora-de-escopo)

<!-- TOC END -->

> Criado: 2026-09-09. Fontes: handoff
> `1788987519000-handoff-refaze-checkpoint-012-stabilizacao.md` (SSOT de entrada),
> estratégia v2 `1788975180492-execution-strategy-skills-automation.md`, status
> `1788961161018-flext-012-checkpoint-status.md`. Bead-mãe: `flext-yirgp`. Diretiva do
> operador: executar IMEDIATAMENTE, poucos passos, sem nova análise, SEM mudar
> arquitetura — estabilizar runtime é o que vale.

## Decisões pré-resolvidas (sem reabrir)

- **D1 — Contradição NS-IMPORT: opção A** (carve-out no dono). `_reverse_import`
  (`flext-infra/src/flext_infra/validate/_namespace_rules/imports.py:151-164`) passa a
  permitir runtime-import das facades de DECLARAÇÃO `m`/`u` quando owner_rank ≤ 1
  (settings/config); `t` continua TYPE_CHECKING-only. B (reescrever settings de 13+
  consumidores) rejeitada — muda arquitetura; C (suspender regra) proibida pelo
  operador.
- **D2 — WIP compartilhado: fix-forward.** Nunca `reset/checkout/clean/stash`. WIP
  flext-api (transports `flext-482u9`, `_settings.py` canônico) CONTINUA.
- **D3 — Superfície canônica apenas.**
  `make gen/fmt/fix/mod/check/test/release-*/publication`; nunca tool cru. `crg`
  (code-review-graph, host tool) só como pre-pass estrutural; findings alimentam
  `make fix`/`make mod`, nunca substituem gates.
- **D4 — Residuais aceitos no checkpoint** (`closeout.checkpoint_0_12_0`: RED 1427 em
  flext-infra check; owners `flext-h2ffh`, `flext-1wjg1.16.34`, `flext-ct0mo`,
  `flext-nnquz`) não bloqueiam o deploy se permanecerem rastreados nos beads donos.

## Âncoras (file:line, já verificadas)

| Fato                          | Local                                                                                        |
| ----------------------------- | -------------------------------------------------------------------------------------------- |
| Ordem camadas settings→…→cli  | `flext-infra/_constants/namespace.py:35-62`                                                  |
| NS-IMPORT / `_reverse_import` | `flext-infra/validate/_namespace_rules/imports.py:151-164`                                   |
| `make mod` cwd-scoped         | `Makefile:1017-1018` (`refactor mod --apply`)                                                |
| Catálogo de codemods          | `flext-infra/_utilities/codemod_rules.py` (`codemod_rule_plan`)                              |
| Mapa NS-CONTRACT              | handoff §1.4 (`dict→t.MappingKV`, `object→t.JsonValue/JsonPayload`, `Optional→X \| None`)    |
| Tips                          | main `c424043b85`; release `4147d43428`; flext-api in-release `528c9e7f` + WIP não commitado |

## Passos (executar nesta ordem; checkpoint após cada slice verde)

### 1. Absorver drift e fechar ciclo por membro (lane `0.12.0-dev`)

- Classificar drift (root main tem 31 submodules M + `pyproject.toml`, `uv.lock`,
  `scripts/*/__init__.py`, `src/flext/__init__.py`, `docs/api-reference/generated/*` não
  commitados; release worktree tem 30 M): `git diff --submodule=log` por membro → 30
  fmt-gen legítimos absorver; flext-api estrutural continuar (D2); flext-core beartype
  investigar antes de absorver.
- Ciclo por membro: `make gen` (cwd do membro) → commit scoped (paths explícitos, nunca
  `git add -A`) → push FF (provar `git merge-base --is-ancestor`) → PR → merge no-ff em
  `origin/0.12.0-dev` → rerun gates no SHA merged → bead evidence
  (verb/cwd/exit/output/SHA).
- Superproject: commitar gitlinks + resíduo raiz → push FF.

### 2. Carve-out NS-IMPORT = decisão A (dono flext-infra)

- Editar `_reverse_import` (imports.py:151-164): owner_rank ≤ 1 permite runtime `m`/`u`;
  `t` segue TYPE_CHECKING-only (~5 linhas).
- Testes em `flext-infra/tests/unit/check/`: settings consumidor com `m/u` runtime →
  PASS; import `t` runtime → FAIL.
- Provar runtime num consumidor real: `uv run --no-sync python -c` importando settings
  de um membro da frota.
- Land flext-infra (commit → PR → merge no-ff) → `make gen` propaga → bead evidence.

### 3. Estabilizar flext-api (47 violações; fechar `flext-482u9`)

- Commitar o WIP do working tree (transports `_protocols/`→`_services/`, `_settings.py`
  canônico) — fix-forward.
- Fechar classes nesta ordem: NS-IMPORT (com carve-out do passo 2) → NS-CONTRACT via
  codemod (`make mod` no cwd flext-api; mapa handoff §1.4) → NS-STRUCT-001/002
  (`api.py:194`, `base.py:46`, MRO dos tests) → NS-LAYOUT (base.py de entrada + cli.py).
- Gate: `make fix` → `make check` → `make test` (45-270s esperado; validar runtime com
  `uv run --no-sync python -c` ANTES do gate longo).

### 4. Regras em fila na frota (uma por vez, com automação)

- NS-CONTRACT: registrar codemod no catálogo (`codemod_rules.py`) + testes
  (`tests/unit/codemod/`), propagar POR MEMBRO cwd `make mod`.
- Depois NS-STRUCT tests MRO; depois NS-LAYOUT base.py/cli.py.
- Não criar `class-nesting-mappings.yml` (proibido: descoberta é SSOT automática).

### 5. Gates full fleet

- `make fix` → `make fmt` → `make check` → `make test` (testmon obrigatório, 32
  membros). Triage por membro via subagentes; parent integra.
- Fechar fleet setup blocker (`flext-cpkk`/`flext-5k9r7`) antes de julgar #83/#84.
- Residuais D4 documentados nos beads donos; nada suprimido.

### 6. PR landing + integração

- `gh pr merge 665 --merge` e `666 --merge` (flext-infra); #83/#84 após fleet setup
  verde.
- `git merge --no-ff origin/0.12.0-dev` na lane release; gates no SHA unificado; bead
  evidence por merge (nunca rebase/force).

### 7. Deploy semver 0.12.0

- `make release-*` (version bump + tag `0.12.0`) → `make publication INDEX=Y` →
  verificação clean-install do PyPI com smoke runtime (import público em env limpo) →
  fechar beads de aceite (`flext-y3qpq.5/.6`, `flext-1wjg1.11/.12`) com SHA merged +
  digests + evidência runtime → teardown (worktree/branch release) só após prova remota.

## Validação (todo slice)

Verb canônico exit 0 + log completo (sem pipe `tail`) + commit scoped + push FF + bead
evidence `flext-yirgp` (verb/cwd/exit/decisive output/SHA).

## Guardrails (erros que custaram tempo — handoff §6)

- `git submodule update` reseta gitlinks → checkout de submodule único.
- `make mod` é cwd-scoped (Makefile:1017) → rodar POR MEMBRO.
- Pipes com `tail` perdem exit code → capturar log completo.
- `uv run --project` SEM `--no-sync` ressincroniza venv compartilhado.
- TypeAliasType (PEP 695) não serve para `isinstance` → tipo concreto.
- `t.Any` continua banido: `name_of()` extrai "Any" de `t.Any`.
- Gate flext-api demora (runtime-census importa módulos) → validar runtime antes.
- OOM em `make gen` (exit 137) → commit+push após cada slice verde (recuperação FF).

## Fora de escopo

Novas ADRs, mudanças de AGENTS.md/lei, arquitetura de settings (decisão B),
ai-hub/cosmos (`flext-mbowt.*`), qualquer refactor além do necessário para gates +
runtime verdes e publicação 0.12.0.
