# Prompt: Continue MRO Deduplication in flext-core (and propagate)

**Audience**: Claude Code or any agent continuing this refactor.
**Working directory**: `/home/marlonsc/flext`
**Authorization scope**: ONLY the changes spelled out here. STOP and ask the user before any deviation.
**Date written**: 2026-04-30 (anchor any "today" claims to this date).

---

## 1. What this prompt is for

You are continuing a deduplication refactor inside `flext-core`. The goal is to remove logic duplication between Tier 3 (`_models/`) and Tier 4 (`_utilities/`) classes by using **real Python MRO inheritance**, not by writing wrappers.

The user has already burned a session on a wrong approach (wrappers and `staticmethod()` aliases). They are explicit that those are still duplication and are forbidden. They have ALSO already burned a session on an over-eager attempt to push this refactor onto the foundational pydantic facade, which broke ruff/pyrefly across the workspace. **Both failure modes are listed below — read §3 carefully before touching anything.**

## 2. State of the workspace at start

Last known good state (verify with `git status` before starting):

| File | Change | Status |
|---|---|---|
| `flext-core/src/flext_core/_models/project_metadata.py` | `class_stem` property delegates to `derive_class_stem` static method (1 source of truth on the model namespace) | DONE |
| `flext-core/src/flext_core/_utilities/project_metadata.py` | `class FlextUtilitiesProjectMetadata(mpm):` — real MRO inheritance from Tier 3, no local wrappers | DONE |
| `flext-core/src/flext_core/_models/_context/_data.py` | `_coerce_scalar_mapping` static helper consolidates 4 copies of the scalar-or-str dict comprehension | DONE |
| `flext-core/src/flext_core/_utilities/pydantic.py` | **REVERTED** by user — DO NOT TOUCH | LEAVE ALONE |

Run this first to confirm:

```
cd /home/marlonsc/flext/flext-core
/home/marlonsc/flext/.venv/bin/ruff check src/
/home/marlonsc/flext/.venv/bin/pyrefly check src/ 2>&1 | tail -3
/home/marlonsc/flext/.venv/bin/pytest tests/ -x -q 2>&1 | tail -5
```

If any of these are not clean, STOP and fix the regression before proceeding.

## 3. The two failure modes — internalize these

### 3.1 Forbidden re-exposure forms (still duplication)

```python
# ❌ One-line wrapper
@staticmethod
def pascalize(slug: str) -> str:
    return mpm.pascalize(slug)


# ❌ staticmethod() alias
pascalize = staticmethod(mpm.pascalize)


# ❌ Re-implementing the same logic
@staticmethod
def pascalize(slug: str) -> str:
    parts = slug.replace("-", "_").split("_")
    return "".join(part[:1].upper() + part[1:] for part in parts if part)
```

The user rejected ALL THREE. The correct re-exposure is real Python MRO inheritance:

```python
# ✅ Real MRO — Tier 4 utility inherits Tier 3 model namespace
class FlextUtilitiesProjectMetadata(FlextModelsProjectMetadata):
    """Tier 3 static methods flow through real Python MRO. No wrappers."""

    # Only NEW Tier 4 methods live here.
```

Then `FlextUtilities` composes `FlextUtilitiesProjectMetadata` via its existing inheritance list, and `u.pascalize` resolves naturally through the MRO chain.

### 3.2 The MRO foundational-facade trap

DO NOT apply the inheritance refactor to a Tier 3 namespace that is already woven into the `FlextModels` / `FlextUtilities` MRO graph. Specifically forbidden parent classes for Tier 4 inheritance refactors:

- `FlextModelsPydantic` (mp) — base for every Pydantic model in the workspace
- `FlextModelsBase` — base of the model facade
- `FlextModelsNamespace` — already a base of `FlextUtilities`
- Anything inheriting `pydantic.BaseModel` directly or via Pydantic's `ModelMetaclass`

**Why these break:** `FlextUtilities` already inherits `FlextModelsNamespace` (see `flext-core/src/flext_core/utilities.py:65`). Adding `mp` (or any class already in the model facade chain) into a sibling utility creates duplicate paths in the resolved MRO graph. ruff/pyrefly then disagree about attribute resolution across every file that types against the model facades — the user observed this and reverted.

**Concrete heuristic — apply BEFORE writing any `class FlextUtilitiesX(FlextModelsY):`**:

