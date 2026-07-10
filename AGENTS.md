# AGENTS.md — FLEXT Canonical Engineering Law

## § Meta do FLEXT (North Star — governa todas as ações)

FLEXT é a plataforma fundacional tipada e ecossistema de pacotes Python para integração de dados, tooling de plataforma e conectores operacionais enterprise. Todo pacote `flext-*` herda de uma única fonte de verdade arquitetural (`flext-core`) e serve a esta meta: **garantir que toda integração seja construída sobre primitivas tipadas, validadas e reutilizáveis** — com contratos `r[T]` em todo caminho falível, facades canônicas (`c/m/t/p/u`) por responsabilidade, e zero código ad-hoc.

O sucesso do FLEXT é medido por: net-LOC negativo em refactors, zero `Any`/bypass/stub, e toda mudança verde validada com evidência antes de declarar pronto.

### Cadeia de governança inviolável (sempre ativa)

Esta Meta e as regras universais abaixo governam **todas as ações de todos os agentes em todas as sessões**, sem exceção, atalho, ou flexibilização por conveniência, urgência ou trivialidade percebida. A cadeia é always-on via prelúdio do `~/.ai-hub/AGENTS.md` + hooks `ai-hub-hook.sh` (PreToolUse/PostToolUse/SessionStart/Stop) + carregamento deste arquivo:

1. **Meta do FLEXT** (acima) — o norte que toda decisão técnica serve.
2. **Universal Agent Law** (abaixo, espelha `~/.ai-hub/AGENTS.md`) — R0–R15 invioláveis.
3. **Regras FLEXT** (abaixo do bloco universal) — stack, naming, contratos, runtime.
4. **Skills path-scoped** (`.agents/skills/*/SKILL.md`) — carregadas por contexto.

Se qualquer ação não puder servir à Meta nem obedecer às regras limpas, o agente PARA e pergunta ao operador — nunca desvia, contorna, ou executa às cegas.

### Precedência absoluta de decisão (sempre ativa, inegociável)

Quando camadas conflitam, a ordem abaixo decide — e o artefato de camada inferior é AJUSTADO para refletir a camada superior, nunca o contrário:

1. **Pedido vivo do operador** — prioridade máxima. Sobrepõe beads, planos, ADRs, skills e documentação. Se um pedido conflita com qualquer artefato, o artefato (bead/plano/ADR/skill/doc) é corrigido para seguir o pedido.
2. **Beads** — sobrepõem ADRs, skills e docs.
3. **ADRs** — sobrepõem skills e docs.
4. **Skills e docs** — base; cedem a qualquer camada acima.

Em caso de dúvida, conflito ou ambiguidade, o agente PERGUNTA ao operador antes de agir — sempre.

<!-- mro-wkii.14 (agent: codegen) — regras universais U2–U8 gravadas por pedido vivo; não remover sem ADR + pedido do operador. Base flext-core (runtime config/settings) em estabilização por outro agente — esta lane é governança + scaffold. -->

### Regras universais FLEXT para config/settings, typing e MRO (sempre ativas, invioláveis)

Estas regras (U2–U8) complementam a precedência (U1, acima) e a Universal Agent Law (R0–R18). Onde qualquer ADR/skill/doc conflitar, o artefato é AJUSTADO — nunca a regra.

