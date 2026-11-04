# Session record 2026-10-31 — gen-perf / rope cures (flext-side view)

SSOT of the campaign lives in the consumer repo:
`devops-oud-iac/docs/handoffs/20261030-gen-perf-rope-cures.md`. This file records only
the facts that land on flext-side surfaces; do not duplicate the full campaign here.

## Landed (committed)

- **flext-infra `973cac1a5`** — Jinja tuple+list cure that killed gen runs g95 and g96:
  `template_render` serializes `model_dump(mode="json")` (tuples → lists), and
  `module_skeleton.py.j2` built a literal tuple in the no-base branch → `() + []`.
  Template now uses lists; regression test
  `test_generate_module_skeleton_renders_uncomposed_domain` proves it. Regression of
  lane commit `0eefa43158`.
- **rope fork (`~/rope-dc15`, consumer of the generator) committed in two scoped
  commits**: `638147ee` (perf cures C1 `requires_header_bindings` memo — 109.9s→9.0s on
  `_get_names`; C2 `Scope.get_end` memo; C3-b `GlobalScope.get_inner_scope_for_line`
  memo; `LiteralString`/`UnresolvedBase` `__eq__`/`__hash__` by value; PEP 646
  `Unpack[Ts]` support with identity-keyed `_generated` cache) and `485797d7` (WIP
  par-backend: `_assigned` rebinding, `header_end`, `import_layouts`,
  `string_mapping_arguments`, `move.py` — required by flext-infra HEAD; rollback is
  impossible). Rope suite 247/247 in both states.
- **Operator decrees recorded as rules**: `~/agents/rules/ethics/no-preexisting-debt.md`
  (no preexisting failure; `--no-verify` banned; fix-forward); budget/deadline/flock and
  profiling-through-declared-binding were already owned by
  `~/agents/rules/workflow/canonical-commands.md` and `gate-budget.md`.

## In flight (flext-infra tree, commit blocked by the lane's 117 lint findings)

Three cures sitting in `flext-infra` (adopt, don't re-edit): missing import in
`facade_members` (NameError in consumer check); classmethod/contextmanager/staticmethod
stack on `project_captured_sources` (TypeError); renderer `type_set_rules` renamed to
`codemod_type_set_rules` (config declared it, method didn't — all renderers now resolve,
proven by getattr walk).

## Blocking decision pending (lane network owner)

Consumer `make check CI=C` closes all flext gates PASS, but the `post-check`
(`scripts/check_deployment`) dies on a synthetic ssh document: the contract requires a
secret (min_length=1) resolved via oci-vault, and the plugin resolves EAGER at parse →
with the CLI present the SDK heads for `secrets.vaults.check-region-1...` (guaranteed
NXDOMAIN). Suggested canonical cure: an offline resolution boundary in the plugin for
check-time synthetic documents (no rollback of eager). Consumer commits stay staged
until the owner decides.

## Next perf lever (C4)

Post-fork `gen-scope` profile: candidate resolution inside each `find_occurrences` pays
~64ms of inference cascata (5,459 unique inferences); first lever to measure is a memo
keyed on `(pymodule, offset) → pyname` across the occurrence searches. Measure with
`GEN_PROFILE=1 make gen-scope WHAT=lazy-init SCOPE=self` in the consumer, comparing the
same operation only.
