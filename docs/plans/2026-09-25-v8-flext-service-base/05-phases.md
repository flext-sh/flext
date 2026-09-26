# 05 — Phases and steps

<!-- TOC START -->

- [Order and dependencies](#order-and-dependencies)
- [Common steps of every slice](#common-steps-of-every-slice)
- [F0 — Preparation (S0)](#f0--preparation-s0)
- [F1 — Contract core (flext-core)](#f1--contract-core-flext-core)
- [F2 — Fleet tooling](#f2--fleet-tooling)
- [F3 — Kernel desfake (flext-core)](#f3--kernel-desfake-flext-core)
- [F4 — Closure (S10)](#f4--closure-s10)

<!-- TOC END -->

## Order and dependencies

```text
F0 (S0)
 └─ F1 flext-core (serial): S1 → S2 → S2b* → S3 → S4 (core + 7 members, consumers first)
     ├─ F2 tooling:          S6 flext-tests (after S1 merged)
     │                       S5 flext-cli   (after S3 merged)
     │                       S7 flext-infra (after S5 merged)
     │                          → then the core deletes its fake facades (D1)
     └─ F3 flext-core (serial): S8 → S9 (after S4)
F4 (S10) superproject: last
* S2b runs only if its typing spike passes; otherwise D3 goes to the operator.
```

Slices in different repositories may run in parallel when independent; `flext-core` is
always serial. Beads: S0 `flext-4jtcb.8`, S1 `.1`, S2 `.2`, S2b `.9`, S3 `.3`, S4 `.10`,
S5 `.4`, S6 `.5`, S7 `.6`, S8 `.7`, S9 `.11`, S10 `.12`.

## Common steps of every slice

| # | Step | What to do | Evidence on the bead |
|---|---|---|---|
| E1 | Preflight | Fetch `origin/0.12.0-dev`; `gh pr list` for the repo; `bd show` and `--claim`; for `flext-core`, check lane `flext-edcqq` | Open PRs, base SHA, claim |
| E2 | Lane | `git -C <primary> worktree add ~/flext-work/v8-<slice>/<repo> -b <branch> origin/0.12.0-dev`; `make setup` in the lane; read the lane's `make help` | Path, branch, SHA, setup exit |
| E3 | Runtime first | Reproduce the current behavior through the public API and record it | "Before" command and output |
| E4 | Implement at the owner | File by file; repeated patterns become codemod rules (R10/R11), with a checkpoint commit before `make mod` | Diff per file |
| E5 | Tests | Behavioral, through public facades: happy path, failure path, must-not-trigger | Test names |
| E6 | Docs | Docstrings and guides in the same commit | Doc files |
| E7 | Gates | `make gen` ×2 (fixed point), `make fix`, `make fmt`, `make check`, `make test` (slice tests selected) | Exit of every verb |
| E8 | Non-breakage | Code-review graph `status`/`update` then `impact` on changed symbols; in the fleet validation workspace, point the member at the lane commit, `make setup`, then the root `make check` and `make test`, compared with the recorded baseline | Consumer table with exits |
| E9 | Landing | Commit by paths; `make check && git push -u origin <branch>`; PR; CI on the head; threads resolved; merge commit; proof on the merged SHA | PR, merge SHA, CI, proof |
| E10 | Retire | Fetch and `git merge-base --is-ancestor`; delete the remote branch, the worktree and the local branch; close the bead with four sources | Ancestry output, close |

Extra proofs for slices that delete code: LOC delta, and zero uses outside the owner for
every deleted symbol (graph plus fleet search). A foreign red gate is recorded on the PR
and the bead with its owning bead; it is never narrowed or suppressed.

## F0 — Preparation (S0)

1. Plan approved on 2026-09-25; operator working copy in
   `~/.claude/plans/plano-v8-flext-service-base/`.
2. **Fleet validation workspace** (R19), created 2026-09-25:
   - superproject worktree `~/flext-work/v8-fleet/flext`, branch `v8/fleet-validation`
     from `origin/0.12.0-dev` `ec666f2c25`, submodules initialized, never committed;
   - measured fleet state: the superproject records gitlinks for 27 members that their
     `0.12.0-dev` tips do not contain (phase-1 wave WIP, `flext-itpd1.3`), and member
     Makefiles at the tips demand a member-local `.venv` (`flext-x8gn6`, whose fix is in
     that wave);
   - therefore the 27 members stay at their recorded gitlinks and `flext-core`,
     `flext-cli`, `flext-infra`, `flext-tests` at their tips (which contain the recorded
     gitlinks); the workspace index mirrors those HEADs; `make setup` exits 0;
   - baseline: the root `make check` and `make test` at that state, stored under
     `~/tmp/v8/baseline/`; each slice compares against it.
3. **Superproject docs lane** `~/flext-work/v8-docs/flext`, branch
   `docs/v8-service-base-plan`: this plan and ADR-019 (Proposed), gates, PR, merge.
4. **Beads:** renumbered, new beads created, dependencies added; cross-notes on
   `flext-v3mzx`, `flext-edcqq`, `flext-itpd1.3` (gitlink divergence evidence), and the
   epic linked to the ai-hub plan v3 phase 1.1 (`aihub-5j4cw`).

## F1 — Contract core (flext-core)

### S1 — Ports, validated runtime seeds, typed hook, preserved cause

Lane `~/flext-work/v8-s1-ports/flext-core`, branch `feat/v8-s1-service-ports`.

E3 before: `Svc(runtime_settings=<non-Settings object>)` is accepted;
`Svc.model_json_schema()` fails; `r[int].fail("x", exception=ValueError("y")).unwrap()`
raises without `__cause__`; consumer inventory of every runtime option.

E4, in the order set by the adversarial review:

| # | File | Change |
|---|---|---|
| 1 | `_typings/pydantic.py` | `type Port[P] = Annotated[P, SkipJsonSchema()]` with a contract comment, plus tests |
| 2 | `_utilities/model_runtime.py` | Typed `runtime_container.context` instead of `getattr(…, "context", None)` (`:233`) |
| 3 | `model_options.py:66,73`, `model_runtime.py:251`, `registry.py:140-143` | Validated construction instead of `model_copy(update=)` |
| 4 | `_models/service.py`, `_utilities/model_options.py` | After proving zero consumers outside the core, delete `services`, `factories`, `resources`, `container_overrides`, `wire_modules`, `wire_packages`, `wire_classes`, `subproject` with the paths that read them, `validate_wire_packages`, the `getattr` overlay (`:42-57`) and the probes (`:58-64`); rewrite `tests/unit/test_service_bootstrap.py:102-165`; an option with a real consumer stays and gains real validation |
| 5 | `_protocols/service.py` | `@runtime_checkable class RuntimeBootstrapProvider(Protocol)` with the classmethod `runtime_bootstrap_options() -> p.RuntimeBootstrapOptions` |
| 6 | `_utilities/model_options.py` | Typed `match`: options model, validated mapping, or `p.RuntimeBootstrapProvider` (hook read typed) plus the `x` seeds; an unknown source raises `TypeError`; the hook is **not** declared on `x` |
| 7 | `mixins.py`, `_models/service.py` | Remove `SkipValidation`: seeds `t.Port[p.Settings \| None]`, `t.Port[p.Context \| None]` with `exclude=True`; `settings_type` out of the schema; validated `ServiceRuntime` ports; break the registry↔runtime cycle by validating the runtime without the registry, then the final runtime with the validated registry |
| 8 | `_utilities/model_runtime.py` | Delete the guards `:100-103,151-155,225-238`: dispatcher failure propagates with its cause |
| 9 | `_result/unwrap.py` | `raise RuntimeError(msg) from <carried exception>` (R20) |
| 10 | `service.py` | Reject a `t.Port` field whose type is not a plain `@runtime_checkable` Protocol class when the subclass is created; docstring with the port, root and `fetch_global` rules |

E5 tests (`tests/unit/`, `TestsFlext*` classes, test port in the tests' `p`/`m`): a
conforming real adapter is accepted; a non-conforming object raises `ValidationError` on
construction and assignment; a subscripted port type is rejected at class creation;
`fetch_global()` of a port service raises `ValidationError`; the service schema works and
lists only data; the subclass hook decides `settings_type`; an unknown source raises;
`unwrap()` carries `__cause__`.

E6 docs: rewrite `docs/guides/service-patterns.md` from `03-contract.md` §1–4 and §7–9;
delete `docs/guides/dependency_injector_prompt.md` and
`docs/improvements/dependency-injection-audit.md` and relink; fix
`docs/architecture/overview.md:98-100`; align `docs/guides/dependency-injection-advanced.md`;
update `examples/ex_11_flext_service.py` (it uses `subproject`).

E8 non-breakage: the 11 members that use `runtime_settings`, `initial_context` or
`with_settings`, handler consumers (`x` backs `h`), `flext-tests`, and every member suite
through the root `make test`. A consumer passing a non-conforming object is fixed in the
consumer's own lane and merged first (R17); the port is never relaxed.

### S2 — Truthful container

Lane `v8-s2-container` after S1 is merged. Bookkeeping first: `_internal_registrations`
covers services, factories and resources (`container.py:253-263`), internal names are
reserved, one private write path applies the rules. Then empty, duplicate and reserved
registrations raise `e.ValidationError` (messages in `c`); `shared(auto_register_factories=True)`
without a resolvable caller raises; a non-callable in the scan raises. Delete the
string-only dependency_injector bridge (`provide`, `wire`) after the zero-use proof;
remove `SkipValidation` in `_container_parts` (9) and `_dependency_types.py` (3) where a
validatable type exists. Tests include the `scope()` LOGGER regression. Docs:
`dependency-injection-advanced.md`, `service-patterns.md`. Consumers: the core suite,
auth, observability, target-ldap, plugin.

### S2b — Protocol keys and `compose` (conditional)

Spike without a PR: candidate `bind(Port, impl)` / `resolve(Port)` signatures through
`make check` at real call sites (mypy `type-abstract`, pyright, pyrefly). If all three
accept without suppression: one keying scheme across `bind`, `resolve`, `has`, `names`,
`drop`, `dispatcher`; internal names become protocol keys; `FlextService.compose(container)`
fills required `t.Port` fields only; two ports of one Protocol need an explicit argument;
tests and docs. Otherwise record the evidence and ask D3 (recommendation: pure DI only).

### S3 — Lazy operation contract

Lane `v8-s3-operations`. `_models/service.py`: frozen `ServiceOperation` (`name`,
`summary`, `request`). `_utilities/discovery.py`: `service_operations(service_type)`
implementing `03-contract.md` §5 (`inspect.getattr_static`, exclusions, shape checks,
annotation resolution without `eval`, Pydantic model check, errors with operation,
annotation, module and fix, sibling collision and zero-operation failures, per-class
cache). No class-creation check. Tests: a real service with one request operation and
one input-less operation, every invalid shape, `TYPE_CHECKING`-only imports, ports and
`dir(FlextService)` excluded. Docs: "Operations are the API".

### S4 — Truthful `p.Service` (consumers first)

Inventory the 17 sub-protocols in 7 members and what each implements and calls. Member
lanes first: members that use a phantom member declare it in their own protocol (for
example `flext-web` `validate_business_rules`), gated and merged. Then the core trims
`p.Service` to the real surface (settings, container, context, logger, track, execute)
without adding service methods; test `isinstance(real_service, p.Service)` is True;
revalidate the 7 members and merge.

## F2 — Fleet tooling

### S5 — flext-cli `service_routes`

Lane `v8-s5-cli/flext-cli` after S3 is merged. Refresh the lock to the merged core (lock
verb from the lane's `make help`). E3: build a route by hand and confirm that
`result.value` is not printed and `ValidationError` escapes raw today.
`service_routes(service_type, *, provide)` derives routes from the class (kebab name,
summary help, request model or one shared empty `m.Cli` model); the handler obtains the
instance through `provide` at execution. The border turns `ValidationError` into
`e.fail_validation` with the cause; success is rendered. Fail loudly on
`_apply_common_params_to_config` (`part_02:27-29`), `u.Cli.field_default`
(`options_part_02:32-37`), the `str` annotation fallback (`part_01:70-72`) and a required
`exclude=True` request field; review the `invoke_app` catch (`part_03:75-80`). Delete
`_utilities/model_commands.py`, the duplicate `derive_model` and its test after the
zero-use proof. Tests with a real Typer app: valid command exit 0 with the result,
invalid input non-zero with the cause, an input-less operation, and `--help` with no
adapter and no configured environment. Docs: the flext-cli "Service CLI" guide.
Consumers: flext-infra, flext-meltano, flext-quality, flext-web, flext-oracle-oic.

### S6 — flext-tests

Lane `v8-s6-tests/flext-tests` after S1 is merged. Refresh the lock. `base.py`: the hook
stays a classmethod (no `@override`); `test_settings_type` raises `TypeError` naming the
class instead of falling back; `isolated_test_runtime` accepts an explicit
`build: Callable[[], Self]` for services with ports. `_fixtures/settings.py:46-48`:
typed, no `getattr` substitution. Tests include a port service built with a real
adapter. Non-breakage: the root `make test` of the fleet validation workspace.

### S7 — flext-infra, then the kernel without fake facades (D1 = A)

Lane `v8-s7-infra/flext-infra` after S5 is merged. Cross-check the open `flext-infra` PRs
and worktrees first. Templates `api.py.j2`, `cli.py.j2`, `services/ping.py.j2` emit the
contract. Countable detection rules (fixtures, snapshots, `ast-grep test`) for
infrastructure built inside services, `u.PrivateAttr(default_factory=<facade>)`,
`settings or X.fetch_global()` and hand-rolled singletons. Fix `ban-skip-validation`
(`pydantic-boundary.yml:44-48`) for the `Annotated[..., t.SkipValidation]` form; the
`flext_core` exemption dies when the count reaches zero. NS-LAYOUT
(`validate/namespace_validator.py:161-182`) requires `api.py` only when services are
composed and `cli.py` only with a console script and operations. After the infra
merge, a core lane deletes `api.py`, `cli.py`, `base.py`, the empty `services/` (if no
longer required) and the `flext-core` console script; `make gen` regenerates the core
`__init__.py` and, in the superproject, `src/flext/__init__.py`. Tests: the
`codegen new` scaffold in `tmp_path` passes `make check`; rules pass `ast-grep test`;
the core without skeletons passes `make check`.

## F3 — Kernel desfake (flext-core)

Per site: a failing public failure-path test, the cure at the owner, the test green, the
graph-driven consumer revalidation; one commit per owner.

- **S8 batch A:** `_models/cqrs.py:122-129`; `registry.py:196-209`, `:325-332`,
  `:473-485`, `:374-381`, `:120-129`; `mapper_access_part_02.py:81-82` and `mapper.py:98`;
  `_utilities/model.py:69-71`; `flexthandlers_part_07.py:130-138`;
  `context_state.py:38-46,126-134`, `context_lifecycle.py:97-138`, `context_crud.py:103-107`;
  `_utilities/project_metadata.py:55-62`.
- **S9 batch B:** `dispatcher.py:58-80`, `:117-120`; `checker_part_02.py:84-93`;
  `parser_coerce.py:99-107`, `conversion.py:88-108`; `parser_targets_part_02.py:45-63`;
  `logging_config_part_01.py:140-146`; `_decorators/_railway.py:143-185`, `:46-53`.
  Beartype sites stay with `flext-edcqq`; if it is still idle when S9 starts, ask whether
  to adopt it.

## F4 — Closure (S10)

Lane `v8-close/flext`: ADR-019 to ACCEPTED with PR and proof links; this plan's final
state; root guide sources (`using-flext-core.md`, `using-flext-cli.md`) and
`settings-config-canonical-pattern.md` contradictions; member gitlinks to merged tips via
the canonical flow; PR and merge; epic closed with four-source evidence; no open lane or
PR in scope; the validation workspace retired; one adoption bead per member with a
service, with the backlog counted by the S7 detection rules; D2 asked when infra
adoption starts.