- **U2 — Acesso strict a config/settings (única forma).** `from <pkg> import config` / `from <pkg> import settings` → `config.<Namespace>.<domain>` / `settings.<Namespace>.<domain>` (ex.: `from ai_hub import config; config.AiHub.*`). Demais config/settings chegam por **MRO**. Proibido qualquer outro caminho (`self.settings`, dict solto, proxy fora de `u`).
- **U3 — Modelado, nunca model-less no consumo.** Domínios são `BaseModel` validados (`frozen=True, extra="forbid"` por domínio; `Root` `frozen=True, extra="ignore"`); `model_validate` na borda; **nunca `dict`/`Any`/`object` no consumo**. Ingestão YAML model-less fica confinada à borda (`FlextConfig` lendo `config/*.yaml`).
- **U4 — ConfigProxy só em `u`.** A capacidade de proxy/config_access vive somente como `ConfigProxy` tipado/lazy em `_utilities/{config,settings}.py`, composto em `u.<Namespace>` por MRO, resolvendo `<pkg>.config` via `importlib` (sem ciclo). Proibido `proxy.py`/`_config_access.py` solto.
- **U5 — Import direction `c → t → p → m → u`.** Forward (alta consome baixa) em runtime; reverse SEMPRE via `TYPE_CHECKING`; cross-project (consumer → base upstream) livre em runtime; leaf config/settings nunca importam a facade `c/t/p/m/u` do próprio projeto em runtime; exceção cuidadosa documentada com prova de não-ciclo.
- **U6 — Typing estrito.** Nunca `Any`/`object`. Anotar sempre com tipos (`t.*` aliases), nunca com classes. Composto usa alias de `t` (`t.MappingOf[K,V]`, `t.SequenceOf[T]`, …). Nullable sempre explícito `T | None` (fora, nunca implícito). Em `models`, importar `p` via `TYPE_CHECKING` (models fica Pydantic-only em runtime). Em `protocols`, importar `m` via `TYPE_CHECKING` (reverse obrigatório; tipa os `@property` com o modelo real).
- **U7 — Zero helpers soltos / zero aliases de compat.** Nenhuma função helper fora do facade MRO; nenhum alias/shim/`DEPRECATED` de compatibilidade; remoção no mesmo ciclo (net-LOC ≤ 0).
- **U8 — Comentário de coordenação por edição.** Toda edição em superfície compartilhada (`AGENTS.md`, ADRs, facades `c/t/p/m/u`, leaf config/settings, codegen, `__init__` gerado) leva comentário curto no trecho alterado indicando agente + bead + motivo, para evitar conflito entre agentes em paralelo.

<!-- BEGIN UNIVERSAL AGENT LAW (portable; regenerable; do not edit inside) -->

## Universal Agent Law (portable core)

This block references `~/.ai-hub/AGENTS.md` as the single source of truth for the universal cross-project law. The full detailed version lives in `~/.ai-hub/docs/agent-law-full.md`.

### Supreme Rule — Absolute Truth, Never Lie

Honesty at 100%, always, backed by real evidence. "I could not" is always acceptable.

### Supreme Law — Resolve, Never Hide

Fix every defect at the root in GitOps/source and verify green. No bypass, workaround, or suppression.

### Core Rules (R0–R18)

- R0: Zero-tolerance for bypass/fallback/hardcode/stub. Fix root cause generically.
- R1: Fix-forward-only. Never `git checkout/restore/reset --hard/stash/revert` another's work.
- R2: Root-cause only. No TODOs, fakes, fallbacks, suppressions.
- R3: Stay in scope. No unrequested changes.
- R4: Evidence before claiming done (command + exit code + output).
- R5: Land your work — commit and push verified changes, no agent attribution.
- R6: Strict typing. No `Any`/bare `object`.
- R7: Bare commands only; no `.venv/bin/` prefixes.
- R8: Fix docs at the source.
- R9: GitOps is the only cluster-management channel.
- R10: Blocked operation protocol — STOP, diagnose, hand to user, wait.
- R11: Execute as planned, else stop and ask.
- R12: Production-readiness — every non-green is an incident.
- R13: Change accountability — atomic, impact/risk declared, no compat shims.
- R14: Dev/prod parity.
- R15: Bead ledger discipline — continuous status and evidence.
- R16: Operator-precedence + ask-when-unsure. A live operator/user request ALWAYS supersedes every bead, plan, ADR, skill, and doc; the strict precedence is **operator request > beads > ADRs > skills > docs**. When a request conflicts with any of these, the request wins and the conflicting artifact MUST be adjusted in the SAME cycle (update bead, edit ADR/plan/skill/doc, record SHA/evidence) — never refuse or defer a request by citing a lower artifact as authority. On ANY doubt or ambiguity, STOP and ASK the operator before acting — never guess or assume.
- R17: Law binds EVERY agent (subagents included, any depth). Every delegation prompt MUST embed the Supreme Rule, Supreme Law, R18, and the exact validation commands. A subagent violation is the coordinator's violation.
- R18: Continuous-green — tree importable/collectable at EVERY instant, not just mission end. Per edit batch (≤5 files): fresh-import smoke + `ruff --no-fix` + typecheck + scoped tests, all green before next batch. Facade/public member move/rename/removal updates ALL consumers (grep-proof, workspace-wide) in the SAME batch. Broken import/collection = active incident: stop everything, fix first.

### Context-Economy Directive

Do not restate these rules. Prefer targeted tool calls and `make` verbs.

<!-- END UNIVERSAL AGENT LAW -->

## Scope and authoritative sources

1. User request (highest)
1. `AGENTS.md` (this file)
1. `~/.claude/AGENTS.md`
1. `.agents/skills/*/SKILL.md`

`AGENTS.md` below is the operational summary for the monorepo. Detailed mechanics live in SKILL docs.

## Quick execution flow (per task)

