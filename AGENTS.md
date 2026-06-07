> Universal: ~/.agents/AGENTS.md (load first). Project overrides below.

<!-- TOC START -->

- [§0 QUICKSTART (15s)](#0-quickstart-15s)
- [§0 STOP CARD (read in 60s before ANY edit)](#0-stop-card-read-in-60s-before-any-edit)
- [§1 Identity](#1-identity)
- [§2 Architecture Law](#2-architecture-law)
- [§3 Code Law](#3-code-law)
- [§4 Import Law](#4-import-law)
- [§5 Make Contract](#5-make-contract)
- [§6 Quality Gates](#6-quality-gates)
- [§7 Skill System](#7-skill-system)
- [§8 Change Management](#8-change-management)
- [§9 Agent Execution Pre-requisites](#9-agent-execution-pre-requisites)
- [§10 Multi-Agent Parallel Execution Law](#10-multi-agent-parallel-execution-law)

<!-- TOC END -->

<!--
description: FLEXT canonical governance — Python 3.13+, Pydantic v2, MRO namespace law
alwaysApply: true
-->

# AGENTS.md — FLEXT Canonical Engineering Law

<!-- BEGIN UNIVERSAL AGENT LAW (portable; regenerable; do not edit inside) -->
## Universal Agent Law (portable core)

**This block is the inviolable, agent-agnostic core of engineering conduct for this repository.** It is
self-contained: it binds any AI agent — Claude, Codex, Gemini, Cursor, Cline, GitHub Copilot, or any other —
and any user, with or without access to the author's personal configuration. The live user's explicit
instructions override this block; nothing else does. These rules apply to every project type and every
session, and may not be relaxed, reinterpreted, or scoped-out for convenience, speed, or perceived triviality.

### 1. Zero-Tolerance / Strict-Total
- **Always** fix the root cause — generically, cleanly, via reuse of existing canonical code — and validate it
  in the same turn with the actual command, its exit code, and the relevant output line.
- **Always** remove superseded code in the same cycle the replacement lands. No dead code "for later".
- **Always** fail loud when the single source of truth (identity, config, contract, version) is absent — never
  substitute a guess, a local copy, or an alternative path.
- **Never** use a fallback, compatibility wrapper, legacy branch, allowlist/carve-out, skip, suppression,
  hardcode, stub, fake, `TODO`/`FIXME`, or a side-script to make a gate pass.
- **Never** classify a failure surfaced by the current task as "pre-existing", "cosmetic", "unrelated", or
  "acceptable legacy". If it appears in your flow, you own it.

### 2. Fix-Forward-Only
Multiple agents may share one working tree. Reverting to a past state silently destroys another agent's
in-flight work. **Accept the current state and fix forward.** Discarding changes via `git checkout -- <path>`,
`git restore`, `git reset --hard`, `git reset <path>`, `git stash` (hiding others' work), `git clean`, or
`git revert` of another's commit is **forbidden**. If you think you must revert → **STOP and ask the user**;
never unilaterally revert shared work.

### 3. Root Cause Only — No Workarounds
No TODOs, stubs, fakes, fallbacks, compat wrappers, or "temporary" workarounds. No suppression directives
(`# type: ignore`, blanket `# noqa`, `@ts-ignore`, `eslint-disable`, etc.) and no escape-hatch typing
(`Any`, bare `object`, unchecked casts) unless carrying a one-line documented justification. A bypass that
hides a symptom is a defect even when the gate turns green.

### 4. Stay In Scope
Do exactly what the user asked — nothing more. No unrequested refactors, renames, cleanups, "obvious
improvements", or adjacent fixes. Found something unrelated? Mention it in one sentence; do not touch it.

### 5. Evidence Before Done — Report Honesty Is 100% Mandatory
"Done" means the **complete chain validated** with objective evidence (command + exit code + output), not
conclusion-by-sample. **Never** present partial, assumed, speculative, or unverified results as verified.
State explicitly when a step was skipped, when a check failed (paste the output), and when a result is
unverified. If something only worked via a workaround, say so — it is not "done".

### 6. Execute As Planned, Else Stop And Ask
Execute the agreed plan exactly. On anything that cannot be done cleanly — a blocked tool, a missing source of
truth, a real ambiguity, or a step that would require a bad practice — **STOP and ask**, presenting concrete
options. **Every option must be a clean, root-cause solution.** Fallback, hack, hardcode, suppression, skip,
or stub are **forbidden as suggestions** — never offer one, even labelled "quick" or "temporary". Any
mid-execution deviation from the plan requires explicit user confirmation **before** applying.

### 7. Blocked-Operation Protocol
When a tool, command, or edit is blocked (deny rule, security hook, sandbox, missing permission, unavailable
integration): (1) **Stop** — do not retry a variation or seek a bypass; (2) **diagnose in one sentence** what
was blocked and why; (3) **hand the exact command or edit to the user** to run on their side; (4) **wait for
their output** before continuing; (5) **never claim done because a substitute ran** — a successful bypass is
still a violation. Forbidden bypass techniques include `bash -c`/`sh -c` subshell wrapping, `eval`/`exec`,
`env <blocked>`, `xargs <blocked>`, absolute-path swaps to dodge prefix deny rules, pipes/command-chains into a
blocked command, and invoking it via a `subprocess` call.

### 8. Strict, Most-Restrictive Typing
Use the most restrictive type that compiles. No `Any`, no bare `object`, no suppression of type errors. Fix
types at the source; depend on declared contracts, not loosely-typed escape hatches.

### 9. Universal Engineering Principles (always, no exception)
- **SSOT** — one authoritative source per fact; reference it, never duplicate or restate it; fail loud when
  absent.
- **SOLID** — SRP / OCP / LSP / ISP / DIP respected. Type-switching where polymorphism applies, fat
  interfaces, and god-objects are defects.
- **YAGNI** — no speculative params, dead branches, future-hooks, or single-implementation abstractions.
  Build only what the task needs now; delete the rest.
- **DI / DIP** — depend on abstractions (protocols/interfaces); inject collaborators; no hidden globals or
  hard-wired construction inside business logic.

### 10. User Manages Git
Do not run `git add`/`commit`/`push`/`tag` unless the user explicitly requests it, and do not suggest
committing. Read-only inspection (`status`/`log`/`diff`) is fine. When a commit is authorized, write it as the
user with no agent/bot attribution — no `Co-Authored-By`, no "Generated with …" trailer, and never override
author/committer identity.

### 11. Multi-Agent Coordination
Agents may share one working tree. Coordinate through a committed task board (e.g.
`<repo>/.agents/coordination/tasks.md`): claim a task with an ownership + lease entry before editing, heartbeat
the lease, set `done`/`blocked` on finish, and recover stale tasks from git history. Commit small and often so
a fresh agent rebuilds state from `git log`. **Never overwrite or discard another agent's work** (see Rule 2);
on a divergent approach, stop and escalate to the user.

### 12. When Unsure — Ask
If a task is unclear, ambiguous, or would expand scope → ask one focused question. If an action is hard to
reverse, affects shared state, or could surprise the user → confirm first. Authorization is scope-specific:
approval for one action once does not authorize it in future contexts.

### 13. Destructive Commands — Archive, Don't Destroy
Prefer non-destructive moves: archive a file as `<file>.bak` instead of deleting it. Do not escalate
privileges (`sudo`/`su`), change ownership/permissions, perform remote operations, or fetch over the network
without explicit user confirmation. Use the agent's structured file/search/edit tools over raw destructive
shell commands.
<!-- END UNIVERSAL AGENT LAW -->

**Canonical sources** (in priority order):

1. User message (explicit task request)
2. This file (`/flext/AGENTS.md`) — FLEXT-specific rules
3. `~/.claude/AGENTS.md` — Universal cross-project rules
4. Project skills (domain-specific patterns)
5. Default agent behavior

### USER-INTENT SUPREMACY (NON-NEGOTIABLE)

- Explicit user directives are law: deliver exactly what was requested, no scope expansion, no speculative refactor, no unauthorized architecture migration.
- Never "optimize" by changing namespace contracts (`src` vs `tests`) unless the user explicitly requested that migration.
- If the user reports regression, mess, or rejected direction, STOP feature edits immediately, perform only rollback-safe corrective work aligned to the last explicit user request.
- If the user says work is cancelled/prohibited, agents must halt implementation edits and only execute the explicit governance/documentation action requested in that same message.
- Any output that ignores or reinterprets the user's direct instruction is INVALID work.

**Scope separation**:

- `~/.claude/AGENTS.md` — Non-negotiable rules, tool priority, forbidden operations, Serena/Scope/RTK/claude-mem, language-specific basics, linting, communication style, security (UNIVERSAL across all projects)
- This file (`/flext/AGENTS.md`) — Python 3.13+, Pydantic v2 governance, MRO namespace law, 34-project architecture, c/t/p/m/u centralization, import discipline (FLEXT-only)
- `~/.claude/CLAUDE.md` — Developer profile, GSD, Code Simplifier, Superpowers, claude-mem (UNIVERSAL)
- `/flext/CLAUDE.md` — Load order for FLEXT skills, namespace checklist, maintenance (FLEXT pointer-only, <50 lines)

---

## §0 QUICKSTART (15s)

Skip one item and the task is invalid.

### §0.000 FAST KILL CARD (READ IN 10s)

If this card conflicts with any longer text below, this card wins.

1. Run `qlty` first; one offender only.
2. If offender is stale, rerun `qlty` immediately.
3. Search canonical origin (`u.*`, `m.*`, parent, existing enum/model`) before any new code.
4. New helper/proxy/wrapper/carrier model/widened kwargs without zero-origin proof is invalid.
5. Single-caller private helper must be inlined and deleted.
6. True option bag -> one `model_validate(kwargs)` at owner origin; fixed-shape API -> explicit params + one packed `model_validate({...})`.
7. Delete custom code with `model_copy(update=...)`, cached `TypeAdapter`, `Annotated`, validators, `computed_field`, `Discriminator`, `RootModel`, `TypeIs`, or `match/case` before writing anything new.
8. No loose module-scope constants/objects; move them into the existing owner class now.
9. No manual kwargs normalization, no magic literals when `c.*` exists, no raw gate output.
10. First edit -> `ruff` then `pyrefly`; cycle stays open until both are green.
11. Refactor with non-negative LOC delta or skipped propagation is invalid.

### §0.00R START GRID (READ IN 10s)

1. `qlty` first. One offender only. If the selection is stale, rerun `qlty` immediately.
2. Generated / auto-generated files are invalid smell lanes unless the generator is the target.
3. Origin before helper. Search `u.*`, `m.*`, parent methods, and existing utilities before writing anything.
4. Single-caller private helper = inline delete. New helper/proxy/wrapper without zero-origin proof = invalid patch.
5. True option bag -> one `model_validate(kwargs)`. Fixed-shape API -> explicit typed params + one packed `model_validate({...})`.
6. Prefer deletion primitives first: `model_copy(update=...)`, cached `TypeAdapter`, `Annotated`, validators, `computed_field`, `Discriminator`, `RootModel`, `TypeIs`, `match/case`.
7. No manual kwargs normalization, no `Any`/`object`/`cast`, no magic literals when `c.*` exists.
8. No loose module-scope constants/objects; centralize them under the correct owner class in the same cycle.
9. First edit => `ruff` then `pyrefly` immediately.
10. Net LOC must be negative. Moving the smell, skipping propagation, or adding a helper first is invalid.
11. Repeat the same failure twice -> stop and rewrite the smallest clean block.
12. No raw gate output + exit code => no done claim.

Default failure memory: helper-first invention. Correct route: search origin -> delete duplicate -> let Pydantic own the payload -> gate immediately.

### §0.00S BRUTAL SELF-CRITIQUE (MANDATORY BEFORE FIRST PATCH)

Write one short paragraph with exactly these four facts, or do not patch:

1. Recurring failure risk in this cycle.
2. Exact stop-rule that blocks it.
3. Exact owner origin being reused, or explicit proof that no origin exists.
4. Exact native primitive replacing the custom code + exact propagation command + first gate command.

### §0.00H EXECUTION HEADER (copy/paste before first edit)

`OFFENDER=<file:line>; PRIMITIVE=<Annotated|validator|TypeAdapter|Discriminator|RootModel|TypeIs|match>; PROPAGATE=<scope/sg cmd>; GATE1=ruff <file>; GATE2=pyrefly <file>; TEST=<pytest target>`

Missing one field above = no patch.

### §0.00 ULTRA START CARD (10s, EXECUTE OR STOP)

Hard line: no helper/proxy/alias, no zero-test pytest, no ambiguous evidence, no second repeat of the same failure.

1. `qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json`
2. Pick one offender (`src/` first) and map full caller chain (`scope`/`sg`/`rg`).
3. Reuse SSOT primitive or delete duplicate; no new helper/wrapper/alias.
4. Use the canonical origin method/class directly; if a centralized method already exists, duplicating it locally with a new helper is invalid.
5. Replace custom code with native ladder first: `Annotated` -> validators -> `computed_field` -> cached `TypeAdapter` -> `Discriminator` -> `RootModel` -> `TypeIs` -> `match/case`.
6. First edit must be followed by `ruff` then `pyrefly` on touched file.
7. Shared contract changed => propagate now with `sg` and re-check callers.
8. Refactor with non-negative LOC delta is invalid.
9. No raw gate output + exit code => no done claim.
10. Repeat same failure twice => stop patching and rewrite minimal clean block.
11. No new inline magic strings/numbers; new runtime literals must come from `c.*` unless they are one-off boundary messages.
12. Moving a smell from the selected file to a sibling file is an invalid cycle; decomposition must reduce or keep total selected-smell family count in-lane.
13. Real `**kwargs` payloads in runtime code must be validated by canonical Pydantic paths (`model_validate`, typed input models, or `TypeAdapter`); manual key/type validation loops are invalid.
13. **`**kwargs: T` always produces `dict[str, T]` — never annotate internal helpers with `Mapping[str, T]` or scalar `T` for these; use `dict[str, T]` directly.**
13.1 **Fixed-shape public/orchestrator signatures MUST stay explicit and typed; pack once into `Model.model_validate({...})` at the origin. Do not widen fixed parameters into `**kwargs` just to hide a smell.**
14. **`metadata or ModelClass(field=default)` is the Pydantic 2 canonical "default model" pattern — never write `ModelClass(field=metadata.field if metadata is not None else default)` multi-branch constructors.**
15. **Before deleting any helper, verify the type error is not a wrong annotation in the helper — wrong annotation must be fixed, not fixed by deleting the helper.**
16. **`model_copy(update={...})` is the canonical Pydantic 2 mutation — never construct a new model from scratch when you already have a base instance to copy from.**
17. **Never write `if x is None: super()(without_x) else: super()(with_x)` for optional kwargs — Python accepts `kwarg=None` and the parent's `Optional` type handles it.**
18. **If you are about to add a helper, first prove two negatives: no existing origin method/class covers it, and no Pydantic 2 / Python 3.13 primitive deletes it. Missing either proof = invalid patch.**
19. **Manual kwargs normalization (`pop`, `get`, `setdefault`, key-existence branches, inline coercion loops) is invalid when one typed input model or `TypeAdapter` can validate the payload once at the origin.**
20. **If the touched block repeats the same string/number twice and no `c.*` constant exists, centralize it in the same cycle. Leaving repeated inline literals behind is incomplete work.**
21. **Addition-heavy refactor is suspect by default: if the first pass adds more than it deletes, stop and re-search for the canonical origin or native primitive before continuing.**

### §0.00B RECURRING FAILURE EXTERMINATION (MANDATORY — read before EVERY patch)

These patterns recur every session. Kill on sight — no debate, no deferral.

**A. Duplicate helpers instead of canonical origin — ABOMINABLE**
> Symptom: new local `def _do_x(...)` when `u.X.do_x(...)` or `FlextBaseClass.do_x(...)` already exists.
> Fix: `grep -rn "def <verb>" flext-core/src flext-cli/src flext-infra/src --include='*.py'` BEFORE writing anything. Zero hits only = allowed to write.

**B. Multi-return branches instead of `match/case` type dispatch — FORBIDDEN**
> Symptom: `if isinstance(x, A): return ...; if isinstance(x, B): return ...; if x is None: return ...` (≥3 returns on type checks).
> Fix: `match x: case A(): ...; case B(): ...; case _: ...` — one return at end. Pydantic discriminated union where applicable.

**C. Repeated model construction instead of one sentinel + `model_copy` — FORBIDDEN**
> Symptom: `m.X(field="", meta=default)` written 2+ times in same function.
> Fix: `_EMPTY = m.X(field="", meta=default)` class/module-level sentinel; branches use `_EMPTY` or `_EMPTY.model_copy(update={...})`.

**D. Manual validation instead of Pydantic auto-coercion — FORBIDDEN**
> Symptom: `if not isinstance(x, str): raise ...; x = str(x).strip()` before constructing a model.
> Fix: Put coercion in `Annotated[T, BeforeValidator(fn)]` field definition; caller passes raw data to `Model.model_validate(data)` or `TypeAdapter[T].validate_python(data)` — Pydantic does the rest.

**E. Inline magic strings/numbers — FORBIDDEN**
> Symptom: `return ""`, `count = 6`, `rule = "qlty:function-parameters"` hardcoded in logic.
> Fix: Move to `c.*` `StrEnum`/`Literal`/`Final`. Use `c.X.EMPTY_DN`, not `""`. No new inline literal in patched block.

**F. Pass-through wrapper with same signature — ABOMINABLE (§3.5)**
> Symptom: `def old_name(a, b, c): return new_name(a, b, c)`.
> Fix: Delete `old_name`; update all callers to `new_name` via `sg`. Same cycle, no deferral.

**G. `del param` inside function body — DEAD API, remove now**
> Symptom: `def f(a, b, unused): del unused; ...`.
> Fix: Remove `unused` from signature; propagate removal to all callers. Track cascade: removal may make caller params dead too.

**H. `kwargs` passed straight into `Model(**kwargs)` without schema — WEAK**
> Fix: Use `Model.model_validate(kwargs)` — raises `ValidationError` with full field diagnostics instead of silent `TypeError`. Always prefer `model_validate` at system boundaries.

**I. `e.BaseError` subclass with custom `__init__` building context manually — ABOMINABLE**
> Symptom: subclass defines `_build_context()`, `InitOptions(BaseModel)`, manual `self.attr=`, manual `error_code or "..."`.
> Fix: Set `_params_cls = MyParamsModel`, `_param_keys = frozenset({...})`, `_default_error_code = "..."` as ClassVars. The base `__init__` validates kwargs, assigns attrs, builds context. Single `super().__init__(msg, merged_kwargs=kwargs)` call. Delete everything else.

**J. New model created to fix `function-parameters` smell — ABOMINABLE**
> Symptom: smell is 5+ params → agent creates `ConnectionParams`, `HealthCheckParams`, `JsonWriteOptions`, `RopeEditContext` etc. Net LOC is zero or positive.
> Fix: (1) Single caller? → inline the function body, delete the helper. (2) `**kwargs` + existing `XSettings.model_validate(kwargs)`? → use it, zero new model. (3) Caller always co-locates `(a, b)` already paired upstream? → dataclass only if ≥8× LOC eliminated, otherwise skip and pick another offender. NEVER add a model just to make the parameter count drop below threshold.

### §0.0 NO-EXCUSES START CARD (READ FIRST, 20s)

1. Run `qlty smells` first. No smell run, no edit.
2. Pick exactly one offender in `src/` and close full caller chain.
3. Reuse SSOT first; if duplicate exists, delete local custom code.
4. Exhaust Pydantic2/Python3.13 deletion ladder before writing anything custom.
5. First edit must be followed immediately by `ruff` then `pyrefly`.
6. Shared contract changed -> propagate now with `sg` + caller audit.
7. Net LOC for refactor must be negative.
8. No raw gate output, no done claim.
9. If you repeat the same failure twice, stop patching and rewrite minimal clean block.
10. If you cannot name the replacing primitive (`Annotated`, validator, `TypeAdapter`, `RootModel`, `Discriminator`, `TypeIs`, `match/case`), do not start.
11. If `/tmp/qlty_smells-tests.json` is empty/corrupted, rerun smells immediately; stale SARIF is invalid evidence.
12. One cycle only counts when it has: one offender, caller audit, one gate run, and command output evidence.
13. When file lives in a sub-project, run status/gates in that sub-project (`git -C <project> status`, then project-local checks). Root-only green is invalid.
14. Ralph-style iterative work must update `ralph-progress.md` in the same cycle; no progress update means cycle incomplete.
15. NEVER drop a symbol/import assuming it became unused. `grep -nE '\b<name>\b' <file>` first. Drop only when the count is 1 (the import line itself).
16. Pydantic decorators (`@field_serializer`, `@model_validator`, `@field_validator`, `@computed_field`) on classes that DO NOT inherit `BaseModel` are INERT scaffolding. Delete the whole method, not just the decorator.
17. NEVER add a new private helper method (even on a base class) until you `grep -rn "def <verb>" flext-core/src flext-cli/src flext-infra/src` and confirm no existing canonical method covers it. Dedup MUST consume existing centralized origins (`u.*`, `c.*`, `m.*`, parent-class methods). Adding a helper is a LAST resort.
18. Wrong import origin that re-enters a lazy facade is an INVALID patch. In owner code, import directly from the owning source when facade reuse would recurse; in consumers, use only the public facade. If you cannot name the owner, stop and search first.
19. For `**kwargs` payloads, manual key/type validation is INVALID when a canonical Pydantic model can `model_validate(...)` the payload at the origin method.
19. No new magic literals in touched blocks: if a same-meaning token/value already exists in `c.*`, using inline string/number is INVALID. Reuse canonical constants or stop and centralize first.
20. True option-bag `**kwargs` in public/orchestrator methods must be validated once at the owner origin through a typed Pydantic contract (`Model.model_validate(kwargs)` or cached `TypeAdapter`). Fixed-shape signatures stay explicit and validate one packed payload via `Model.model_validate({...})`. Manual inline key/type checks and inplace kwargs mutation are INVALID.
21. **`e.BaseError` subclasses: use `_params_cls` + `_param_keys` + `_default_error_code` ClassVars. NEVER add nested `InitOptions`/`_XxxContextMixin`/`_build_context` — the base hook validates kwargs, builds context, and assigns attrs automatically. Writing a local context builder when `_params_cls` already handles it is §3.5 ABOMINABLE.**
22. NEVER write `if isinstance(x, Model): self.x = x.model_copy(update=overrides)` else parse-branches. Canonical Pydantic 2: `Model.model_validate({**x.model_dump() if isinstance(x, Model) else (x or {}), **overrides})` — ONE call, validator owns all type coercion + defaulting + extra-key rejection. Manual inplace branches before parse are INVALID.

### §0.Z BRUTAL SELF-CRITIQUE (MANDATORY BEFORE FIRST PATCH)

Before editing, state exactly this (one short paragraph):

1. Recurring failure risk in this cycle.
2. Exact stop-rule that blocks it.
3. Exact Pydantic 2 / Python 3.13 primitive replacing custom code.
4. Exact propagation command + exact green-gate command.

Missing one item = do not patch.

Failure memory: the defect is helper-first invention. Start by deletion and origin reuse, not by creating local logic.

### §0.A AUTOPSY CARD (MUST RUN BEFORE FIRST EDIT)

Failures that keep repeating and the mandatory counter-rule:

1. Syntax break after patch: STOP and restore a compilable minimal state immediately.
2. New helper/wrapper/proxy/compat alias: DELETE in the same cycle.
3. Contract changed without caller propagation: task stays OPEN.
4. Selective validation hiding red gates: result INVALID.
5. Refactor without negative LOC: result INVALID.
6. SSOT primitive exists but local duplicate was written: DELETE duplicate now.
7. Same failure repeated twice in one lane: STOP patching and rewrite the smallest clean version.
8. Pytest command ran with zero selected tests: result INVALID (no behavior evidence).

Hard floor: no loose declarations outside `c/p/t/m/u`; Pydantic 2 + Python 3.13 are deletion primitives first.

### §0.B CONTEXT LOAD (20s, NO EXCUSES)

Load in this exact order before coding:

1. `AGENTS.md` §0 + touched-path rules skill.
2. One-line blast radius (`scope`/`sg`/`rg`) for edited symbols.
3. First failing smell offender + full caller chain.
4. First gate command to run after edit.
5. One-line statement of last recurring failure and its stop-rule.

If you cannot state these 5 items in one short paragraph, you are not ready to edit.

### §0.C FIRST PARAGRAPH CONTRACT (MANDATORY)

Before first edit, write exactly one short execution paragraph containing:

1. Offender file:line and why it is selected now.
2. Which SSOT primitive will replace duplicate/custom code.
3. First post-edit gate command.
4. Caller-propagation command.

Missing any item above = INVALID start.

## §0 STOP CARD (read in 60s before ANY edit)

FLEXT-only. Read §0 first. Ignore excuses. Universal rules → `~/.claude/AGENTS.md`. Detail rules → §1–§10.

### §0.0 EXECUTION FLOW (every task, every edit)

```
SMELL → SEARCH → REUSE → DELETE → P2+3.13 REPLACE → MRO COLLAPSE → PROPAGATE → VALIDATE → COMMIT
```

Rules:

- Net LOC delta MUST be negative.
- New code only with ≥8× LOC eliminated.
- One offender per cycle.
- No skipped blast radius.
- No skipped post-edit gate.
- No custom helper before the native deletion ladder fails.

### §0.1 PYDANTIC 2 + PYTHON 3.13 FLOOR — exhaust before writing ANY custom code

Deletion ladder, in order:

`Annotated[T, Field(...)]` -> `BeforeValidator` / `AfterValidator` -> `field_validator` -> `model_validator` -> `computed_field` -> `model_dump` / `model_validate(_json)` -> cached `TypeAdapter` -> `Discriminator("kind")` -> `RootModel` -> `PrivateAttr` -> PEP 695 generics / aliases -> `Self` -> `@override` / `@final` -> `TypeIs[T]` -> `match/case` -> `cached_property` -> frozen/slots dataclass.

Custom equivalent = AUTOMATIC DELETION (§3.1.PYDANTIC-V2-NATIVE table).

### §0.2 ABSOLUTE BANS (any one = STOP, REVERT, RE-PLAN)

`Any` / bare `object` / `cast()` outside flext-core/result.py · `model_rebuild()` · pass-through wrappers (`def x(): return y()`) · pass-through constructors (`__init__` only forwarding parent args) · compat aliases (`OldX = NewX`) · manual/inplace kwargs validation or normalization chains when `Model.model_validate(...)` / `model_copy(update=...)` can replace them · `os.environ`/`os.getenv` in `src/` · bare `except:` · `# type: ignore` / `# pyrefly: ignore` / `# noqa` for SUPPRESSION (root-cause fix only) · `git checkout/reset --hard/stash pop` to discard work · `T | None` without docstring sentence justifying `None` · public `get_*/set_*/is_*` accessors on facade services · loose module-level `def`/`class`/`Final` · direct framework imports of flext-core-abstracted libs (pydantic/structlog/orjson/pyyaml/dependency_injector/returns) in consumers · `model_validate(...).execute()` GOD-pattern dispatchers · sibling duplication of `model_config`/fields/methods.

Also absolutely banned:

- Editing outside explicit user scope after user requested focus correction.
- Mixing `src` and `tests` namespace contracts without explicit migration approval.
- Continuing implementation work after explicit user cancellation/prohibition.

### §0.3 FORBIDDEN RATIONALIZATIONS (task INVALID on first utterance)

| Excuse | Rule |
|---|---|
| "distinct cohesive concern" | Cohesion DESCRIBES, never JUSTIFIES. MRO absorbs all. |
| "collapse would create a monster" | SHIP collapse THEN split via MRO ≤200 LOC. |
| "different signatures" | Unify via widening OR delete descendant. Two defs same name = §3.1 violation. |
| "defensive / safe / pragmatic" | SUPREME LAW = net-LOC-negative. Tests prove correctness; LOC delta proves work. |
| "plan target was a ceiling" | INVERTED. Targets are FLOORS. Ship below floor only with §0.A.2 evidence. |
| "this is too complex / risky" | Then split into ≤30-LOC atomic edits, not skip. |
| "parallel agent's work" | Fix-forward across the boundary if it blocks measurable LOC reduction. |

### §0.4 HARD STOPS (instant, no debate)

- "Done" without raw command output + exit code → INVALID
- First edit without first running `qlty smells` for the active lane → INVALID
- File touched twice same session → INVALID (re-plan)
- Class named without grepping `_models/` → REVERT
- Pass-through `__init__` re-declaring parent fields → DELETE
- `make check` passed but no commit → INCOMPLETE
- Suppression hint instead of structural fix → DELETE hint, fix root cause
- Custom helper/class written before exhausting Pydantic 2 + Python 3.13 → DELETE and re-plan
- Offender fixed locally without caller propagation → INCOMPLETE
- First substantive edit not followed by the cheapest focused executable validation → INVALID
- Smell loop skipped while debt remains → INVALID
- Claims of "done" without naming the exact replaced Pydantic/Python primitive → INVALID

### §0.5 OPTIMIZATION LOOP (continuous improvement)

```bash
qlty smells --all --sarif --include-tests > /tmp/qlty_smells-tests.json
# pick one eligible offender (src/ first; tests/ allowed when selected or coupled to the same flow)
# close the whole usage chain for that offender
# validate immediately
# repeat
```

Hard stop: do NOT claim completion while unresolved `src/` smell offenders remain in the active lane.

Stop condition is strict:

1. The active lane/scope has zero unresolved selected smells.
2. Every selected smell has caller-chain proof + green gates evidence.
3. "Good enough for now" is forbidden while selected smells remain.
4. If the user explicitly requests full-smell cleanup, completion claim is valid only when SARIF total smells is zero (`jq '[.runs[].results[]] | length' /tmp/qlty_smells-tests.json`).

### §0.6 STRUCTURAL RENAME

```bash
sg -p 'OldName' --lang py flext-*/src              # find
sg -p 'OldName' -r 'NewName' --lang py flext-*/src # replace
```
Never grep+manual.

### §0.7 CANONICAL ALIASES (use, never wrap)

`c` Constants · `m` Models · `t` Types · `p` Protocols · `u` Utilities · `r` Result · `h s d e x` operational. Call sites use alias (`m.MyModel`, `c.MY_CONST`), never raw class. Organic MRO paths preserved (`m.TargetOracle.ExecuteResult`); flattening FORBIDDEN. Tests/examples/scripts import via wrapper root (`from tests import c, m, p, t, u`). Facade naming: `src/`→`Flext<Project><Tier>` · `tests/`→`TestsFlext<Project><Tier>` · `examples/`→`ExamplesFlext<Project><Tier>` · `scripts/`→`ScriptsFlext<Project><Tier>`. *Detail*: §2.2, §3.6, §4.

### §0.8 SSOT SEARCH KEYS (grep BEFORE creating)

`cce.get_catalog().{rules,by_id,by_kind}` · `FlextUtilitiesEnforcement.{check,run,run_layer}` · `ube.find_*` (cast/model_rebuild/pass-through/private-probe) · `FlextInfraUtilitiesProtectedEdit.protected_file_edit` · `FlextInfraRefactorSafetyManager.create_pre_transformation_stash` · `r[T]` + `e.fail_*` · `FlextLogger` · `FlextContainer` + `@u.factory` · `FlextSettings` + `@FlextSettings.auto_register("<ns>")` · flext-core JSON/YAML utilities (no direct `orjson`/`pyyaml`/`structlog`/`dependency_injector`/`returns`).

### §0.9 VERIFICATION (BLOCKING for any "done" claim)

Per-touched-file: `ruff check <file>` + `pyrefly check <file>` + relevant `pytest`. Per-PR boundary: `make check` on affected projects. No proxy evidence — only raw command output. *Detail*: §3.8.

---

## §1 Identity

- **Supreme Document**: FLEXT canonical governance file. AGENTS.md defines mandatory law; skills hold detailed implementation guidance.
- **Reviewed**: 2026-04-18.
- **Stack Baseline**: Python 3.13+, Pydantic v2, Ruff, Pyrefly, Pyright, Mypy, Poetry, Make, RTK.
- **Projects**: 34 flext projects in monorepo (`flext-core`, `flext-cli`, `flext-meltano`, etc.).
- **No Shadow Policies**: Agent-specific settings are pointers only. No policy duplication outside this file.
- **Meta-Surface Drift Is Invalid**: Pointer docs, prompts, and meta-skills with duplicated startup law, repeated frontmatter, or stacked mini-cards are governance defects. Collapse them to one pointer plus one operational start card in the same cycle.

## §2 Architecture Law

### 2.1 Dependency Flow & Layers

- **Inward Flow**: Dependency flow is inward only (`L3 -> L2 -> L1 -> L0`). Reverse imports are FORBIDDEN.
- **Layer Breakdown**: `L3` = Orchestration, `L2` = Domain/Infrastructure, `L1` = Foundation/Bridge, `L0` = Contracts.
- **Infrastructure Bridging**: Bridge external infra through runtime/container boundaries, NEVER via direct framework imports.
- **Platform Chains**: `Core -> Cli -> Meltano -> Integration` (orchestration), `Core -> Web -> Api -> Auth` (API layer).

### 2.2 Facades, Namespaces & Naming Patterns

- **One Facade Rule**: Each public facade module defines exactly ONE primary facade class plus ONE canonical alias.
- **Facade Class Naming**: `src/` facades MUST use `Flext<Project><Tier>`. `tests/` facades MUST use `TestsFlext<Project><Tier>`. `examples/` facades MUST use `ExamplesFlext<Project><Tier>`. `scripts/` facades MUST use `ScriptsFlext<Project><Tier>`. Legacy patterns such as `Flext<Project>Test<Tier>`, `FlextTest<Project><Tier>`, and `{Flext<Project>}{Examples|Scripts}<Tier>` are migration debt only and MUST NOT be copied into new work.
- **Private Mixin Naming**: Classes under `models/`, `_utilities/`, `_protocols/`, and similar private trees MUST keep the project prefix and append only the module concern (e.g. `FlextInfraUtilitiesImportNormalizer`, `tk`).
- **Canonical API & Aliases**: Namespace aliases are the STRICT canonical public API surfaces. You must always use them (`m.MyModel`, `c.MY_CONST`), never the direct classes.
  - `m` = Models (`Flext*Models`)
  - `c` = Constants (`Flext*Constants`)
  - `t` = Types (`Flext*Types`)
  - `u` = Utilities (`Flext*Utilities`)
  - `p` = Protocols (`Flext*Protocols`)
  - `h` = Helpers (`Flext*Helpers` - mostly test/infra)
  - `s` = Services (`Flext*Services`)
- **Organic Namespace Access**: Call sites MUST keep the namespace path produced by MRO (`u.Infra.parse_semver`, `c.Tests.ERR_OK_FAILED`, `m.TargetOracle.ExecuteResult`). Facades MUST NOT flatten nested domain-local classes back onto the facade root with class-level alias assignments.
- **Alias Import Sources**: In `src/` code, `c`, `p`, `t`, `m`, `u` come from `flext_core` or the project's own package (MRO-extended). In `tests/`, `examples/`, and `scripts/`, these aliases MUST be imported from the local MRO package: `from tests import c, m, p, t, u`, `from examples import c, m, t`, etc. NEVER import `c`, `p`, `t`, `u` from a sibling project (e.g., `from flext_target_oracle import t` in test code is FORBIDDEN). Operational aliases (`r`, `e`, `h`, `d`, `s`, `x`) come from `flext_core` or the project's extended package.
- **Strict Boundaries**: Domain boundaries are strict (e.g. `oracle-wms != db-oracle`, `ldap != ldif`).
- **Export Discipline**: `__init__.py` files are exports-only. They must ONLY contain type hints, `__all__`, and the native `__getattr__` module-level lazy load strategy. **These files are AUTO-GENERATED**. You must NEVER edit them manually. Run `make gen` to regenerate lazy initialization exports.

### 2.3 MRO Inheritance & Namespace Composition

- **Single Namespaced Classes (Production & Tests)**: For both production and test infrastructure, you must create exactly ONE local namespaced class per tier (models, constants, helpers, etc.). All domain logic, constants, and methods MUST reside inside this single class.
- **Single Root Nested Namespace**: A `src/` facade root defines exactly one local domain namespace class (e.g. `class Infra:`, `class Tests:`). A `tests/` facade root defines exactly one local project-domain namespace whose test-only branch lives under `.Tests`. No other local top-level nested namespace classes are permitted in the facade.
- **The MRO Cascade & Exhaustive Composition**: Cross-project composition MUST use inheritance via MRO symmetrically across all components. Furthermore, within a project, a top-level facade class MUST strictly compose ALL of its domain-specific subclasses.
  *(Example: `class FlextCoreModels(FlextCoreBaseModels, FlextCoreCQRSModels, FlextCoreSettingsModels): pass` and similarly for `FlextCoreUtilities` composing all `_utilities` subclasses. Loose disconnected subclasses are FORBIDDEN).*
- **Subdirectory Composition Only via MRO**: Private files in `models/`, `_utilities/`, `_protocols/`, and similar trees define mixin classes only. The public facade composes them directly in its inheritance list. Manual flat wrapper nesting such as `class Docker(tk): pass` inside the facade namespace is STRICTLY FORBIDDEN.
- **Internal Namespaces & Elimination of Loose Objects**: Do not duplicate parent variables. Loose module-level objects or functions outside this class are STRICTLY FORBIDDEN. They must be absorbed into the namespace class as attributes/methods or consumed directly from base classes.
- **Integration Projects** (`tap|target|dbt`): Composed of one platform and one domain via inheritance (e.g., `class FlextTapLdapProtocols(FlextMeltanoProtocols, FlextLdapProtocols): pass`).
- **Naming & Location Patterns**: Classes must be placed in specific locations (e.g., `models.py` or `models/`) and follow the `Flext<Role><Domain><Facade>` pattern (e.g. `FlextCoreModels`, `FlextTestInfraHelpers`, `FlextTapLdapProtocols`). Test classes must also match the domain they are testing. The integration class name MUST NOT contain the "Meltano" prefix.
- **Test Hierarchy Strictness**: In tests, the MRO hierarchy operates in two axes: test tools + domain under test. The test class MUST compose `FlextTests<Tier>` with the project's own `Flext<Project><Tier>` to gain both testing utilities and the full application context transparently.

### 2.4 Governance Anti-Patterns

- **No Private Imports**: Public contracts MUST be consumed from package facades and root exports only.
- **No Backward-Compat Aliases**: Backward-compatibility alias layers (e.g. `LegacyX = NewX`) and namespace shadowing are FORBIDDEN. You must NEVER re-assign parent aliases.
- **No Facade Mirrors**: Public facade modules (e.g. `core.py`, `client.py`) must NEVER duplicate code from `_utilities/` or `models/` internals. Implementation lives in `_utilities/`; the public module is a thin re-export stub:

  ```text
  # Re-export stub structure (uses placeholders — not executable Python):
  # 1. """Re-export from internal module."""
  # 2. from __future__ import annotations
  # 3. from <package>._utilities.<module> import <Symbol1>, <Symbol2>
  # 4. __all__: list[str] = ["Symbol1", "Symbol2"]
  ```

  If `qlty smells` reports `identical-code` between a public file and its `_utilities/` counterpart, replace the public file with a re-export immediately.

*For full MRO matrix, architecture layers, and anti-patterns logic, consult skills:* `flext-mro-namespace-rules`, `flext-architecture-layers`, `flext-patterns`, `rules-flext-core`, `rules-src`.

### 2.5 Service Facade Pattern (`api.py` + `base.py` + `services/`)

Projects that provide a main service class (e.g., FlextCli, FlextLdif, FlextObservability) MUST follow the **MRO service facade pattern**:

- **`api.py`** — The single entry-point class `Flext<Project>` composing only the service mixins whose public behavior is reused directly via MRO. Only infrastructure (factory methods, Constants, model aliases, strict runtime DSL alias support) is defined locally. Services that require dedicated construction state but are only orchestrated once MUST be instantiated from local facade methods instead of being inherited only to wrap them again.
- **`base.py`** — `Flext<Project>ServiceBase(s[T], ABC)` providing typed settings access. All mixins inherit from this base.
- **`services/`** — One file per concern, one mixin class per file. Each mixin provides a single domain responsibility (e.g., tracing, metrics, health). Auto-generated `__init__.py` via `make gen`.

```
flext-<project>/src/flext_<project>/
├── api.py                   # Flext<Project> MRO facade
├── base.py                  # Flext<Project>ServiceBase
├── constants.py             # c = Flext<Project>Constants
├── models.py                # m = Flext<Project>Models
├── protocols.py             # p = Flext<Project>Protocols
├── typings.py               # t = Flext<Project>Types
├── utilities.py             # u = Flext<Project>Utilities
├── settings.py              # Flext<Project>Settings
└── services/
    ├── __init__.py           # AUTO-GENERATED
    ├── <concern_a>.py        # Flext<Project><ConcernA>Mixin
    ├── <concern_b>.py        # Flext<Project><ConcernB>Mixin
    └── ...
```

```text
# api.py — MRO facade (structural pattern):
# class Flext<Project>(
#     Flext<Project><ConcernA>Mixin,
#     Flext<Project><ConcernB>Mixin,
#     ...all service mixins...
#     Flext<Project>ServiceBase,
# ):
#     """All domain methods come from mixins via MRO."""
```

*See `flext-patterns` skill for valid reference implementations.*

```text
# base.py — typed service base (structural pattern):
# class Flext<Project>ServiceBase(s, ABC):
#     @property
#     @override
#     def settings(self) -> Flext<Project>Settings:
#         return FlextSettings.fetch_global().fetch_namespace(
#             "<namespace>", Flext<Project>Settings
#         )
```

*Reference: `flext-cli/src/flext_cli/base.py`.*

**Rules**:

1. **No standalone service classes** — every service class MUST be a mixin on the facade.
2. **No re-export stubs for services** — access is via the facade (`FlextObservability().method()`), not individual class import.
3. **One concern per mixin** — each `services/*.py` file defines ONE mixin class.
4. **MRO field conflicts** — the facade MUST declare shared fields (`logger`, `_container`) to shadow inherited duplicates.
5. **No public accessor prefixes on service facades** — public `get_*`, `set_*`, and `is_*` methods/properties are FORBIDDEN. Local deterministic derivation MUST become fields or `@u.computed_field`; external boundary reads MUST use domain verbs such as `fetch_*` or `resolve_*`; state mutation MUST use validated model assignment, `model_copy(update=...)`, or a domain verb such as `configure`, `apply`, or `update`.
6. **Service runtime state is centralized** — each service concern MUST flow through one central `m.<Domain>.*State` or `m.<Domain>.*Status` model instead of spreading round-trips through many small carrier models, dict conversions, and ad-hoc type narrowing.
7. **Runtime DSL aliases are eager instances** — the module runtime alias MUST be `alias = Flext<Project>()`, never `alias = Flext<Project>`. When migration compatibility requires `alias(...)`, implement `__call__` on the facade as a typed factory and keep all direct behavior available on the eager alias itself.
8. **Do not inherit stateful services just to re-wrap them** — if a service has its own constructor/state and the facade only exposes a single orchestration verb around it, keep that verb local in `api.py` and instantiate the concrete service there.

**Reference implementations**: `flext-cli/src/flext_cli/`, `flext-ldif/src/flext_ldif/`, `flext-observability/src/flext_observability/`.

### 2.6 Settings Law

- **Mandatory Inheritance**: ALL settings classes MUST inherit `FlextSettings`. Using `m.Value`, `BaseSettings`, `BaseModel`, or custom singleton patterns for configuration is FORBIDDEN.
- **ConfigDict Required**: Every settings class MUST define `model_config = ConfigDict(env_prefix="FLEXT_<PROJECT>_", extra="ignore")`.
- **Env Prefix Convention**: `FLEXT_` (core), `FLEXT_CLI_` (cli), `FLEXT_MELTANO_` (meltano), `FLEXT_API_` (api), `FLEXT_AUTH_` (auth), `ORACLE_` (db-oracle), `FLEXT_<ROLE>_<DOMAIN>_` (integration projects).
- **Constants as Defaults**: ALL field defaults MUST come from `c.*` constants. Hardcoded strings, numbers, or booleans as defaults are FORBIDDEN.
- **No os.environ Access**: `os.environ`, `os.getenv`, `environ.get()` in `src/` code is PROHIBITED. Use FlextSettings env resolution or `c.*` constants. Tests are exempt.
- **Singleton via Base**: Use `FlextSettings.__new__()` singleton. Custom `_global_instance`, manual locks, or class-level instance caches are FORBIDDEN.
- **Namespace Registration**: Use `@FlextSettings.auto_register("<namespace>")` for namespace access via `FlextSettings.get_namespace()`.
- **MRO Composition**: Integration projects (tap/target/dbt) MUST use dual-inheritance for settings, same as models: `FlextTargetOracleSettings(FlextMeltanoSettings, FlextDbOracleSettings)`.
- **Auto-MRO Env Sources**: `settings_customise_sources` in FlextSettings base auto-resolves parent env prefixes from MRO. Leaf class env_prefix takes priority, parent prefixes are fallbacks.

> **ENFORCE-042** — Settings classes missing `FlextSettings` base or wrong `env_prefix` are detected at runtime by `FlextUtilitiesBeartypeEngine.check_settings_inheritance` (dispatched via `c.ENFORCEMENT_RULES["settings_inheritance"]`).

### 2.7 Library Abstraction Boundaries

- **Mandatory Abstraction Enforcement**: Libraries abstracted by any flext project (dependency_injector, structlog, rich, typer, tomlib, rope, etc.) MUST NOT be used directly outside that project's `src/` domain.
- **Scope**: Applies to all external usage (other projects' `src/`, `tests/`, `examples/`, `scripts/`, typings, constants, annotations).
- **Access Pattern**: Always use public abstractions from the originating library: `m.*` (models), `c.*` (constants), `t.*` (types), `u.*` (utilities), `p.*` (protocols), `r[T]` (result container).
- **Cross-Project Abstraction**: If project A abstracts pydantic, project B must access pydantic through A's public contracts (`m.`, `c.`, `t.`, etc.), never via direct `from pydantic import ...`.
- **No Bare Framework Imports in Consumers**: `from pydantic import ...`, `from dependency_injector import ...`, `from structlog import ...` in project code outside flext-core are FORBIDDEN if the framework is abstracted by flext-core.
- **Testing Exemption**: In test code under `tests/`, use local test façades and helpers; if direct third-party imports are unavoidable for test scaffolding, document the exception with a technical justification comment.
- **No Example/Script Exemption**: `examples/` and `scripts/` are NOT exempt from abstraction boundaries. Direct imports of abstracted libraries are forbidden there unless the code lives inside the owning abstraction project `src/` domain.
- **Core Abstraction Inventory**: flext-core abstracts: pydantic v2, dependency_injector, structlog, returns (`r[T]`), orjson, pyyaml, and foundational contracts. All other projects must use flext-core abstractions for these.
- **Enforcement**: Use `ruff` with import rules (e.g., flake8-noqa, import-order rules) and grep audits to detect violations. Suppress only with documented technical justification.

## §3 Code Law

### 3.1 Architecture & Code Structure

- **MVI 200-LINE CAP (SUPREME LAW)** module, class, method, or function >200 **code lines** is a violation. Line count is measured via `tokei` (logical LOC only — blank lines, comments, and docstrings are excluded from the count). Refactor immediately using strict OO composition and canonical MRO architecture. Decompose into explicit contracts and reusable domain components—never use compression hacks. **FORBIDDEN approaches to meet the cap**: removing blank lines, removing or compressing docstrings, style/formatting changes that reduce line count, and arbitrary code splits without domain decomposition. Only genuine OO decomposition via MRO inheritance, facade extraction to `models/`/`_utilities/` subdirectories, and domain responsibility separation are valid.
  - **VALID code reduction** (actively encouraged): deleting dead/unused code, removing unnecessary helpers and pass-through wrappers (`def old(): return new()`), removing proxy functions/classes, removing backward-compat aliases (`LegacyX = NewX`), and replacing inline composed type annotations (`str | t.Numeric`) with canonical `t.*` contracts from `typings.py`. These eliminate real architectural violations and are the preferred first step before OO decomposition.
- **Pydantic v2 Mastery**: Every class MUST extend Pydantic v2 `BaseModel` (or FLEXT base models) via MRO. Fully utilize `m.Field()`, `model_config: ClassVar[m.ConfigDict] = m.ConfigDict(...)`, `u.PrivateAttr()`, and built-in constraints. Standalone `*Settings` classes, unnecessary `@property`, manual `self._x` assignments, line-reduction wrappers, and public `get_*`/`set_*`/`is_*` accessors are FORBIDDEN. Direct `from pydantic import ...` in consumer projects is BANNED — every Pydantic construct flows through the canonical `m.*` / `u.*` aliases from `flext_core` (or the project's MRO-extended package). The `FlextUtilitiesPydantic as up` / `FlextModelsPydantic as mp` internal aliases exist ONLY inside `flext-core/src/flext_core/_*` to break `c/t/p/m/u` bootstrap cycles — they are NOT consumer-facing. See `pydantic-v2-patterns` §Facade-Only.
- **Accessor Naming Law**: Values already present in object state or derived locally MUST be exposed as fields or `@u.computed_field`; mutations MUST occur through validated model state or a domain verb; boolean outcomes/statuses MUST use noun/adjective names such as `success`, `failure`, `expired`, `configured`, `connected`, or `healthy`.
- **MRO Inheritance Hierarchy**: Domain logic must reside in a single nested class hierarchy. Subprojects inherit from the parent project's facade class to cascade namespaces. Loose functions or standalone classes without MRO lineage are FORBIDDEN. They MUST be absorbed into the namespace classes or used via existing base classes.
- **Utility & Helper Generalization (`u.*`)**: All shared helpers MUST strictly flow through the `u.*` utilities namespace. Do not duplicate logic. Use and enhance the lowest-level function available, systematically generalizing existing code rather than creating new redundant functions.
- **Centralize Polymorphic Code**: Dismantle polymorphic functions branching on type unions. Use centralized Pydantic v2 models with discriminated unions and validation.
- **Centralized Runtime Contracts**: Inputs, outputs, runtime state, and status snapshots MUST flow through central `m.*` models. Eliminate avoidable dict round-trips, ad-hoc conversion helpers, and non-essential type narrowing between service boundaries.
- **Sibling-Config Duplication**: ≥2 classes sharing identical `model_config = ConfigDict(...)`, fields, or methods MUST extract an MRO base/mixin in the lowest existing facade. New base class allowed only with proven ≥8× LOC elimination stated in commit message.
- **Pydantic 2 + Python 3.13 IDIOM MANDATE**: Custom imperative code is GUILTY UNTIL PROVEN INNOCENT. Before declaring any custom function/class/dispatcher/validator "legitimate", confirm NO row below replaces it. Any row that applies → REWRITE using the idiom (declarative, type-checked, shorter). Custom re-implementation of a row's idiomatic replacement = §3.5 Legacy Extermination violation.

  | Custom pattern (FORBIDDEN if replaceable) | Idiomatic replacement (Pydantic v2 / PEP) |
  |---|---|
  | `__init__` body computing derived fields | `model_post_init(self, __context)` OR `@model_validator(mode="after")` returning `self` |
  | `def get_x(self): return self._x` getter | direct field access OR `@u.computed_field` (auto-serialized to JSON) |
  | `def set_x(self, v): self._x = v` setter | direct assignment + `model_config = ConfigDict(validate_assignment=True)` |
  | `if/elif` chain over `kind`/`type` discriminator | `Annotated[Union[A, B, C], Field(discriminator="kind")]` (Pydantic auto-dispatches) |
  | `match k: case "a": …` over Pydantic-modelled discriminator | same as above — let Pydantic do it, no `match` boilerplate |
  | `cast(X, value)` after `isinstance(value, X)` | `TypeIs[X]`-narrowing predicate (PEP 742, bidirectional) |
  | `__getattribute__` override | `PrivateAttr(default_factory=…)` for tracked private state |
  | Mutable default in `__init__` | `Field(default_factory=…)` |
  | `Annotated[str, Field(min_length=1)]` repeated ≥3× | PEP 695 alias `type NonEmptyStr = Annotated[str, Field(min_length=1)]` in `_typings/` |
  | Custom JSON parsing with manual schema | `model_validate_json` |
  | `try: int(s); return True; except: return False` | `TypeAdapter(int).validate_python(s, strict=True)` (catch `ValidationError`) |
  | Custom dispatch table `{"a": fn_a, "b": fn_b}` | `singledispatch` / `singledispatchmethod` |
  | `@property` returning derived data | `@u.computed_field` (auto-serialized) |
  | `Generic[T]` with no useful default | PEP 696 `TypeVar("T", default=…)` |
  | Forgotten override → silent drift | PEP 698 `@override` decorator (mandatory on every overriding method) |
  | `class Sealed(BaseModel): pass` doc-only seal | `@final` decorator |
  | `if isinstance(x, dict): … elif isinstance(x, Mapping): …` | `match x: case Mapping(): …` (PEP 634 class patterns) |
  | One-shot expensive computation per instance | `functools.cached_property` |
  | Catching multi-exception in TaskGroup / parallel awaits | `except*` (PEP 654) |
  | `def fluent(self) -> "MyClass":` | `def fluent(self) -> Self:` (PEP 673) |
  | `BaseModel` accepting JSON-shaped scalars only | `RootModel[t.JsonValue]` (no boilerplate field) |
  | Custom `@field_validator` doing single coercion | `Annotated[T, AfterValidator(coerce_fn)]` (declarative composition) |
  | Custom `@field_validator` doing single coercion BEFORE validation | `Annotated[T, BeforeValidator(coerce_fn)]` |
  | Custom `__eq__` over field bag | `model_config = ConfigDict(frozen=True)` (Pydantic auto-equality) |
  | `Optional[X] = None` + null-check loops | `X \| <SkipMarker>` discriminated union OR remove the `None` branch if dead |
  | `Union[ModelA, ModelB]` without discriminator | `Annotated[Union[ModelA, ModelB], Field(discriminator="kind")]` + `kind: Literal["a"]` per variant |
  | `to_dict()` / `to_json()` wrapper methods | `model_dump()` / `model_dump_json()` directly |
  | `from_dict(d)` / `from_json(s)` factory methods | `Model.model_validate(d)` / `Model.model_validate_json(s)` directly |
  | Manual schema dict construction | `Model.model_json_schema()` |
  | `dataclass` with validation | Pydantic `BaseModel` (validation built-in) |
  | `dataclass` without validation | `@dataclass(slots=True, kw_only=True, frozen=True)` (when truly no validation) |

- **None-Audit Mandate**: every `T | None` parameter or return MUST justify `None` semantics in one short sentence stating the **business condition** that produces `None`. Anti-patterns and required fixes:

  | Anti-pattern | Real semantic | Fix |
  |---|---|---|
  | `def helper(x: A \| None = None)` ("use default if None") | The default IS the value | `Field(default_factory=...)` or two overloads |
  | `def lookup(...) -> T \| None` ("not found = None") | "Not found" is a failure mode | `r[T].fail("not found")` (Result monad) |
  | `def maybe_compute(...) -> T \| None` ("not yet computed") | Lazy computation | `@u.computed_field @property` (cache + schema) |
  | `Optional[X]` chains in signatures (`a: A \| None, b: B \| None`) | Caller is dispatching | discriminated union, single param |
  | `if value is None: return default` boilerplate at start of function | Default-handling | `Field(default=...)` on the model where `value` lives |
  | `return None` to indicate "skip" | Caller-side branching | `r[T].ok(...)` vs `r[T].fail("skip")`, or yield from generator |

  Helper signatures with `T | None` lacking a docstring sentence explaining `None` semantics → AUTOMATIC REWORK.

- **Cached-Adapter Mandate**: every recurring parse target gets ONE module-level/class-level `_X_ADAPTER: ClassVar[TypeAdapter[X]] = TypeAdapter(X)` constructed once, reused forever. Calling `TypeAdapter(X)` per invocation = §3.5 Legacy Extermination violation (re-parses schema each call).

- **KWARGS-Model Mandate**: dynamic option bags MUST be validated exactly once at the origin method via a Pydantic v2 model (`OptionsModel.model_validate(kwargs)`). Fixed-shape signatures MUST stay explicit and typed, then pack once into `OptionsModel.model_validate({...})` at the owner origin. Widening a fixed signature to `**kwargs` to hide parameter count is FORBIDDEN. Manual `if key in kwargs`, manual type checks, and in-place dict mutation chains are FORBIDDEN except at unavoidable external boundaries.

- **MRO-Collapse Mandate**: when 2+ classes/files share concern, COLLAPSE via MRO immediately:
  - Same-named verb in 2 projects (`to_str`, `run`, `build`, `_apply_rule`) with different signatures → unify by widening param OR delete descendant + callers go to canonical via `c.* / u.*` from the most-root project. NEVER keep two definitions.
  - `_utilities/<cluster>_*.py` cluster with N>2 files → ask "is each file a genuinely separate public API?" If `cluster_helpers.py` is internal-only → MERGE into the public file. Helper-only files = DELETE TARGETS.
  - Cohesion is NEVER a reason to keep ≥2 files when the MRO can absorb them. "Each file has a single concern" is a description, not a justification — every concern lives on a single MRO-composed mixin.

### 3.2 Types & Contracts

- **Strict Contracts Only**: `Any`, bare `object`, and `Mapping[str, Any]` are TOTALLY FORBIDDEN across all code. Use `t.*` contracts exclusively (`t.Scalar`, `t.JsonValue`, `m.ConfigMap`, etc.). Duplicate type definitions or compatibility aliases (`MyScalar = t.Scalar`) are FORBIDDEN. Use modern Python typing syntax (`X | Y`).
  - **Exception: Intentional Generic Types** - `t.JsonMapping` and `t.JsonMapping` ARE permitted ONLY in these contexts:
    1. **Type aliases** (in `typings.py`): `type ProjectSettings = t.JsonMapping` with docstring explaining intent
    2. **Test fixtures** (in `conftest.py` and test support): Dynamic test data with unknown structure
    3. **Validation/Rule engines**: Return types for unstructured violations (e.g., `r[Sequence[t.JsonMapping]]`)
    4. **Configuration transformers**: Methods that accept/return dynamic configuration from external sources (YAML, JSON)
    - **All other uses are FORBIDDEN**. Use `object` or specific Pydantic models instead.
- **PEP 695 Canonical (Python 3.13+)**: ALL type aliases in `typings.py` must use `type X = ...` syntax. These create `TypeAliasType` objects—using them in `isinstance()` crashes at runtime and is FORBIDDEN. Runtime narrowing MUST use `u.is_*()` functions instead.
- **Type Narrowing**: NEVER use `type(x) is T` or `type(x) == T` to narrow types. Use `isinstance(x, T)` or `TypeGuard`. Avoid gratuitous narrowings for types that shouldn't exist. `cast()` is completely forbidden outside `flext-core` result internals.
- **Nullability and Unions**:
  - `| None` is ONLY permitted inline at usage sites when business semantics require it (e.g., "not configured"). Never bake it into aliases.
  - Inline composed type annotations (e.g., `str | int`) are FORBIDDEN in application code.
- **`t.JsonValue` Exclusivity**: `type Container = t.JsonValue`. `BaseModel` is TOTALLY FORBIDDEN inside `t.JsonValue`. If both are needed, use explicit `t.JsonValue | BaseModel`.

> **ENFORCE-039** — `cast()` calls outside `flext-core` are detected at runtime by `FlextUtilitiesBeartypeEngine.check_cast_outside_core` (dispatched via `c.ENFORCEMENT_RULES["cast_outside_core"]`).

### 3.3 Failures & Error Handling

- **`r[T]` for Fallible Operations** function that can fail MUST return `r[T]`. `T | None`, bare exceptions, and ad-hoc error dicts are FORBIDDEN. The `r` alias is mandatory.
- **Result Outcome Naming**: `r[T]` carriers and result-like protocols/models MUST expose `success`/`failure`, never `is_success`/`is_failure`. Type-guard helpers MUST use non-`is_` names such as `successful_result` and `failed_result`.
- **DSL-First Failure Construction**: In application/runtime flows, prefer centralized DSL helpers (`e.fail_*`, `r.fail_op`, `r.fail_exc`, and `s.fail_*` helpers) over ad-hoc `r.fail("...")` string construction. Direct `r.fail(...)` is reserved for primitive result internals, test scaffolding, or cases requiring explicit `error_data` passthrough.
- **Runtime Strictness**: In `src/` runtime paths, ad-hoc `r.fail(...)` is forbidden unless preserving structured `error_data` from an external boundary. Default to `e.fail_*`, `r.fail_op`, or `r.fail_exc`.
- **No Exceptions as Control Flow**: Bare `try/except` in business logic is FORBIDDEN when `r` composition (`map`/`flat_map`/`lash`) can handle the flow. Bare `except:` is universally forbidden. Catch explicit exceptions.

### 3.4 Tools, Modules & Environment

- **Imports Rules**:
  - `from **future** import annotations

from collections.abc import Mapping, Sequence` MUST be the first import in every Python module.

- `typing.TYPE_CHECKING` is ALLOWED ONLY for type-only imports and `__init__.py` lazy loading. Autogenerated `__init__.py` files MUST preserve the lazy-export pattern.
- `_LAZY_IMPORTS` string references MUST match real class names exactly.
- Import parent components by CLASS NAME (e.g. `from flext_core import FlextProtocols`), never by assigned alias.
- **Command & Output Abstractions**: Bare `subprocess` calls, `sys.exit` outside `__main__.py`, direct `dependency_injector` wiring, and `print()` in production are FORBIDDEN. Use provided abstractions and `FlextLogger`.
- **Zero Hacks**: `model_rebuild()`, `exec()`, `eval()`, direct architectural `getattr()`, inline imports, and fallback `try/except ImportError` blocks are TOTALLY FORBIDDEN.

> **ENFORCE-041** — `model_rebuild` invocations are detected at runtime by `FlextUtilitiesBeartypeEngine.check_model_rebuild_call` (dispatched via `c.ENFORCEMENT_RULES["model_rebuild_call"]`).

### 3.5 Integrity & Change Management

- **Pre-Action Gate (BLOCKING)**: §0.1 applies before any new symbol. Search-first via `grep -rn` (§0.4), prove ≥8× duplication elimination for any new abstraction, delete-first refactor priority. Skipping the gate = governance violation, not "iteration speed".
- **Context Evaluation**: Read and fully understand existing code, MRO chains, and base classes BEFORE changing code. Maximize reuse. Simplifications, TODOs, mocks, and stubs are FORBIDDEN.
- **AST-Grep Required**: Structural code changes/renames across the codebase MUST use `ast-grep` (`sg`). Ad-hoc python/shell scripts, `sed`, and `awk` for code transformations are TOTALLY FORBIDDEN.
- **Integral Changes**: After any type, model, or signature change, you MUST update all references across all 33 projects to maintain global consistency.
- **Linter Zero Tolerance**: Code must pass ALL 4 linters (ruff, mypy, pyright, pyrefly) with ZERO errors/warnings. Suppressions (`# type: ignore`) are FORBIDDEN unless accompanied by a verifiable technical explanation and business necessity, restricted to a single line.
- **Evidence Required**: See §3.8 Verification Discipline.
- **Stay In Scope vs Fix-Forward**: Execute ONLY the assigned task. Out-of-scope speculative "improvements" are FORBIDDEN. **Exception**: when a §0.5 forbidden construct or dead infrastructure blocks measurable LOC reduction inside the active task, fix-forward across the lane boundary — document the cross-lane edit in the commit message. "Another agent's lane" is NOT a valid reason to keep dead code in place.
- **Legacy Extermination (ABOMINABLE)**: Legacy maintenance, non-business validation fallbacks, compatibility wrappers (`def old(): return new()`), deprecation shims, and parallel re-implementations of canonical SSOT (`FlextUtilitiesEnforcement`, `cce.get_catalog()`, `FlextLogger`, `FlextContainer`, etc.) are ABOMINABLE. Delete and replace immediately. Fix forward.
- **Net LOC Delta Negative**: Any PR labelled "refactor", "deduplicate", "cleanup", or "YAGNI" MUST show insertions − deletions ≤ 0. Positive delta on a refactor PR = the work was creation in disguise. Reviewers MUST reject.
- **Git is IMMUTABLE**: Rolling back is FORBIDDEN. `git checkout <file>`, `git reset`, `git revert`, and `git stash pop/apply` to OVERWRITE/DISCARD work is forbidden. Fix issues forward.

> **ENFORCE-040** — Unjustified linter-ignore directives are caught by `ruff PGH003` (registered in catalog as `EnforcementRuffSource(rule_code="PGH003")`).
> **ENFORCE-043** — Pass-through wrappers (single-statement return delegating to another callable with identical args) are detected at runtime by `FlextUtilitiesBeartypeEngine.check_pass_through_wrapper` (dispatched via `c.ENFORCEMENT_RULES["pass_through_wrapper"]`).

### 3.6 Test Standardization

- **Unified Test Namespace**: Tests MUST strictly consume utilities, constants, types, and models from the central test infrastructure (`tests.infra`). Direct imports from `flext_core` or `flext_infra` into `tests/unit` codebase are FORBIDDEN if an equivalent exists in `tests.infra`.
- **Alias Usage**: Use the same canonical aliases for test infrastructure components: `from tests import c, t, p, m, u`.
- **Test Facade Naming**: Test facades MUST use the `TestsFlext<Project><Tier>` pattern. Legacy `Flext<Project>Test<Tier>` and `FlextTest<Project><Tier>` forms are migration targets only.
- **Test Namespaced Classes & MRO**: Test infrastructure MUST follow the single namespaced class structure using MRO. Test namespaces must compose with `TestsFlext` and the project's own namespace (e.g., `class TestsFlextInfraConstants(FlextCoreConstants, FlextTestsConstants)`), defining the test-only branch under `<Domain>.Tests`.
- **Centralized Fixtures & Conftests**: All fixtures and `conftest.py` configurations MUST be centralized within the `tests.infra` MRO structure. Ad-hoc loose mocks or fixtures spread around test scripts are STRICTLY FORBIDDEN. Rely on canonical helpers (`h`) and shared centralized fixtures over recreating isolated objects.
- **Absolute Strictness**: Tests MUST demonstrate the exact same strict typing (`r[T]`), Pydantic v2 execution, and architectural discipline as production code. "Test-only" relaxation or bypassing validators is FORBIDDEN.
- **Behavior-Only Test Contract**: Tests MUST assert public, observable behavior of modules, facades, and services — never their private implementation details. Assertions against internal warning text, stack trace fragments, private helper names, local alias spellings (`p`, `m`, etc.), exact internal class names, MRO shape, or other non-contract internals are FORBIDDEN unless that exact surface is itself the explicit public contract being tested. When a test fails because internals were refactored but behavior is unchanged, the test is wrong and MUST be rewritten to assert stable external behavior instead.
- **No Test Accessor Leakage**: Tests MUST exercise the canonical public contract after migration — fields, `@u.computed_field`, public verbs, and `r` outcomes (`success`/`failure`) only. Tests that reach into legacy getters/setters/predicates or rely on transitional naming are violations.

> **ENFORCE-044** — Reflective probes against private attributes (`hasattr`/`getattr`/`setattr` with a string argument starting with `_` and not dunder) are detected at runtime by `FlextUtilitiesBeartypeEngine.check_private_attr_probe` (dispatched via `c.ENFORCEMENT_RULES["private_attr_probe"]`). Test the public contract; private internals are not part of the test surface.

### 3.7 Associated Skills

- **Namespace/MRO Law**: `flext-mro-namespace-rules` (includes cross-project slot registry for `c/p/t/m/u` ownership)
- **Type Law & Result Patterns**: `flext-strict-typing` (includes PEP 695 aliases/generics, `TypeIs`/`TypeGuard`, `match/case`, `@override`, `@final`, `Self`)
- **Type-System Protocols**: `flext-type-system` (includes the "protocols mandatory at public boundaries" rule)
- **Result/Logging/DI Patterns**: `flext-patterns`
- **Pydantic v2 Governance**: `pydantic-v2-governance` (Model HARD Rules Checklist, Forbidden Structures, facade-only rule)
- **Pydantic v2 Patterns**: `pydantic-v2-patterns` (TypeAdapter caching, RootModel vs BaseModel, Annotated validators, facade import discipline)
- **Constants Discipline**: `flext-constants-discipline` (StrEnum/IntEnum/Literal/frozenset/MappingProxyType/tuple/Final rules)
- **Testing Discipline**: `testing-patterns` (public-API-only, real-flow-over-mocks, enforcement warnings as failures, golden-file examples)
- **Refactoring Workflow**: `flext-refactoring-workflow` (includes the net-negative-LOC delta gate, "more with less" north star)
- **Scope Bootstrap & Reindexing**: `flext-scope-bootstrap` (official Scope bootstrap from the correct root, validation with `status`/`index`, and FLEXT-specific reindex triggers)

### 3.8 Verification Discipline

- **Skepticism by Default**: Treat every claim (test pass, lint clean, behavior unchanged) as unverified until executable evidence is produced. Memory, logs from prior sessions, and "it worked before" are not evidence.
- **Evidence-First**: Every assertion that code passes a gate MUST include the exact command, its stdout/stderr, the exit code, and a UTC timestamp. Store durable artifacts under `.reports/` and attach concise execution notes to the owning Bead with `bd comments add`. Links and proof, never bare verdicts.
- **Severity-First Reporting**: When reporting issues, lead with the highest-risk item. Order: data loss > security > correctness > performance > style.
- **Transparency About Limits**: Be explicit about what was NOT checked. If only one project was linted, say so. Partial verification presented as complete verification is a governance violation.
- **No Proxy Evidence**: Screenshots, CI badge URLs, or "make check passed" without output are FORBIDDEN. The raw command output is the evidence.
- **Scope Must Match Claim**: A claim of "all linters pass" requires evidence from ALL 4 linters (ruff, mypy, pyright, pyrefly). A claim of "all projects pass" requires evidence across all affected projects.
- **Documentation Code Integrity**: Every Python code block in governance files (AGENTS.md, skills, docs) MUST pass all 4 linters. Pseudo-code and structural patterns use ` ```text ` fences, never ` ```python `. Bad-pattern examples are replaced with text instructions describing what is FORBIDDEN and what to use instead — no invalid Python in documentation.

> **Runtime Catalog Dispatch** — All `ENFORCE-NNN` rules in `c.ENFORCEMENT_CATALOG` whose source is `EnforcementBeartypeSource(hook=...)` are exercised at runtime by `FlextUtilitiesEnforcement` (dispatcher in `c.ENFORCEMENT_RULES` + per-tag arms in `FlextUtilitiesEnforcementCollect._namespace_items` + `check_<tag>` static methods on `FlextUtilitiesBeartypeEngine`). `make val` and the test suite both surface violations as `me.Violation` records — no separate audit verb is required (per YAGNI; see §5).

## §4 Import Law

- Canonical alias imports are mandatory at usage sites: `r,t,c,m,p,u,d,e,h,s,x`. You only ever import the local facade explicitly; parent facades are inherited seamlessly.
- **Dependency Order**: Future, stdlib, third-party, first-party, local.
- **`flext-core` Imports**: Import concrete submodules (`flext_core.<module>`), NOT the package root.
- **Subproject Imports**: Consume public API/facade exports; NEVER import private `_` internals.
- **Forced Patterns**: Wildcard imports and relative imports are FORBIDDEN in governed code.
- **Aliases**: No double-assignment of facade aliases (`c/m/p/t/u` are assigned once at module bottom).
- **Direction**: Cross-tier imports violating architecture direction are FORBIDDEN.
- **No Same-Project Cross-Facade Runtime Imports**: Public same-project facade files (`constants.py`, `models.py`, `protocols.py`, `typings.py`, `utilities.py`) MUST NOT import sibling public facades or aliases at runtime. Use direct private-class imports from `models/*` / `_utilities/*` or MRO inheritance instead. The only standing runtime exception is `FlextRuntime` inside `flext-core`.
- **Abstraction Boundary Enforcement (SUPREME LAW)**: Libraries abstracted by a flext project MUST NOT be imported directly outside that project's `src/` domain. Core-abstracted libraries (pydantic, dependency_injector, structlog, returns, orjson, pyyaml) are FORBIDDEN in consumers (`tests/`, `examples/`, `scripts/`, other projects' `src/`). Use public abstractions from the originating library (`m.*`, `c.*`, `p.*`, `t.*`, `u.*`, `r[T]`) instead. This applies equally to runtime code, typing annotations, and constants.
- **Facade Import Matrix**:
  - `typings.py` may reference same-project `p` and `m` ONLY under `TYPE_CHECKING`.
  - `protocols.py` may reference same-project `t` and `m` ONLY under `TYPE_CHECKING`.
  - `models.py` may reference same-project `t` and `p` ONLY under `TYPE_CHECKING`.
  - `constants.py` may import same-project runtime symbols when genuinely required.
  - `utilities.py`, `models/*`, and `_utilities/*` may import private classes directly across private modules to break cycles, but MUST NOT hop through sibling public facades.
- **MRO Alias Import Rule — Complete Matrix (CRITICAL)**:
  - Each facade file (`constants.py`, `models.py`, `typings.py`, `protocols.py`, `utilities.py`) DEFINES its own alias (`c`, `m`, `t`, `p`, `u` respectively). Therefore, that alias MUST come from the **parent MRO package** in that facade file AND in ALL private modules (`models/*.py`, `_utilities/*.py`, `_typings/*.py`, `_protocols/*.py`, `_constants/*.py`) that participate in its lazy-load chain.
  - **Why**: Importing an alias from own package triggers loading the facade file that defines it (`m` → `models.py`, `u` → `utilities.py`, `c` → `constants.py`, `t` → `typings.py`, `p` → `protocols.py`). If that facade depends on `models/`/`_utilities/` which are still loading → deadlock.
  - **Parent MRO lookup**: Check each facade file to find its parent. Example for flext-ldif:
    - `models.py`: `from flext_cli import m` → parent for `m` is `flext_cli`
    - `utilities.py`: `from flext_cli import u` → parent for `u` is `flext_cli`
    - `constants.py`: `from flext_cli import c` → parent for `c` is `flext_cli`
    - `typings.py`: `from flext_cli import t` → parent for `t` is `flext_cli`
    - `protocols.py`: `from flext_cli import p` → parent for `p` is `flext_cli`
  - **flext-core (ROOT)**: Is the MRO root — its `models/*.py` and `_utilities/*.py` import ALL aliases from `flext_core` (own package). This works because flext-core's lazy loader handles internal sequencing.

  **Complete import matrix by file type**:

  | File type | `m` | `u` | `c` | `t` | `p` | `r` | Sibling classes | Named Flext* classes |
  |-----------|-----|-----|-----|-----|-----|-----|-----------------|---------------------|
  | `models/*.py` | parent | parent | own pkg | own pkg | own pkg | own pkg | own pkg (runtime) or TYPE_CHECKING (annotation) | own pkg via lazy init |
  | `_utilities/*.py` | own pkg | parent | own pkg | own pkg | own pkg | own pkg | own pkg via lazy init | own pkg via lazy init |
  | `models.py` (facade) | parent | parent | — | own pkg | — | — | own pkg via lazy init | — |
  | `utilities.py` (facade) | own pkg | parent | — | — | — | — | own pkg via lazy init | — |
  | `constants.py` (facade) | — | — | parent | own pkg | — | — | — | — |
  | `typings.py` (facade) | — | — | — | parent | — | — | own pkg via lazy init | — |
  | `protocols.py` (facade) | — | — | — | — | parent | — | own pkg via lazy init | — |
  | `services/*.py` | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg |
  | `servers/*.py` | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg |
  | `base.py` / `api.py` | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg |
  | `settings.py` | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg | own pkg |
  | `tests/*.py` | tests pkg | tests pkg | tests pkg | tests pkg | tests pkg | tests pkg | tests pkg | tests pkg |

  **Key rule**: "parent" means the alias comes from the **most advanced parent MRO package** that the project inherits from (check the facade file's own import). "own pkg" means `from flext_<project> import X` which resolves via the auto-generated lazy `__init__.py`.

  - **Sibling classes** in `models/*.py` used at runtime (base classes, `isinstance`) → `from flext_<project> import FlextProjectModelsBases` (lazy init resolves before cycle).
  - **Sibling classes** used ONLY in annotations (with `from __future__ import annotations`) → `TYPE_CHECKING` block.
  - **Use organic namespace** `m.Ldif.ClassName` at all usage sites instead of raw `FlextLdifModelsSettings.ClassName`.
- **Circular Import Resolution (CRITICAL)**:
  - **Root Cause**: Circular imports arise when (1) `models/*.py`/`_utilities/*.py` import `m` or `u` from own package, triggering the facade module load chain, or (2) modules at the same tier reference each other.
  - **Correct Solution** (NO workarounds):
    1. **`m, u` from parent MRO** in `models/*.py`, `_utilities/*.py`, `models.py`, `utilities.py` — prevents facade self-load cycle.
    2. **Use `from __future__ import annotations`** — Converts ALL type hints to forward references (strings).
    3. **Use `TYPE_CHECKING`** for annotation-only imports that would create a cycle.
    4. **Trust lazy loading in `__init__.py`** — The lazy-load system properly sequences module initialization. Sibling class imports via `from flext_project import ClassName` work correctly through the lazy map.

- **FORBIDDEN Workarounds**:
  - ✗ `from flext_project._models.X import Y` — private submodule bypass
  - ✗ `from flext_core import m, u` when the parent MRO is `flext_cli` — wrong parent, less complete namespace
  - ✗ `from pydantic import BaseModel/ConfigDict` in consumers — use `m.BaseModel`, `m.ConfigDict`
  - ✗ Using `model_rebuild()` — indicates root-cause unresolved
  - ✗ Using `object` or `Any` as catch-all types — use precise `t.*` contracts
  - ✗ Reordering `__init__.py` imports or relying on "order of initialization" — architecture must NOT depend on load order
- **Verification**: Run `make gen` without timeout or errors. Imports should resolve cleanly via `python -c "from flext_core._protocols.* import *"`.
- *Detailed matrix & exceptions*: See skill `flext-import-rules`.

## §5 Make Contract

- **Primary Entrypoint**: Automation entrypoint is `make` for multi-gate workflows. Bare tool commands (`ruff check`, `pyrefly check`, `pyright`, `mypy`, `pytest`) are allowed for single-file checks — they are auto-proxied through RTK for token savings. Never use `.venv/bin/` prefixed paths.
- **Workspace Verbs**: `boot check scan fmt docs test val types clean gen mod up sync`.
- **Project Verbs** (`base.mk`): `boot check scan fmt docs test val clean`.
- **Git Verbs**: Use `make` for Git operations: `make stat`, `make save MESSAGE="..."`, `make push`, `make tag`, `make pr`.
- **Advanced Make Options**: Use the provided selectors to target scenarios directly instead of writing custom bash loops. Examples: `make check PROJECT=flext-core FILE=src/foo.py CHECK_GATES=pyright`, `make test MATCH=test_container FAIL_FAST=1`, `make check CHANGED_ONLY=1`.
- **Selectors**: `PROJECT`, `PROJECTS`, `CHECK_GATES`, `VALIDATE_GATES`, `PYTEST_ARGS`, `FIX`, `JOBS`, `FAIL_FAST`, `FILE`, `FILES`, `CHANGED_ONLY`, `MATCH`, `RUFF_ARGS`, `PYRIGHT_ARGS`, `CHECK_ONLY`, `VERBOSE`.
- **File Targeting** (`check`/`test`/`format`): `FILE=<path>` or `FILES="a.py b.py"` runs only on those files (fast-path, bypasses `flext_infra check run`). `CHANGED_ONLY=1` auto-discovers git-modified `.py` files.
- **Test Shortcuts**: `MATCH=<expr>` is an alias for pytest `-k <expr>`. `FAIL_FAST=1` adds `-x`. `VERBOSE=1` adds `-vv -s`.
- **Lint Shortcuts**: `RUFF_ARGS="--select E501"` passes extra args to ruff. `PYRIGHT_ARGS="--level basic"` passes extra args to pyright. `CHECK_ONLY=1` on format/check runs without writing (dry-run).
- **Scope Controls** (Workspace): `VALIDATE_SCOPE=project|workspace`, optional `DEPS_REPORT=0`.
- **No Bypasses**: Strictness is mandatory. `SKIP_*` bypass toggles in the contract are FORBIDDEN.
- **Exit Codes**: `0` pass, `1` policy failure, `2` usage/settings error, `3` infra/runtime error.
- **Validation**: Policy/automation edits MUST run `make val VALIDATE_SCOPE=workspace` before claiming completion.
- **Reports**: Must be factual, machine-readable when produced, and include explicit executable next actions.
- *Verb semantics & thresholds*: See skill `flext-quality-gates`.

## §6 Quality Gates

- **Environments**: Workspace `.venv` is mandatory. System Python/pip usage is FORBIDDEN. Project-local `.venv` is fallback-only when workspace `.venv` is missing.
- **Preflight**: Before workspace loops, ensure root `.venv` exists and remove project `.venv` drift. In fallback mode, run `make boot` before loops.
- **`pyproject.toml` Generation**: Files must follow Poetry 2.x + PEP 621/639 constraints. New packages MUST be managed via `poetry add` and `poetry remove`. Furthermore, you must run `make mod` and `make up` to regenerate, consolidate dependencies, and format the toml files before lock/install. Manually hacking dependency tables is FORBIDDEN.
- **Coverage**: Source of truth is purely `[tool.coverage.report] fail_under` in each project's `pyproject.toml`. No Makefile constants, no `--cov-fail-under` flags.
- **No Silent Failures**: Constructs like `2>/dev/null` or `|| true` on mandatory gates are FORBIDDEN.
- **Attached sub-repo opt-in**: directories outside the workspace's git tree (separate sub-repos) opt into workspace iteration by declaring `[tool.flext.workspace] attached = true` in their own `pyproject.toml`. The contract is the typed `FlextModelsProjectMetadata.ProjectToolFlextWorkspace` model in `flext-core` (frozen, `extra="forbid"`, single `attached: bool = False` field) reachable via `u.read_tool_flext_config(root).workspace.attached`. Workspace iterators (`u.Infra.discover_project_candidates`, `u.Infra.discover_projects`, `u.Infra.resolve_projects`) surface attached entries only when `include_attached=True` is passed. Default (False) preserves the legacy git-tracked-only behaviour.
- **Docs Python codeblock parity**: embedded ` ```python ` fenced blocks under every governed `docs/` scope are linted by the `python-codeblocks` audit check on `FlextInfraDocAuditor` (extends the existing `docs/auditor.py` service — no parallel route or service). Each block is extracted via `c.Infra.PYTHON_FENCE_RE`, written to a temp file, and gated through `u.Cli.run_raw(["ruff", "check", ...])`. Failures land as `m.Infra.AuditIssue(issue_type="python_codeblock", severity="medium")` records flowing through the standard audit JSON + markdown reports. Invoked via `make docs DOCS_PHASE=audit` (default `check="all"` includes `python-codeblocks`).
- *Gate details & matrix*: See skill `flext-quality-gates`.

## §7 Skill System

- **Authority**: Skills are authoritative detail documents. This file (`AGENTS.md`) is the supreme law surface framing them.
- **Load Order**: Touched-path `rules-*` skill first, supporting skills second. Afterwards, load only minimal skills needed for the change.
- **Mandatory Usage**: Do not implement rules from memory. Do not claim skill usage without reading the `SKILL.md`.
- **Plan-Mode Intent Recovery**: In plan mode, always use the `/ask` skill on the target code before writing the plan. Use it to read the code and recover the original transcript that generated it when available; understanding intent is mandatory input to a better plan.
- **Mapping**: Baseline maps must be respected (`flext-core->rules-flext-core`, `src->rules-src`, `tests->testing-patterns`, etc.).
- **Rule Definitions**: `rules.yml` schema uses flat fix keys only. Prefer `type: ast-grep`; use `type: custom` only when AST matching is completely unviable. `fix_auto: true` must map to an executable real fix mechanism.
- **Prompt Routing**: For requests centered on simplification, deduplication, pyrefly/ruff reduction, canonical facade migration, or large-scale contract cleanup, agents MUST load `.github/prompts/flext-aggressive-scale-refactor.prompt.md` after `AGENTS.md` and the path-scoped skills. Prompts operationalize this file; they never replace it.
- **Prompt/Agent Review Routing**: Requests to review or improve prompts, agent instructions, `AGENTS.md`, `copilot-instructions`, or `SKILL.md` files are governance work. Agents MUST read `AGENTS.md` first, then load the relevant scoped skills, and improve those surfaces by reinforcing canonical-source discipline, correct skill-loading order, repository-native tool routing, and non-duplication of policy text.
- **Continuous Skill Hardening**: When repeated agent failure modes appear (skipped impact analysis, incomplete propagation, non-surgical edits, wrong tool choice, weak context alignment), update the relevant skill or prompt in the same governance cycle so the behavior becomes stricter for future runs.
- *Skill format policies*: See skills `skill-format-universal`, `flext-docs-pointer-policy`.

## §8 Change Management

- **Policy Workflow**: Policy changes land in `AGENTS.md` first, then propagate to skill documents.
- **Complete Work**: Never ship incomplete work as complete. Each claim REQUIRES command evidence (format per §3.8). Changes must be minimal, explicit, root-cause oriented, and verifiable.
- **No Unapproved Bypass**: Altering lint/gate semantics or deferring/skipping a violation is FORBIDDEN without explicit in-session user approval.
- **Correct Governance**: If governance corrections arise during work, update this file immediately before further implementation.
- **Commit-After-Validation**: Every passing validation MUST be immediately accompanied by a `git add -A` → `git commit` → `git pull --rebase` → `git push` sequence. Uncommitted or unpushed work is LOST WORK.
- **Frequent Push is FUNDAMENTAL (BLOCKING)**: Push after EVERY atomic per-lane fix — never batch multiple lanes or hold work for an end-of-session push. Each push is a coordination point: another agent may be working in parallel, so `git fetch` + `git pull --rebase --autostash` before every push, never `--force`, and never sweep another lane's dirty working tree into your commit. Every push/handoff MUST end with an explicit indication of what to do next (recorded in Beads, see below) so the next actor — human or agent — can continue without re-discovery.
- **Beads Action Tracking (BLOCKING)**: Track your own work as Beads issues with a parent epic + sub-beads per task/sub-task, under a distinct `--actor`/`--assignee` and an `agent:<name>` label so your lane is separable from concurrent agents'. Set state as you progress (`bd update`/`bd close`), and when dispatching subagents give each a sub-bead. Coordinate by reading other actors' beads; do not act on a lane another actor owns while it is in-progress/dirty.
- **One Session Loop**: At most ONE recurring 5-minute session loop (cron) per agent session — do not spawn duplicates; reuse the existing job.

### 8.1 Refactor Priority Stack (THE ONLY VALID ORDER)

The four refactor questions, asked **in order**. Skipping any of (1)–(3) to reach (4) = governance violation.

1. **Delete dead code first.** Run `grep -rn '<symbol>' flext-core/src flext-cli/src flext-infra/src flext-tests/src --include='*.py' | grep -v '<owning_file>'`. Zero external consumers = the symbol is dead infrastructure. Archive (`mv X X.bkp`) and remove its export sites (lazy manifests, `__all__`, MRO bases). Per AGENTS.md §3.8, anything duplicating runtime detection (`FlextUtilitiesEnforcement`, `__pydantic_init_subclass__`) is YAGNI-FORBIDDEN regardless of lane ownership.
2. **Collapse via existing MRO.** ≥2 classes sharing fields/methods/`model_config` → re-parent to an existing or new MRO base. New base allowed ONLY with §0.1#2 evidence (≥8× LOC eliminated by the new base).
3. **Move loose objects into class.** Module-level `def`/`Final[X]`/assignments → relocate as classmethod/staticmethod/ClassVar inside the canonical class. Skip when relocation cost (callsite churn) exceeds 5× LOC saved.
4. **Only after (1)–(3): propose new abstraction.** Must satisfy §0.1#2.

- **Canonical Facades First**: Prefer `flext-core` and `flext-cli` public facades, settings, models, typings, protocols, utilities, results, and exceptions over local re-declarations. Search §0.4 inventory before creating.
- **Pydantic at the Boundary**: Validation, transport typing, and runtime data normalization MUST converge on canonical Pydantic v2 models through `m.*` and `u.*`, not ad-hoc dict conversion pipelines.
- **Constants Drive Contracts**: Closed token sets, regexes, read-only maps, and immutable collections belong in `c.*`; `t.*` should reuse those canonical definitions instead of duplicating them.
- **Same-Cycle Propagation**: Signature, contract, enum, model, or settings changes MUST be propagated to every impacted caller in the same cycle. No half-migrations.
- **Measured Reduction (BLOCKING)**: Refactor PR MUST close with `git diff HEAD --stat` showing insertions ≤ deletions. Cosmetic churn (renames, blank-line tweaks, file splits without LOC reduction) is a §3.5 violation. Reviewers MUST reject positive-delta refactor PRs.
- **Impact First**: No refactor, rename, or contract change may start without an explicit blast-radius check proportionate to the change. If the change can cross file or project boundaries, you MUST inspect references before editing.
- **Surgical Necessity**: Every change must be justified by real architectural, typing, validation, or enforcement need in the active context. Edits that are broad, speculative, or weakly justified are violations.
- **Zero Debt at All Times**: `ruff`, `pyrefly`, enforcement checks, and `pytest` must remain zeroed across all affected projects at all times. Pre-existing failures in the active dependency chain or requested scope are not an excuse to stop; fix them in the same execution cycle unless the user explicitly narrows scope or blocks the work.

## §9 Agent Execution Pre-requisites

- **Verify Before Implement**: Check recent commits (`git log --oneline -20`) and active task trackers to prevent duplication. Cross-session deduplication is critical.
- **Scope Discipline**: DO NOT modify files outside the specific task boundary. If blocked, escalate instead of silently rewriting external dependencies.
- **Scale and Parallelism**: Refactoring many call sites or modules across the portfolio should utilize multiple batched passes to retain focus and verifiability.
- **`.new/.old` Swap Protocol**: For massive file modifications (>50 lines changed), create a `.new` file, verify changes, then execute `mv file.py file.py.old && mv file.py.new file.py`. Commit both in one transaction.

### 9.2 Mandatory Tooling Discipline

- **Scope is Mandatory When Available**: If `.scope/` exists or `scope status` succeeds, use `scope` first for cross-file discovery, call-site inspection, blast-radius analysis, caller/reference tracing, and architecture orientation. Skipping `scope` for qualifying tasks is a governance violation.
- **Scope Freshness is Mandatory**: Keep the Scope index fresh. Run `scope index` after structural edits, and for multi-project or workspace-wide work prefer `scope workspace index` (or `scope workspace index --watch`) so structural queries stay trustworthy.
- **Scope Bootstrap Must Use The Official CLI Baseline**: For repo-local FLEXT work, initialize Scope from the repository root with `scope init`, which creates `.scope/config.toml`. For multi-repository sessions, initialize member repositories first and then run `scope workspace init` at the workspace root to generate `scope-workspace.toml`. Do not handcraft Scope config files from memory.
- **Scope Validation Loop Is Required**: After Scope bootstrap or any edit to `.scope/config.toml` or `scope-workspace.toml`, run `scope status` before trusting queries, then rebuild the matching index with `scope index` or `scope workspace index`.
- **FLEXT Structural Changes Require Reindexing**: Re-run the relevant Scope index after `make gen`, facade/export regeneration, namespace or alias migration, symbol/file moves, or other structural changes that can invalidate caller/reference results.
- **AST-Grep is Mandatory for Structural Changes**: Any structural rename, repeated call-site migration, broad contract propagation, or syntax-pattern rewrite MUST use `ast-grep` (`sg`) unless the change is provably single-site. Plain grep-only refactors for structural work are forbidden.
- **Serena is Mandatory When Available**: If Serena is connected or its project configuration is present, activate the workspace/project correctly and use its project-aware capabilities for symbol/refactor/navigation flows that depend on language-server-backed context. Do not leave Serena half-configured and then ignore it.
- **Official Serena Setup Only**: FLEXT Serena setup must follow the upstream quick-start flow from the global AGENTS contract: installed `serena` CLI, `serena init --language-backend LSP`, workspace MCP registration in `.vscode/mcp.json`, and repo-local project config in `.serena/project.yml`. Do not replace these with local wrappers or alternate config formats.
- **FLEXT Serena Project Baseline**: The canonical local project setup is `serena project create . --name flext --language python --index`. When `.serena/project.yml` already exists, validate with `serena project health-check` and refresh with `serena project index` instead of recreating the project.
- **FLEXT Serena Scope Hygiene**: Keep `.serena/project.yml` focused on the navigable repository surface. Synthetic or support-only trees that break symbol extraction must be excluded through `ignored_paths` rather than tolerated as routine Serena failures.
- **FLEXT Serena Boot Order**: For Serena-backed work in this repository, use the workspace MCP server command `serena start-mcp-server --context=vscode --project-from-cwd`, activate `flext`, then run `check_onboarding_performed` and `onboarding` when required before relying on symbol tools.
- **MCP is Mandatory When Context Requires It**: If the task depends on configured MCP capabilities (remote repo metadata, GitHub workflow state, external structured resources, Serena project tooling), use the configured MCP server rather than improvising local guesses or skipping context.
- **No Excuses Routing**: Tool availability must be checked, not assumed away. If a required tool is unavailable or misconfigured, state that explicitly and reduce scope safely; do not silently fall back to weaker reasoning for a high-blast-radius change.
- **Impact Analysis Before Edit**: Signature changes, alias changes, namespace moves, protocol/model/settings/constant changes, and deletions require a tool-backed reference audit before the first substantive edit.
- **Propagation Audit Before Exit**: Before claiming completion on cross-file changes, rerun the relevant caller/reference search to confirm there are no leftover old paths.
- **Learning Loop Required**: When a required tool is misused or underused, harden the relevant skill or prompt in the same governance cycle so the next execution becomes stricter and more precise.
- **Canonical Scope Params on flext-infra Verbs**: Every flext-infra verb (`python -m flext_infra <group> <verb>`) accepts the canonical scope selectors `--workspace`, `--projects`, `--project`, `--module`, `--namespace`. These flags compose: a verb run with `--workspace . --module flext_core.result` runs only against the named module across the whole workspace. The fields are declared once on `FlextInfraServiceBase` (and `FlextInfraModelsMixins.ScopeMixin` for non-service request payloads) so verbs inherit them uniformly. Refactor verbs default to the narrowest explicit scope to avoid accidental blast; audit verbs may default to workspace.
- **Verb Safety Gate (Mandatory for Refactor Verbs)**: Every refactor verb that mutates source files MUST wrap its writes in one of the canonical safety primitives: `FlextInfraUtilitiesProtectedEdit.preview_source_writes(...)` (transactional multi-file preview-restore), `FlextInfraUtilitiesProtectedEdit.protected_file_edit(...)` (single-file lint-delta + restore), or `FlextInfraRefactorSafetyManager.create_pre_transformation_stash(...)` followed by `.rollback(...)` on regression. The gate captures a pre-run lint/pyrefly snapshot, applies the verb's writes, captures a post-run snapshot, and restores the pre-edit state if either tool reports a NEW error vs. the baseline. The user-visible workspace MUST never be left red after a verb invocation. **The verb-internal rollback inside a safety gate is the ONE legitimate use of revert in flext-infra** — it is scoped to the verb invocation and never visible to the user; the §3.5 "Git is IMMUTABLE" rule applies to user-facing operations.
- **Discovery vs Correction Substrate Boundary**: `flext-core` owns lightweight runtime detection ONLY — Pydantic v2 model-init hooks (FlextMroViolation, FlextValidationWarning, …), beartype-decorated probes (preferred substrate for new runtime rules — advanced, deeply integrated with internal object typing), and `ast` stdlib MINIMALLY (last resort, scoped to a single target symbol, with mandatory graceful skip when `inspect.getsourcefile(target)` returns `None` — the runtime may not have source files on disk). flext-core publishes violations as in-memory data; it MUST NOT walk the source tree, run subprocesses, or invoke Rope. `flext-infra` owns heavy static analysis + rewrite — Rope-only inside refactor verbs (`libcst`, `ast-grep` as engine, `ast` stdlib are forbidden in flext-infra refactor paths). flext-infra orchestrators consume flext-core runtime emissions + the declarative `c.ENFORCEMENT_CATALOG` and supplement only `pattern_kind="static_rope"` rules with their own Rope analysis.

### 9.1 Coding Directives for Agents

- **Runtime Aliases**: `c`, `p`, `t`, `m`, `u` are declared via MRO in each layer (`src/`, `tests/`, `examples/`, `scripts/`). In test code: `from tests import c, m, p, t, u`. In examples: `from examples import ...`. NEVER import aliases across project boundaries (e.g., `from flext_target_oracle import t` in tests is FORBIDDEN). Operational aliases (`r`, `e`, `h`, `d`, `s`, `x`) come from `flext_core` or the project's extended package.
- **No Loose Aliases**: Remove compatibility aliases entirely. Constants belong in `c`, protocols in `p`, typings in `t`, models in `m`, utilities/helpers in `u`. Never maintain these concerns outside their canonical namespace.
- **Narrowing Enforced**: No `type(x) == T`. Use `isinstance(x, T)` or `TypeGuard` properly. Prefer Pydantic validation functions where structured data is involved.
- **Evidence Requirement**: See §3.8 Verification Discipline.

## §10 Multi-Agent Parallel Execution Law

### 10.0 Beads Pending-Work SSOT

Beads is the only source of truth for pending work, lane state, and cross-lane dependency hierarchy in this repository. Legacy plans, reports, continuation prompts, operations handoffs, and migrated architecture TODOs are reference material only until their actionable content is imported into Beads; after import, they must be removed with `git rm` or archived as `.bak`.

`.beads/issues.jsonl` and `.beads/interactions.jsonl` are generated storage files. Manual edits to any `.beads/*.jsonl` file are FORBIDDEN. Create, update, close, relate, import, export, repair, resolve conflicts, and sync Beads data only through `bd` commands such as `bd create`, `bd update`, `bd close`, `bd dep`, `bd import`, `bd export`, `bd repair`, `bd resolve-conflicts`, and `bd sync`.

If Beads storage appears stale, corrupt, conflicted, or out of sync, stop editing and repair through the CLI path: `bd sync --import-only`, `bd repair`, `bd resolve-conflicts`, `bd sync`, then validate with `bd doctor`, `bd lint --status all`, `bd dep cycles`, and `bd graph --all --compact`. A patch to JSONL that bypasses `bd` is invalid even when it produces valid JSON.

### 10.0.1 Temporary Migration Session Rule — `mro-uqji`

This subsection is temporary and active only while Bead `mro-uqji` is not closed. Remove it in the same checkpoint that closes `mro-uqji`.

For the legacy-docs-to-Beads migration, the session has exactly one coordination loop: every 5 minutes, the owning agent must run one Beads/Git/quality checkpoint, update the active Bead notes or sub-bead status, and then continue from the current state. Creating a second timer, heartbeat loop, watcher, daemon, or background cadence for the same migration is forbidden.

The owning agent must coordinate its own work through `mro-uqji` and child Beads, not through legacy markdown or chat memory. Each delegated subagent gets a distinct child Bead or sub-bead before work starts, with a non-overlapping scope and explicit acceptance criteria. Subagents may audit or patch only their assigned scope; they must not edit `.beads/*.jsonl` directly and must report changed paths or read-only findings back to the owning agent.

For this migration only, the user has authorized frequent Git checkpoints: after each validated migration slice, run `git status`, stage only files belonging to this migration slice, commit with no agent attribution, and push. Do not include unrelated dirty files from other agents. If the tree contains unrelated changes that prevent a clean checkpoint, record the blocker in the active Bead and continue with the next non-conflicting migration slice.

Quality control for each slice is mandatory: use `bd` commands for Beads mutations, run Beads graph/storage checks for Beads changes, run stale-reference scans for documentation cleanup, and report command names, exit codes, and relevant output before marking any child Bead done.

### 10.1 The 11 Commandments (Execution Ritual)

UNBREAKABLE LAW for all parallel agent work:

1. **Organize libs first**: Domain monopoly—each module owns its domain exclusively.
2. **Minimal skeleton**: Start with interfaces/protocols. Optimize structure before implementation.
3. **Reconnect one-by-one**: Fix ONE integration at a time, verify before moving to the next.
4. **Tests last per module**: Update tests AFTER implementation passes static checks.
5. **Zero Tolerance Linters**: Ruff, mypy, pyright, pyrefly MUST all pass. No `# type: ignore`.
6. **Stay in Lane**: Only touch files in your ownership. READ-ONLY for others.
7. **Never Rollback**: Fix forward only. No `git revert`, no deprecation shims.
8. **Commit Frequently**: Every task completion = separate commit + push.
9. **`.new/.old` Owned-Only**: Use the `.new/.old` pattern ONLY for files you own exclusively.
10. **No Automation Scripts**: Manual changes only. No shell scripts for mass edits.
11. **Never Rush/ULW**: No ultrawork mode, no batched giant commits. Perfection over speed.

### 10.2 Core File Ownership (`flext-core`)

**Ownership Matrix**:

| Category    | Primary Owner                                                                              | Read-Only For Others |
| ----------- | ------------------------------------------------------------------------------------------ | -------------------- |
| **Agent 1** | `dispatcher.py`, `constants.py`, `models/cqrs.py`                                         | All other agents     |
| **Agent 2** | `registry.py`, `typings.py`                                                                | All other agents     |
| **Agent 3** | `service.py`, `models/base.py`                                                            | All other agents     |
| **Agent 4** | `result.py`, `exceptions.py`, `runtime.py`, `loggings.py`                                  | All other agents     |
| **Agent 5** | `container.py`, `decorators.py`, `handlers.py`, `mixins.py`                                | All other agents     |
| **FROZEN**  | `context.py`, `settings.py`, `models.py`, `utilities.py`, `_utilities/*`, `__version__.py` | NO AGENT MODIFIES    |

*Exception*: FROZEN files may be unfrozen ONLY for: (a) annotation additions (typing, `m.Field()`, imports), or (b) **performance-only caching changes** — adding `ClassVar` cache fields, wrapping instantiations in lazy-load patterns, and adding env-variable configuration toggles — provided the change is isomorphic (same inputs → same outputs), passes all linters and tests, and runs as single-agent work (not parallel). Behavioral logic changes beyond (a) and (b) remain frozen.

**`protocols.py` Section Split**:

- Sections must be appended strictly at the end of their respective ownership blocks.
- **A1**: CommandBus, Middleware, Processor
- **A2**: Registry
- **A3**: Model, Settings, Service, Validation, ValidatorSpec
- **A4**: Result, Result, VariadicCallable, ResourceFactory, Log, Logger, Metadata
- **A5**: Context, RuntimeBootstrapOptions, DI, Handler, RegisterableService, ServiceFactory
- *Lines 1-236 & 1289+ are strictly FROZEN for behavioral changes. Performance-only caching additions (ClassVar cache fields, lazy-load wrappers) are permitted per the FROZEN file exception above, limited to method bodies — function/method signatures and class declarations within the frozen range MUST NOT be altered.*

### 10.3 Execution Phases

- **Phase 0 (SOLO)**: Agent 4 completes Wave 0 (`RuntimeResult.__slots__` + `r.fail()` + `p.Result`) and PUSHES. All others BLOCKED.
- **Phase 1**: Agent 4 continues + Agent 5 starts (containers, decorators, etc). A5 must `git pull --rebase` first.
- **Phase 2**: Agent 1 (Dispatcher) + Agent 3 (Service) start. Must `git pull --rebase` first.
- **Phase 3**: Agent 2 (Registry) starts. Must `git pull --rebase` first.
- **Phase 4 (Consumers)**: All agents work on their assigned consumer projects IN PARALLEL.

### 10.4 Lint Scoping & Quality

- **During parallel work**: Agents run linters ONLY on modified files using bare commands (`ruff check <file>`, `pyrefly check <file>`, `pyright <file>`, `mypy <file>`). RTK auto-proxies for token savings.
- **At phase boundaries**: Agents run FULL project lint (`cd <project> && make check`) before pushing.
- **Before Phase 4**: ALL agents run full `flext-core` lint and verify ZERO errors. No `# type: ignore`.

### 10.5 Git & Session Hygiene

- **Always Rebase**: `git pull --rebase` before EVERY push. NEVER use basic `git pull`.
- **Never Force Push**: NEVER `git push --force` to main/master.
- **Conflict Resolution**: Conflict in YOUR file → resolve manually. Conflict in ANOTHER agent's file → `git checkout --theirs <file>`.
- **Cross-Session Deduplication**: Before spawning new tasks, verify no other agent is working on the same scope via Beads (`bd search`, `bd list --status open`, `bd list --status in_progress`, `bd dep tree`) and `git log --oneline -20`. Merge overlapping work into the existing Bead hierarchy rather than creating duplicate plans.

## §11 flext-cli SSOT — Inviolable CLI Domain Owner

**flext-cli is the SINGLE source of truth for the CLI domain across the entire workspace.** No other project may invade this responsibility. The only exception is flext-core (which cannot import flext-cli to avoid circular imports).

### Forbidden imports outside `flext-cli/src/` (audited automatically)

The following stdlib/third-party libraries MUST NOT be imported anywhere outside `flext-cli/src/`:

- `argparse` → `cli.register_result_command(model_cls=PydanticModel, handler=...)` + `cli.create_app_with_common_params`
- `typer` → `cli.create_app_with_common_params` + `cli.register_command` / `cli.register_result_routes`
- `click` → `c.Cli.CliAbortError` / `c.Cli.CliCommandError` (re-exported); `t.Cli.ExternalCli` for Singer-SDK boundary types
- `rich` → `cli.print` / `cli.display_message` / `cli.render_panel` / `cli.create_tree`
- `tabulate` → `cli.format_table` / `cli.show_table`
- `colorama` → `cli.print` with `c.Cli.MessageStyles.*`
- `prompt_toolkit` → `cli.prompt` / `cli.confirm` / `cli.prompt_choice` / `cli.prompt_password`
- `tqdm` → `cli.display_progress`
- `getpass` → `cli.prompt_password`
- `orjson` / `ujson` / `simplejson` → `cli.read_json_file` / `cli.write_json_file` / `u.Cli.json_dumps` / `u.Cli.json_loads`
- stdlib `subprocess` module → `cli.run` / `cli.capture` / `cli.run_raw` / `cli.run_checked` / `cli.run_to_file`

### Direct stdlib usage forbidden (call-site detection)

- `json.load(open(...))` / `json.dump(data, open(...))` → `cli.read_json_file` / `cli.write_json_file`
- `json.loads(s)` / `json.dumps(d)` → `u.Cli.json_loads` / `u.Cli.json_dumps`
- `yaml.safe_load(open(...))` / `yaml.dump(data, open(...))` → `cli.read_yaml_file` / `cli.write_yaml_file`
- `csv.reader(...)` / `csv.writer(...)` / `csv.DictReader` → `cli.read_csv_file_with_headers` / `cli.write_csv_file`
- `print(...)` (top-level call-site) → `cli.print` / `cli.display_message`
- `sys.exit(code)` → `cli.exit(code)` (context-aware: raises `typer.Exit` inside Typer/Click context, `sys.exit` at process boundary)

### Project-scoped exemptions (documented in audit script)

- **`tomllib` / `tomlkit`**: exempt ONLY in `flext-infra` (workspace pyproject orchestration).
- **`click`**: exempt in Singer SDK boundary files: `flext-tap-*`, `flext-target-*`, `flext-meltano/services/executor_base.py`, `flext-meltano/_protocols/singer.py`, `flext-meltano/tests/unit/test_singer_sdk_adapter.py`.

### `FlextCli<X>` concrete-class imports

Forbidden EVERYWHERE outside `flext-cli/src/` EXCEPT in **MRO namespace extension files** of consumer projects:

- `<projeto>/src/<projeto>/{constants,models,protocols,typings,utilities,settings}.py` may extend the corresponding `FlextCli<Tier>` (e.g., `class MyProjectModels(FlextCliModels)`) — this is the canonical SSOT pattern (cf. skill `flext-mro-namespace-rules`).
- `FlextCli` (the singleton class type) is allowed only inside `if TYPE_CHECKING:` blocks of test helpers needing typed inheritance.

### Mandatory canonical aliases at every call-site

Consumers MUST use:

- `cli` — singleton facade (runtime API)
- `c, m, p, t, u, s, r, d, e, h, x` — namespace aliases (constants, models, protocols, typings, utilities, service base, result, dispatcher, exceptions, handlers, mixins/extras)

Direct concrete imports (`FlextCliFileTools`, `FlextCliFormatters`, `FlextCliSettings`, etc.) are FORBIDDEN. Use `cli.<method>`, `cli.settings`, `cli.new_settings()`.

### Enforcement

- Pre-commit hook: `.pre-commit-config.yaml` workspace-root.
- CI gate: `python .agents/skills/scripts-infra/audit_banned_cli_libs.py` and `python .agents/skills/scripts-infra/audit_flext_cli_concrete_imports.py` — both must return exit code 0.
- Per-project Ruff: `[tool.ruff.lint.flake8-tidy-imports.banned-api]` block in every `pyproject.toml` outside flext-cli/flext-core.
- Skill: `.agents/skills/flext-cli-ssot-enforcement/SKILL.md` documents the decision tree.

### flext-cli MUST NOT invade other projects' domains

flext-cli is a leaf in the dep graph for the CLI domain. It depends ONLY on flext-core. Imports from any other workspace project (`flext-ldap`, `flext-meltano`, `flext-quality`, etc.) are FORBIDDEN inside `flext-cli/src/`.

### Required dependency declaration

Every consumer project that imports from `flext_cli` MUST declare `"flext-cli"` in `[project] dependencies` of its `pyproject.toml`.
