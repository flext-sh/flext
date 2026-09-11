# HANDOFF — flext-gov program session 2026-09-11 (reinicio completo)

> Continuation-order: THIS fallback-first doc → `bd prime` → plan `docs/plans/2026-09-11-flext-gov-program.md` (TODO table is the Live mirror) → authority chain below.
> Wrote-and-Stop: read this fully before ANY mutation; operator approval is REQUIRED at gate (see § Pending approvals).

## 1. Identity of this program (what you are resuming)

- **Program**: `flext-gov` (epic bead `flext-ssnc7`) — governance rules + gates
  so consumers reuse canonical facades and duplication is gate-detected.
  Falls under ADR-015 + `docs/standards/consumption-law.md` (R1–R6).
- **Sibling programs NOT run here**: agents WS-A..D and ai-hub WS-H1..H5 —
  other agents coordinate via WS IDs.
- **Session date**: 2026-09-11. Last commits: see § Status table.

## 2. Authority resolution (strict order)

1. `AGENTS.md` (repo/worktree ROOT of whichever checkout you are in)
2. `.agents/skills/flext-law/SKILL.md` (branch-matched, LOCAL delivery)
3. Nearest scope `AGENTS.md` (member-level)
4. **Active Bead** (`flext-ssnc7.n` — domain truth of "what counts as done")
5. Pins: operator word > orchestration > beads > ADRs > skills > docs.

Hard refs for the fleet law themselves:
- Global rules place: `~/.agents/rules/flext/` (incl. new
  `gate-registry-ownership.md`, and pre-existing `flext-venv-hermeticity.md`).
- Global skill + command (automation cycle):
  `~/.agents/skills/framework/flext-gates-as-products/SKILL.md`
  `~/.agents/commands/flext/gov-automation-cycle.md`
- Memory keys (bd): `fleet-venv-hazard`, `gate-registry-derive`,
  `atomic-primitives-core-u`, `mod-checkpoint-includes-venv`,
  `flext-program-automation-cycle`.

## 3. Non-negotiables learned THIS session (a "must-not-repeat" list)

1. **Beads status reality**: `bd list` / `bd show` IS the SSOT of status;
   the plan's TODO table mirrors it (never the other way). It shows
   in_progress/open/closed, never narrative.
2. **Anti-hardcode runtime derivation** — never enumerate what code/SSOT can
   derive: prefixes, owners, legal symbols, gate vocabulary budgets, SARIF
   row → runtime derivation from `c.Infra.SARIF_TOOL_INFO`,
   `core_u.project_alias_owners()`, `pkg.__all__`, `_LAZY_IMPORTS`.
3. **FlextResult[None] / None success payloads are BANNED** (Result base
   rejects them). Typed payloads (e.g. `r[int]` byte-count).
4. **Bases are not attributes**: `class A(B)` → `A.B` is NOT settable;
   access inherited methods flat via the facade instance/class MRO
   (`u.append_atomic`), never `u.SomeBase` attribute hunt.