1. Confirm active bead/issue and ownership with `bd ready` and `bd show <id>`.
1. Read the relevant local scoped SKILL docs before editing.
1. Run the narrowest smell/quality discovery first (`qlty`, `rg`, `sg`, or `scope` as available).
1. Reuse canonical origin before creating helpers/abstractions.
1. Make the minimal fix, then run the first local validation gate.
1. Update impacted callers in the same cycle.
1. Record evidence and next step in Beads before any handoff.

Any unresolved blocker at step 6 keeps the change incomplete.

## Non-negotiables

- Do not introduce bypasses, shims, fallbacks, compat aliases, or pass-through wrappers.
- No ad-hoc helper inflation without proving the canonical owner is missing.
- No broad edits outside the active lane.
- Do not edit `.beads/*.jsonl` manually.
- Prefer `make`/`ruff`/`pyrefly` workflows over one-off scripts for broad refactors.
- If a command is blocked or ambiguous, stop and surface evidence instead of inventing a workaround.

## FLEXT architecture constraints (compact)

### Stack and style

- Python 3.13+, Pydantic v2, Ruff, Pyrefly, Pyright, Mypy, Make.
- Follow MRO namespace classes and project facades (`c/m/t/p/u`, etc.).
- One canonical class/namespace owner per concern before adding new constructs.
- Prefer composing via MRO + mixins over duplicate utilities.

### Naming and contracts

- Keep aliases canonical: `c`, `m`, `t`, `p`, `u`, and operational aliases (`r`, `e`, `s`, `x`) from project facades.
- Facade owner modules that extend upstream FLEXT facades by MRO import the upstream short alias and use it as the base class, then rebind the local public alias at the bottom, e.g. `from flext_cli import m, u`; `class FlextPluginModels(m): ...`; `m = FlextPluginModels`.
- Project `base.py` may import upstream runtime `s` as the service base and rebind local `s` once, e.g. `from flext_core import s`; `class FlextDbOracleServiceBase(s, FlextDbOracleUtilitiesDbOracle): ...`; `s = FlextDbOracleServiceBase`.
- Project `api.py` stays a thin MRO facade over the composed runtime class and publishes the package operational alias, e.g. `class FlextDbOracleApi(FlextDbOracleApiRuntime): ...`; `db_oracle = FlextDbOracleApi`.
- Use `r[T]` for fallible app paths (avoid ad-hoc error dicts or raw exceptions for control flow).
- Keep `__init__.py` as export-only.
- Keep abstractions layered by project boundaries (`src` first, tests/examples/scripts are consumers).

### API/runtime constraints

- Prefer typed `OptionsModel.model_validate(kwargs)` for dynamic payloads.
- Avoid raw `os.environ` in `src/` runtime; go through settings abstractions.
- Do not import abstracted framework libs directly from consumer projects; use FLEXT abstractions.
- Reject speculative architecture migration without a concrete blocker and a scoped acceptance target.

### Config / parametrization SSOT (ADR-005)

- Five concerns, one owner each: `constants` = defaults/invariants (`c.*`); `config/` = execution parametrization; `settings` = env-override (`FlextSettings`); `templates/*.j2` = large strings (Jinja2 via `flext-cli`); sibling `schemas/*.schema.json` = validation.
- Execution parametrization lives **only** under a package `config/` dir; no schema/config source outside it.
- `config` ≠ `settings`: the settings-bound subset is a separate file (`config/settings.yaml`).
- Large/derived structures are **generated** by `_constants/_generated.py` from `config/`; hardcoding a large structure in `_constants/` is a blocked defect.
- Layering (no runtime cycle): `flext-core` runtime-minimal (stdlib only, no Jinja2, never imports cli/infra at runtime) → `flext-cli` owns the universal template/config/schema engine → `flext-infra` enforces.
- Canonical: [`docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md`](docs/architecture/adr/005-config-settings-constants-templates-schemas-ssot.md) · plan [`docs/architecture/config-ssot-migration-plan.md`](docs/architecture/config-ssot-migration-plan.md) · beads `mro-wkii`.

### Strict typing, import layering, config access (R16 — inviolable)

