# ADR-032 — Host-Wide Admission for Heavy Gates

<!-- TOC START -->

- [Context](#context)
- [Decision](#decision)
- [Queue contract](#queue-contract)
- [Repeat limit for full-weight runs](#repeat-limit-for-full-weight-runs)
- [Fail early](#fail-early)
- [Capacity and host pressure](#capacity-and-host-pressure)
- [Consumers](#consumers)
- [Consequences](#consequences)

<!-- TOC END -->

- **Status:** ACCEPTED — operator plan 2026-11-12, host memory containment
  (ai-hub epic `aihub-pxu63`, slice `aihub-pxu63.6`)
- **Date:** 2026-11-12
- **Scope:** every generated FLEXT Make surface (`flext-infra` template
  `templates/project/base/Makefile.j2`) and every external consumer that starts a
  heavy gate tool directly (ai-hub post-edit hooks)
- **Complements:** ADR-025 (fleet toolchain), ADR-029 (one complete cycle per
  slice)

## Context

One developer host runs many agent sessions, each with its own lane. On
2026-11-12 the host (20 cores, 64 GiB RAM) reached load 70–94 with swap at
51/61 GiB. The kernel killed desktop clients to free memory. One measured cause is
concurrent heavy gates from different lanes: one Mypy run over a FLEXT project
uses about 4 GiB. Nothing bounds how many start at once. Each generated verb
bounds its own wall time (`timeout`), memory (`prlimit`) and cache (the Mypy cache
lock). It has no view of the gates other checkouts are running.

`~/.gc/gate-slots/slot-{0,1}.lock` are leftovers from Gas City's own push-gate
semaphore (`gascity/scripts/push-gate-lock-lib.sh`), written when the global
`~/.gc` was taken for a city root. They are not a FLEXT contract and FLEXT does
not read them.

## Decision

1. **One owner, one process.** `flext-infra` owns heavy-gate admission: a typed
   utility (`u.Infra` gate admission) and its configuration
   (`Infra.gate_admission` in `config/infra.yaml`). The heavy route (`workspace
   check`, `workspace tests`, `workspace tests-full`, `codegen generate`,
   `refactor mod`) admits itself in its own process, at the CLI dispatcher,
   before any work. No wrapper process and no consumer re-implements the queue.
2. **The budget starts at admission.** Each heavy route's wall-time budget is
   declared in `Infra.gate_admission` and armed by the route after it is
   admitted, so time spent queued never counts against it. The generated Make
   recipes carry no `timeout` prefix for these verbs. On expiry the route stops
   its owned children through the flext-cli process supervisor and exits 124,
   the status `timeout(1)` gave before. `setup` is not admitted: it installs
   flext-infra, the admission owner.
3. **FIFO, no retries, no skips.** A waiter is admitted only when a slot is free
   and no live ticket is ahead of it. A Make verb waits until it is admitted and
   prints its position and the current holders when it starts waiting and each
   time either changes. A refused or failed admission terminates the verb with
   its cause. Nothing is retried and nothing passes as green without running.
4. **Liveness and TTL reclaim slots.** A dead holder's slot is freed when the
   next waiter looks at the queue. A holder that stops heartbeating for longer
   than the TTL is reclaimed. A reclaimed holder that wakes up later fails loud.
5. **Nesting is inherited, never re-queued.** A gate started inside an admitted
   gate runs under its ancestor's ticket and does not queue again.

## Queue contract

- **Location:** `$XDG_STATE_HOME/flext/gate-admission/`, or
  `$HOME/.local/state/flext/gate-admission/` when `XDG_STATE_HOME` is unset.
  There is one queue per user and host, shared by every checkout and lane.
- **Serialization:** one exclusive `flock(2)` on `queue.lock` covers every
  read-modify-write of the ticket set.
- **Ticket:** `<sequence>.json` holds the monotonic sequence number, pid, gate
  name, repository, enqueue time, admission time and last heartbeat. Its
  content is diagnostic. Admission decisions read only the sequence number, the
  admission state, the heartbeat and the liveness lock.
- **Liveness:** each ticket owner holds an exclusive non-blocking `flock(2)` on
  `<sequence>.json.lock` for its whole life. If another process can take that
  lock, the owner is dead (normal exit, failure, crash or kill alike), and the
  ticket is removed. Lock descriptors are close-on-exec, so a leaked
  descendant never keeps a slot alive.
- **TTL:** the owner refreshes its heartbeat every `heartbeat_seconds`. A live
  lock whose heartbeat is older than `ttl_seconds` means a stopped or frozen
  holder. Its ticket is reclaimed and the reclaiming waiter reports that on
  stderr. When the stalled owner's heartbeat finds its ticket gone, the route
  stops its owned children and exits non-zero.
- **Nesting:** an admitted route exports `FLEXT_GATE_ADMISSION_TICKET` to its
  children. A nested heavy route accepts the ticket only if it exists, is
  admitted and its liveness lock is held, and then neither queues nor arms a
  second budget. Otherwise the nested admission fails loud.

## Repeat limit for full-weight runs

The queue bounds how many heavy gates run at once. It does not stop one agent
from running the full `make check`, `make mod` or `make tests-full` after every
edit, which keeps the slots busy all day. The admission owner therefore also
limits how often the full-weight form of a verb runs in one checkout
(operator order 2026-11-13).

- **Ledger:** every full-weight run that completes with exit 0 appends one
  record to `history/<checkout-digest>.jsonl` in the queue directory, under the
  queue lock: verb, selection, checkout root, admission time and finish time.
- **Failures never count.** A run that fails, is refused, times out or is
  killed writes no record, so it never starts or extends a window. Failing
  early is cheap by the fail-early contract below, and the corrected run is
  always admitted.
- **Rule:** a full-weight request for a checkout is refused before it queues
  when the same verb succeeded in that checkout less than its window ago. The
  refusal is a failure (exit 75, never a pass, never a silent downgrade). It
  names the earlier run, the time left in the window and the lighter command.
- **Full-weight forms, windows and lighter forms** (declared in
  `Infra.gate_admission.repeat`):

  | Full-weight (limited) | Window | Lighter form (not limited by this rule) |
  | --- | --- | --- |
  | `make check` | 30 min | `CHECK_PHASE=primary make check` |
  | `make tests-full` | 60 min | `make tests` (Testmon selection) |
  | `make mod` without `LAWS`/`RULES` | 120 min | `make mod` with `LAWS` or `RULES` |
  | `make mod` with the same `LAWS`/`RULES` selection | 5 min | a different selection |

  Lighter forms still queue for a slot like any heavy gate.
- **Not limited:** CI runners (`CI=Y`), and the generated pre-push hook, which
  runs the full matrix once per push by contract. `gen` and `gen-scope` are not
  limited: they are required after every source change of a generator input.

## Fail early

A heavy verb must fail in its first seconds when it is going to fail, not
minutes in (operator order 2026-11-13). Measured on 2026-11-13: `make check`
reported 11 lint findings after 1.7 s and still ran every other gate for
669 s, because the prerequisite phase's failure does not stop the later phases
unless `fail_fast` is set, and its default is false.

- **Preflight first.** Before queueing and before any child starts, a heavy
  route validates everything it can decide without running a tool: its
  arguments and selection, the repeat limit, the configuration and the
  presence of every executable its gates need. A preflight failure exits
  before a slot is taken.
- **Cheapest evidence first.** Gates run in phases ordered by declared budget.
  The prerequisite phase (`check_prerequisite_gates`: lint, pyrefly) runs
  alone. Any finding or failure in a phase ends the verb before the next,
  slower phase starts. The remaining gates are reported as not executed,
  never as passed.
- **One slow gate never hides another's verdict.** Within the final phase the
  long gates (mypy, pyright, duplication, codemod) start only after every
  faster gate of that phase has passed.
- **Same law for tests and mod.** `tests` and `tests-full` already stop at the
  first failure (`max-failures: 1`); collection and selection errors must
  surface before the suite starts. `mod` validates its selection and catalog
  before it plans any rewrite.

## Capacity and host pressure

- `capacity.normal` (2) and `capacity.high` (1) are declared in
  `Infra.gate_admission`. Capacity is checked again at every admission
  decision. Running holders are never preempted. When capacity drops, new
  admissions wait until the running holders fall below it.
- The pressure level is produced by the host-budget owner (ai-hub
  `aihub-pxu63.5`), not measured again by flext-infra. The owner publishes an
  atomic JSON snapshot `{"level", "observed_at", "valid_seconds"}`, and its path
  reaches flext-infra in `FLEXT_GATE_ADMISSION_PRESSURE_FILE`. The variable's
  explicit absence (CI runners, hosts without a host-budget owner) selects
  `capacity.normal`. A declared snapshot that is missing, malformed, unknown or
  older than `valid_seconds` stops the admission with its cause.
- `high` and `critical` both select `capacity.high`. The host-budget owner's
  critical-pressure spawn block applies before this queue is reached.

## Consumers

- **Generated Make verbs:** `flext-infra` regenerates every consumer Makefile
  from the template. Consumers repin flext-infra and run `make gen` to reach the
  fixed point.
- **ai-hub post-edit gates (`python_gates`):** the heavy tools (mypy, pyrefly,
  pytest) acquire a ticket through the same flext-infra utility. Their wait is
  bounded by the hook's own tool timeout. When the wait expires, the hook
  reports the tool as `not executed: admission queue full` with the current
  holders. It is never reported as a pass. Agents' direct tool invocations are
  already denied by the ai-hub bash guard (`BG-EXEC-010`, `BG-EXEC-011`).

## Consequences

- With the declared capacity, two lanes' `make check` runs queue instead of
  overlapping, and two 4 GiB Mypy runs from different lanes never start
  together.
- A verb may wait a long time behind other gates. The wait is visible and
  names the holders, and it never turns into a timeout failure.
- Gas City's push-gate semaphore stays a separate owner for Gas City's own Go
  suites. The stale `~/.gc/gate-slots` files belong to Gas City and are not
  part of this contract.