1. Open `flext-core/src/flext_core/models.py`. Is `FlextModelsY` listed in the base list of `FlextModels`? If YES → DO NOT inherit it from a utility. STOP.
2. Open `flext-core/src/flext_core/utilities.py`. Is anything listed there a transitive subclass of `FlextModelsY`? If YES → DO NOT inherit it from a utility. STOP.
3. Run a quick ancestor check:

   ```
   /home/marlonsc/flext/.venv/bin/python -c "
   from flext_core import FlextModels, FlextUtilities
   from flext_core._models.<your_target> import <FlextModelsY>
   print('mp_in_FlextModels:', issubclass(FlextModels, <FlextModelsY>))
   print('mp_in_FlextUtilities:', issubclass(FlextUtilities, <FlextModelsY>))
   "
   ```

   If EITHER prints `True`, the parent is foundational. STOP.
4. Only when both are `False` is the parent class an isolated namespace and safe to inherit from a sibling utility.

`FlextModelsProjectMetadata` passed both checks (isolated namespace) — that is why it worked. `FlextModelsPydantic` fails check #1 — that is why it broke.

## 4. The pattern of acceptable refactors

A candidate must satisfy ALL of these:

1. The Tier 3 namespace is small (≤ ~200 lines) and self-contained: no metaclass, no `__init_subclass__`, no Pydantic models that are themselves used as facade bases elsewhere.
2. The Tier 3 namespace is NOT in the `FlextModels` MRO base list (verify per §3.2).
3. The Tier 4 utility currently has either a wrapper, a `staticmethod()` alias, OR re-implements the same logic — i.e. a real duplication exists.
4. The Tier 4 utility is composed into `FlextUtilities` via a single base entry (typical case). If it is composed into multiple facades, validate each independently.
5. After the change, `class FlextUtilitiesX(FlextModelsY):` does NOT introduce any class that already appears in the MRO graph of `FlextUtilities`.

If even one of these is not satisfied, the candidate is unsafe — leave the duplication alone and document why in `feedback_*` memory.

## 5. The execution protocol — per candidate

You execute one candidate at a time. No batching. After each candidate the workspace must be green; otherwise revert just that candidate (Edit-tool reverse, never `git checkout`).

### 5.1 Discovery

1. Pick one Tier 4 utility module under `flext-core/src/flext_core/_utilities/*.py`.
2. Read it end-to-end. Identify any of: wrappers (`return mp_or_other.method(...)` one-liners), `staticmethod(...)` aliases, or duplicated logic that exists in a Tier 3 model. Use Grep on the suspected method name to find the Tier 3 owner.
3. If you find no duplication, move to the next utility module. Do NOT invent refactors.

### 5.2 Safety checks (mandatory, in order)

Run all four BEFORE editing:

```bash
cd /home/marlonsc/flext/flext-core

# 1. Confirm Tier 3 candidate parent is isolated
/home/marlonsc/flext/.venv/bin/python -c "
from flext_core import FlextModels, FlextUtilities
from flext_core._models.<MODULE> import <PARENT_CLASS>
print('in_models:', issubclass(FlextModels, <PARENT_CLASS>))
print('in_utilities:', issubclass(FlextUtilities, <PARENT_CLASS>))
"

# 2. Snapshot current ruff/pyrefly state
/home/marlonsc/flext/.venv/bin/ruff check src/ > /tmp/ruff-before.txt 2>&1
/home/marlonsc/flext/.venv/bin/pyrefly check src/ 2>&1 | tail -3 > /tmp/pyrefly-before.txt

# 3. Confirm pytest baseline
/home/marlonsc/flext/.venv/bin/pytest tests/ -x -q 2>&1 | tail -3 > /tmp/pytest-before.txt

# 4. Identify all callers across the workspace
cd /home/marlonsc/flext
grep -rn "<METHOD_OR_CLASS_NAME>" --include="*.py" \
  | grep -v ".venv\|_archived\|__pycache__\|.bak"
```

If step 1 prints `True` for either line, ABORT this candidate. If steps 2-3 are not clean, fix the regression first. Step 4 gives you the propagation surface.

### 5.3 The edit

Make ONE atomic change: convert `class FlextUtilitiesX:` to `class FlextUtilitiesX(<Tier3Parent>):` and DELETE the duplicated wrappers/aliases/reimplementations in the same edit. Do not change anything else in this step (no docstring polishing, no signature edits, no scope creep).

### 5.4 Local validation