- **Typing**: never `Any`/`object`; never annotate with a concrete class. Use `t.*` aliases and `p.*` protocols; composite types use a `t.*` alias with `| None` on the **outside** (`t.Foo | None`). Import `p` and `m` under `TYPE_CHECKING` to sharpen typing (protocol modules import `m` under `TYPE_CHECKING`).
- **No loose helpers / no compat aliases**: no standalone functions or compatibility shims; everything flows through `c/t/p/m/u` composed by MRO.
- **Import order** strict `c → t → p → m → u`: a later facade may import earlier ones at runtime; the reverse (earlier importing later, e.g. `c` importing `m`) must be `TYPE_CHECKING`-only. `m` may lazy-import `c`; internal modules may, with extreme care, import a sibling directly only to break a real cycle.
- **Config/settings access is single-form**: always `from <namespace> import config, settings` then `config.<Ns>.*` / `settings.<Ns>.*` (e.g. `from ai_hub import config, settings` → `config.AiHub.*`). Namespace fields are modeled nested `BaseModel` classes with validation — never a model-less dict; this is the standardized delivery the old proxy provided. Other projects inherit via MRO. No other access form may exist.
- **Edit-coordination comment**: when editing a file, add a short inline comment explaining the change *for the other agent* so concurrent agents don't conflict or re-revert each other.

## Project map

- Governed packages: `flext-*`.
- Root docs and onboarding: `docs/`.
- Shared tests: `tests/` and project-local `tests/` trees.
- Scripts/tools: `scripts/`, `workspace_custom.mk`, top-level `Makefile`.

## Build, test, and local dev commands

```bash
make help
make boot
make check
make check PROJECT=<proj> CHECK_GATES=<gates>
make test PROJECT=<proj> MATCH=<expr>
make docs DOCS_PHASE=<generate|fix|audit|build|validate> PROJECT=<proj>
make val VALIDATE_SCOPE=workspace
make ship WHAT=<save|tag|push|pr|rel>
```

Common gate values: `lint`, `format`, `pyrefly`, `mypy`, `pyright`, `markdown`, `go`, `loc-cap`, `boundary`, `coordination`.

Recommended baseline for contribution work:

- `make check CHANGED_ONLY=1`
- `make test PROJECT=<proj> MATCH=docs`
- `make val VALIDATE_SCOPE=workspace`

## Testing and quality gates

- `ruff` and `pyrefly` are the first gates for touched files.
- For project-level contract changes, run project-local checks before wider propagation.
- Keep failure evidence in Beads: command, output, and exit code.

### Safe validation before production (universal)

- Validations and tests must be REAL — they execute the actual code path — yet
  must never mutate the active workspace or environment. Anything that would
  write outside the bead lane runs in an isolated sandbox (`pytester`,
  `tmp_path`, temp-dir synthetic packages); evidence artifacts under
  `.beads/artifacts/` are the only permitted side effects.
- Activating a behavior/enforcement change as the workspace or production
  default is a SEPARATE, explicit final gate: allowed only after the full
  validation chain (unit + E2E + read-only baseline) is green with recorded
  evidence — never in the same edit that introduces the change.

## Commit and PR behavior

- Default profile is land-immediately: after scoped green validation, stage only
  the active bead lane files, commit, push fast-forward, and record SHA/evidence
  in Beads.
- The operator grants durable authorization for normal scoped `git add`,
  `git commit`, and fast-forward `git push`; do not stop at “needs
  authorization” for routine landing.
- Never use `git add .` in the shared worktree. Use explicit pathspecs and
  coordinate overlaps through Beads before staging.
- Escalate only destructive, non-fast-forward, history-rewrite, rollback, or
  cross-lane ambiguity. A dirty worktree outside the bead is not a blocker when
  explicit pathspecs can isolate the lane.
- PRs/commits should state: scope, why, commands run, and remaining risk.

## Tooling and agent workflow (ECC alignment)

- Use repository skills: `.agents/skills/*` and `gd`/`scope`/`sg` where available.
- `make` is the canonical execution lane; avoid direct `git`-wide scripts when a Make target exists.
- FLEXT participates in the `~/.ai-hub` distributed workspace base: `make cosmos-help` exposes dispatcher verbs; the common base is maintained from `~/.ai-hub` via `make workspaces WHAT=distribute APPLY=1`.
- Bead system (`bd`) is the mandatory work ledger.
- Agent lanes (Claude, Codex, Gemini, and their subagents) claim work via `bd` (epics/tasks), keep child beads for disjoint scopes, and record evidence in bead notes rather than chat-only state.
- Subagents write verbose findings to disk (`coordination/resultados/` or `.beads/artifacts/`) and update `bd` only with filepath and status.
- Repeated cross-file edits require caller/audit validation before marking done.

## Verification expectation

A task is complete only with:

- objective command evidence (command + exit code + output),
- a scoped commit and fast-forward push, with SHA recorded in Beads,
- no unresolved scoped smells in the touched lane,
- bead notes updated with blocker status or completion evidence.
