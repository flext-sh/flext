---
name: rules-scripts
description: 'Use when creating or changing Bash or Python automation under `scripts/`; pair it with the path-specific GitHub, Docker, or skill-validator rules outside that tree.'
license: MIT
metadata:
  version: 2.0.0
---
# Script Engineering Rules

## Ownership and entry points

1. Find the canonical Make verb and owning service before editing a script.
2. Add an `Owner-Skill` marker only when the selected enforcement manifest requires it.
3. Keep the script a thin, deterministic adapter to the owning Python service when
   domain logic or structured data exceeds simple shell orchestration.
4. Do not create a second executable path for an existing command.

## Bash baseline

```bash
#!/usr/bin/env bash
# Owner-Skill: .agents/skills/<skill>/SKILL.md
set -euo pipefail

readonly REPO_ROOT="$(git rev-parse --show-toplevel)"
```

- Quote every expansion unless intentional splitting is documented.
- Use arrays for command arguments and `mapfile`/`readarray` for lists.
- Prefer `[[ ... ]]`, arithmetic contexts, `case`, and `printf`.
- Declare function locals with `local` and immutable globals with `readonly`.
- Resolve paths from `REPO_ROOT` or the script directory, not the caller's CWD.
- Use `mktemp -d` plus `trap 'rm -rf "$tmp_dir"' EXIT` for temporary state.
- Send diagnostics to stderr and machine-readable results to stdout.

## Failure and safety contract

- `0`: success; `1`: validation failure; `2`: invalid usage; `3`: infrastructure failure.
- A gate must never turn an expected failure into success with broad `|| true`.
  Capture status explicitly when probing is intentional.
- Validate required commands and arguments before mutation.
- Default to read-only or dry-run. Require an explicit apply flag for mutation.
- Never use `eval`, unquoted command substitution, predictable temp files,
  download-and-execute pipelines, embedded credentials, or secret-bearing tracing.
- Make repeated runs idempotent and output ordering deterministic.

## Python automation

Use Python for structured parsing, concurrency, complex error models, or reusable
workspace services. Keep a typed `main() -> int`, an `if __name__ == "__main__"`
guard, strict annotations, and the same FLEXT facade boundaries as production code.

## Validation

1. Run the safe `--help`, check, or dry-run mode from a non-repository CWD.
2. Exercise success, validation-failure, usage-error, and infrastructure-error exits.
3. Run `shellcheck` when provided by the canonical environment.
4. Run the owning Make gate and a second dry-run to prove idempotence.
5. Verify no secret, absolute developer path, or nondeterministic output was added.

## Enforcement

The canonical `scripts-validation` rule package and `flext-infra` validator own
execution. This skill adds no second rules manifest, parser, scanner, or CLI.