```bash
cd /home/marlonsc/flext/flext-core
/home/marlonsc/flext/.venv/bin/ruff check src/<EDITED_FILE>
/home/marlonsc/flext/.venv/bin/pyrefly check src/<EDITED_FILE> 2>&1 | tail -3
/home/marlonsc/flext/.venv/bin/python -c "
from flext_core import FlextUtilities as u, FlextModels as m
# Smoke-test: every public symbol that used to be a wrapper still resolves.
assert callable(u.<METHOD>)
assert callable(m.<METHOD>)
print('symbols resolve via MRO')
"
```

### 5.5 Whole-project validation (mandatory — the pydantic.py mistake came from skipping this)

```bash
/home/marlonsc/flext/.venv/bin/ruff check src/
/home/marlonsc/flext/.venv/bin/pyrefly check src/ 2>&1 | tail -3
/home/marlonsc/flext/.venv/bin/pytest tests/ -x -q 2>&1 | tail -5
```

All three must show ZERO errors / ZERO failures. If ANY error appears that did not exist in the snapshot from §5.2, **revert the edit** (use Edit tool reverse — never `git checkout`) and document the candidate as `UNSAFE` in `feedback_*` memory with the observed errors.

### 5.6 Cross-project propagation

The change is internal to flext-core (you only changed *how* the symbol is exposed, not the symbol itself), so consumers should be unaffected. But verify:

```bash
# Pick a representative consumer for each tier
cd /home/marlonsc/flext/flext-cli
/home/marlonsc/flext/.venv/bin/pyrefly check src/ 2>&1 | tail -3
/home/marlonsc/flext/.venv/bin/pytest tests/ -x -q --co 2>&1 | tail -3   # collection only

cd /home/marlonsc/flext/flext-infra
/home/marlonsc/flext/.venv/bin/pyrefly check src/ 2>&1 | tail -3

cd /home/marlonsc/flext/flext-ldap
/home/marlonsc/flext/.venv/bin/pyrefly check src/ 2>&1 | tail -3
```

If any consumer regresses, the change is NOT propagation-safe. Revert and document.

### 5.6.1 If you discover a CALLSITE that uses the old wrapper signature

Sometimes the wrapper had a different signature than the Tier 3 method (extra normalization, different defaults). In that case the inheritance refactor changes observable behavior. If your discovery in §5.2 step 4 found such call sites, do NOT silently change behavior. Either:

(a) Restore the normalization in the Tier 3 method itself (push the logic up — Tier 3 becomes the SSOT for the union of behaviors), then inherit cleanly. This requires updating all callers' expectations, and the Tier 3 method's tests.

(b) Mark the candidate as UNSAFE because the wrapper had load-bearing behavior that cannot be cleanly merged.

### 5.7 Commit boundary

After §5.5 and §5.6 are both green, that candidate is done. Move to the next. Do NOT bundle multiple candidates into one change set — each must be independently reversible.

## 6. Hard rules — never break

These come from `AGENTS.md`, `CLAUDE.md`, and explicit user feedback in memory:

1. **Never use `git checkout`/`git restore`/`git reset` to revert.** Use the Edit tool to reverse changes. The user is explicit (`feedback_never_git_checkout_restore.md`).
2. **Never use `# type: ignore`, `# pyrefly: ignore`, `# noqa`** to silence errors. Fix the root cause (`feedback_no_lint_ignore_hints.md`).
3. **Never bundle scope creep** into a refactor commit. One candidate, one change.
4. **Never add new helpers, wrappers, or aliases** in `_utilities/`. The MRO inheritance IS the deduplication mechanism.
5. **Always validate with the flext venv** at `/home/marlonsc/flext/.venv/bin/`, not project-local venvs.
6. **Net LOC must be negative** per change. If you find yourself adding lines, you are doing it wrong.
7. **No facade-to-facade same-project imports** at runtime (see `.agents/skills/flext-mro-namespace-rules/SKILL.md`).

## 7. Read these files before starting (in order)

1. `/home/marlonsc/flext/AGENTS.md` — §0 (startup law), §2.3 (MRO composition), §3.1 (SUPREME LAW), §3.5 (Legacy extermination), §3.8 (Verification)
2. `/home/marlonsc/flext/.agents/skills/flext-mro-namespace-rules/SKILL.md` — full
3. `/home/marlonsc/flext/.agents/skills/flext-import-rules/SKILL.md` — full
4. `~/.claude/projects/-home-marlonsc-flext/memory/feedback_real_mro_inheritance_no_wrappers.md` — the rule + caveat that came from this session
5. `~/.claude/projects/-home-marlonsc-flext/memory/feedback_never_git_checkout_restore.md`
6. `~/.claude/projects/-home-marlonsc-flext/memory/feedback_no_lint_ignore_hints.md`
7. `~/.claude/projects/-home-marlonsc-flext/memory/feedback_zero_errors_fix_forward.md`