5. **make mod checkpoint includes .venv/history auto-stage** ("chore(git):
   checkpoint before ast-grep batch apply") — after every mod cycle make a
   scoped-path commit and do NOT let the checkpoint count as the work commit.
6. **Never uv sync from a fleet lane without the env guards**:
   `UV_PROJECT_ENVIRONMENT=$PWD/.venv VIRTUAL_ENV=$PWD/.venv` (leaked from
   direnv, poisoned primary venv once already — see memory
   `fleet-venv-hazard` and rule `flext-venv-hermeticity.md`).
7. **crg = tool CLI only** (`code-review-graph`, ai-hub host-tools), never a
   code dependency; rule `ban-ai-hub-crg-library-boundary.yml`.

## 4. HOW to rebuild the TODO list from the real world

```bash
bd prime                                              # session contract
bd list | grep ssnc7                                  # live statuses (SSOT)
bd show flext-ssnc7 && bd show flext-ssnc7.<n>        # planned claims / notes
```
Then reconcile § Status table below + plan TODO section. The rule: never
move the plan text past reality — adjust the BEAD/describe or the STATUS,
not the plan narrative to hide drift. If the TODO table disagrees with bd,
correct the pieces (or the actual bd state) to converge BEFORE faking.

## 5. Current work trees / branches / pins (2026-09-11 EOD)

| Repo | Path | Branch | SKA chain |
|---|---|---|---|
| flext-core lane | `~/flext-work/flext-core-gov` | `feat/consumer-import-grammar` | `6440f1529` (F1 core: FamilySurface) → `14c63121d` (F4 core: Files + pins) |
| flext-infra lane | `~/flext-work/flext-infra-gov` | `feat/consumer-gates` | `8c4ef3266` (F1 infra: detector) → `ba1e5ab70` (F2/F4) → `c8a429d59` (v2 audit repairs) |
| super lane | `~/flext-work/flext-gov-super` | `feat/flext-gov-consumption-law` | `3ebf812055` (F3 docs) → `e9b8cf4050` (plan v2) → `b25d519d51` (ledger fix) → `bcf2a130bb` (automation proposal) → `551e936c88` (TODO sync) |

- Core lane `uv.lock` pins (after re-resolution):
  `flext-infra rev=0.12.0-dev#bff59228`, `flext-cli` re-resolved.
- Live CI check on core/infra tips: RED with pre-existing debt (namespace
  reform 762 findings etc.) — NOT the program delta; absorb `--no-ff` at landing.
- Live concurrent session still working on infra (template/CI churn). Do
  not collide in 0.12.0-dev landing; merge hunk-a-hunk.

## 6. Bead status snapshot (source `bd list` at EOD)

 epic `flext-ssnc7` ○
 ├ `.1` F1 in_progress (reopened for premature close; detector v2 in place)
 │  └ `.1.1` open (validation twin synthetic RED→GREEN; starts after .1 lands)
 ├ `.2` F2 in_progress (config reader consumer+family; cross-contamination fix pending)
 │  └ `.2.1` open (planted-twin validation)
 ├ `.3` F3 in_progress (docs delivered to super lane; gates markdown pending)
 ├ `.4` F4 in_progress (budget gate derives ALLOWED_GATES; atomic primitives
 │      delivered; fsync/O_NOFOLLOW/EINTR + writer unification + telemetry pending)
 ├ `.5` F5 open (tags/AI_HUB_CONSUMER after F1+F4 land)
 ├ `.6` F6 open
 ├ `.7` F7 open
 └ `.8` F-AGE in_progress — AWAITING OPERATOR APPROVAL (proposal section in plan)

Closed this session: none yet (kept honest — F1 close was reverted on
self-audit; no push from any lane yet).

## 7. Pending approvals (ask the operator, THEN proceed)

- **A1**: begin P0 (authorizing `push → PR → --no-ff` merges from all 3
  lanes into their `0.12.0-dev` integration branches, respecting concurrent
  0.12.0-dev churn absorb rules).
- **A2**: crg build on integrated tips + optional daemon during wave.
- **A3**: pilot P2 — pick one real consumer (ai-hub) for R1 RED→GREEN
  homologation; only after84 P2 proves GREEN flip warn→hard + F5 tags.

Each approval must be reconfirmed (do not extrapolate "already approved").

## 8. Canonical execution cycle (per slice, no ad-hoc)

```bash
export UV_PROJECT_ENVIRONMENT=$PWD/.venv VIRTUAL_ENV=$PWD/.venv
make gen APPLY=Y    # config SSOT → projections
make mod APPLY=Y    # ast-grep scoped (--module/--namespace) + Ruff + Pyrefly + LSP
make fix APPLY=Y    # gate fixes
make fmt APPLY=Y    # format gate
make check APPLY=Y  # full gates
make test APPLY=Y   # scoped tests with testmon
code-review-graph build | update --brief | doctor | detect-changes | dead-code | impact
```
(automated references in
`~/.agents/commands/flext/gov-automation-cycle.md`).

## 9. Workstreams depth (who owns what next)

- F1 detector v3 (small: asname in current_import text + per-root memo).
- F1 landing: FF-push → draft PR → resolve conversations → merge `--no-ff`
  into `0.12.0-dev` (core, then infra) → gates on merged SHA.
- F2 hygiene: fix cross-contamination, delete `_scope_paths` legacy,
  unify `_read_project_config` (single owner via base gate/u.Infra),
  ENFORCE-100, twin planted RED (.2.1).
- F3 gates: make check markdown gate on the SUPER lane once docs land.
- F4: fsync + O_NOFOLLOW + EINTR loop on atomic primitives; unify with
  `u.Cli.atomic_write_*` (single owner, net-negative); budget telemetry
  (measure time/memory per gate run); project_new emits
  `[tool.flext.project]` keys via scaffold.
- F6/F7: block on post-P0; workflow gates + docs bijection (three file docs).

## 10. Docs & ADRs you must read (order)

1. `AGENTS.md` (composition + composition of laws — RULES; not optional)
2. `docs/plans/2026-09-11-flext-gov-program.md` — TODO table as live state
3. `docs/architecture/adr/015-consumer-consumption-law.md` (now accepted)
4. `docs/standards/consumption-law.md` (R1-R6 canonical + anti-hardcode)
5. `docs/GOVERNANCE.md` (router: owners, gate registry, anti-hardcode)
6. `~/.agents/rules/flext/*` (registry ownership, hermeticity, etc.)

## 11. If you hit a new violation that isn't covered yet

STOP, ask one precise question. Never "improve" mid-flight. Never feign
success. Always `bd update <bead> --notes` with the exact command that
fired the divergence (4 evidences for closure require git history on the
integration lane, command/cwd/exit, decisive output, and code state).

## 12. Reconciliação docs vs campo (auditoria 2026-09-11 final)

Confrontado código real contra docs/ADRs/skills ANTES de autorizar pouso:

- [OK] SKAs conferidos, `bd list | grep ssnc7` refletido 1:1 no TODO do
  plano (fonte da verdade é ALWAYS `bd`, nunca o texto).
- [OK] `infra-gov` lane: docs de gates gerados (Makefile/README/
  pyproject/examples docs) foram reescritos pelo `make gen` — RESIDUO
  NÃO COMMITADO na lane (files: `M Makefile M README.md
  M docs/api-reference/... M pyproject.toml`). Próximo agente DEVE:
  abrir a lane, rodar `make check` para validar dir, e commitar o
  generated output por paths escopados ANTES do pouso — não migrar
  para um lane novo.
- [OK] `core-gov` lane: `.venv/`+`.ruff_cache/` sujos — que é ESPERADO,
  não é trabalho em voo; commit escopado no primeiro ciclo da sessão
  futura para não subir das contaminações.
- [AWAITING] crg graphs ainda ausentes em ambas as lanes — `build` nos
  tips integrados (A2 acima); `doctor` crítico até lá.
- [AWAITING] ENFORCE-100 (R2) e 101 (R4 budget) ainda NÃO catalogados —
  NÃO registrar como deliverado (F2/F4 fazem) — e NO R1 ainda são as
  únicas linhas de enforcement do programa.
- [LAW] F5 só abre depois de F1+F4 pousados com gates verdes; e
  só após `warn→hard` pilot verde.

## 13. Decreto de continuidade (OBRIGATÓRIO antes de qualquer efeito)

- Reabrir o `docs/plans/2026-09-11-flext-gov-program.md` TODO e confirmar
  que `bd list` e SKAs ainda casam depois de sincronizar (nunca pular).
- Revalidar que as 3 lanes estão no mesmo estado de branch acima (se
  algum agente mexeu no origin `0.12.0-dev`, rodar `git fetch` e aferir
  ancestralidade com `git merge-base --is-ancestor`) antes do pouso
  `--no-ff`.
- As regras-guia do programa continuam nos FILES vivos: plan (TODO),
  handoff (este), ADR-015, GOVERNANCE.md, consumption-law.md,
  `~/.agents/{rules,skills,commands}/...`. Qualquer réplica re-gerada
  por `agentsctl sync` recebe o conteúdo do arquivo canônico, nunca o
  inverso (sync é delivery, não é dono).
- END OF TURN protocol: ao cruzar cada aprovação (A1..A3) registrar
  `bd remember` novo + update no bead dono + versos no plan/TODO antes
  da re-execução. Nunca fiar conclusões em narrativa; tudo com
  SKA/command evidence recolhida.

STOP here. Re-read once more before mutating anything.