## 8. Initial candidate scan

Start with these files, in this order. They are the most likely to contain a project_metadata-style isolated duplication. Do NOT touch the listed unsafe ones.

### 8.1 Likely safe candidates (still must pass §3.2 ancestor check)

- `flext-core/src/flext_core/_utilities/text.py` ↔ any Tier 3 text/string namespace
- `flext-core/src/flext_core/_utilities/conversion.py` — does it duplicate any model-side coercion helpers?
- `flext-core/src/flext_core/_utilities/enum.py` ↔ any enum-related Tier 3 namespace
- `flext-core/src/flext_core/_utilities/checker.py` ↔ Tier 3 checker/validator namespace
- `flext-core/src/flext_core/_utilities/discovery.py` ↔ Tier 3 discovery model

### 8.2 Definitely UNSAFE — DO NOT TOUCH

- `flext-core/src/flext_core/_utilities/pydantic.py` — already reverted by user, foundational
- `flext-core/src/flext_core/_utilities/model.py`, `model_runtime.py`, `model_options.py` — all in the foundational model graph
- `flext-core/src/flext_core/_utilities/context*.py` — context is foundational state
- `flext-core/src/flext_core/_utilities/logging_*.py` — logger MRO is intricate
- `flext-core/src/flext_core/_utilities/enforcement*.py` — already a heavily refactored hot zone
- `flext-core/src/flext_core/_utilities/_beartype/` — runtime type-checking, leave it
- `flext-core/src/flext_core/_utilities/guards*.py` — type guards are foundational

When in doubt, classify as unsafe and skip.

## 9. Reporting back

After every candidate (whether applied or skipped):

- If applied: report the file, the parent class, lines deleted, ruff/pyrefly/pytest counts before/after.
- If skipped: report the file, the candidate parent class, and which §3.2 check it failed (or which §4 criterion it violated).

Keep reports short — one paragraph per candidate, no narrative prose.

## 10. Stop conditions

Stop and ask the user:

- After every 3 successful candidates (mid-checkpoint).
- The first time any §5.5 whole-project validation regresses (with the reverted state preserved).
- If a candidate would change observable behavior (§5.6.1 case b).
- If you cannot find any more safe candidates after scanning all of §8.1.

Do not continue past these checkpoints autonomously.

---

## Appendix A: Reference — what was done in the seeding session

Two successful refactors and one failed one. Use them as templates / anti-templates.

**Successful #1 — `flext-core/_models/project_metadata.py`:**
- The `class_stem` property used to inline-implement the same logic as the (already-existing) `derive_class_stem` static method on the same namespace. Replaced the body with `return FlextModelsProjectMetadata.derive_class_stem(self.name)`. Net –6 LOC, single source of truth on Tier 3.

**Successful #2 — `flext-core/_utilities/project_metadata.py`:**
- The Tier 4 utility had its own `pascalize` and `derive_class_stem` static methods that re-implemented Tier 3's logic. Converted `class FlextUtilitiesProjectMetadata:` → `class FlextUtilitiesProjectMetadata(FlextModelsProjectMetadata):` and deleted both methods. The inherited static methods now resolve via real Python MRO. `u.pascalize` and `u.derive_class_stem` continue to work; `m.pascalize` and `m.derive_class_stem` continue to work; both routes hit the same implementation. Net –24 LOC.

**Failed — `flext-core/_utilities/pydantic.py`:**
- Attempted the same pattern with `class FlextUtilitiesPydantic(FlextModelsPydantic):`. This broke ruff/pyrefly across the workspace because `FlextModelsPydantic` is already in the `FlextModels` MRO chain (and therefore transitively in `FlextUtilities` via `FlextModelsNamespace`). The MRO graph collapsed into duplicate paths. The user reverted via the Edit tool. **Lesson encoded in §3.2.**

**Bonus — `flext-core/_models/_context/_data.py`:**
- Not an MRO refactor, but a related dedup: 4 copies of `{k: str(val) if not isinstance(val, (str, int, float, bool)) else val for k, val in items}` collapsed into a single `_coerce_scalar_mapping` static helper on the namespace. Net –14 LOC. This kind of helper-extraction is OK when the helper stays scoped to its owning namespace and is not just re-exposing an already-existing root primitive.
