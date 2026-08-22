# FLEXT Quality

FLEXT Quality is the unified orchestration platform for Claude Code tooling in the FLEXT ecosystem. It combines a YAML-
driven declarative rules engine, Claude Code hook management, an MCP server (tools and resources), and integrations for
Claude context, memory, and code execution behind one railway-oriented facade and CLI.

## Status & health

- **Version**: 0.20.0-dev
- **Python**: 3.13+ only
- **Project class**: platform (consumes `flext-core` and `flext-cli`)
- **Facade**: `from flext_quality import quality` — the process-wide `FlextQuality` singleton
- **CLI**: `flext-quality` console script (`flext_quality.services.cli:main`)
- **Short aliases**: `c`, `m`, `p`, `r`, `t`, `u` plus operational `s`, `d`, `e`, `h`, `x`, and `settings`

### Quality signals

- Lint, type-check, security, and tests run through the canonical `make` verbs; current status is produced by the gates,
  not restated here.
- Run `make check PROJECT=flext-quality` (lint + type-check) and `make check` for the full gate chain.

## Quick start

```bash
pip install flext-quality
```

```python
from pathlib import Path

from flext_quality import quality

rules = quality.load_rules(Path("rules/default.yaml"))
if rules.success:
    u.Cli.print(f"{len(rules.value)} rules loaded")

status = quality.fetch_status()
```

The facade also exposes `execute_hook(...)`, `process_stdin_hook()`, `format_hook_output(...)`,
`fetch_hook_config_json()`, `load_rules_from_config()`, and `validate_configuration()` — the operations the CLI and the
Claude Code hook pipeline drive. The `flext-quality` command runs the same flows from the shell, including stdin-based
hook processing.

## Architecture & modules

- **Facade**: `api.py` defines `FlextQuality` over `FlextQualityServiceBase`, publishing the `quality` singleton;
  `cli.py` and `services/cli.py` implement the command surface with `main(args)` entry points.
- **Rules engine** (`rules/`): `FlextQualityRulesEngine` validates against declarative YAML rule definitions loaded by
  `FlextQualityRulesLoader`, with `validators` for the individual checks; rules are data (`m.Quality.RuleDefinition`
  models), not code.
- **Hooks** (`hooks/`): `FlextQualityHookManager` orchestrates Claude Code hooks over the `FlextQualityBaseHook`
  contract.
- **MCP** (`mcp/`): `FlextQualityMcpServer`, `FlextQualityMcpTools`, and `FlextQualityMcpResources` expose the platform
  through the Model Context Protocol.
- **Integrations** (`integrations/`): `claude_context`, `claude_mem`, `code_execution`, and `mcp_client` adapters for
  the Claude tooling ecosystem.

### Key architectural patterns

- **Declarative rules as data**: rule definitions are YAML files validated into Pydantic models; the engine is a generic
  evaluator, so new rules never require new detector code.
- **Railway everywhere**: rule loading, hook execution, and status reporting return `r[T]`; the CLI maps failures to
  exit codes at the boundary only.
- **Service-base composition**: `FlextQuality` and `FlextQualityCli` build on the `s` service base from `flext-core`,
  keeping state in private attributes and the public surface uniform.
- **Pydantic 2-way models**: rule definitions, hook payloads, and MCP messages are `m.Quality.*` models that round-trip
  through `model_validate` / `model_dump`.

## Testing & quality

- `make check PROJECT=flext-quality` — Ruff + type-check on the project lane.
- `make test PROJECT=flext-quality` — unit and integration suites through the shared `flext-tests` helpers.
- `make check` — full workspace validation chain (lint, types, security, tests, docs).
- Typing is strict (no `Any`/`object`); all owned payloads are `m.Quality.*` Pydantic models and all fallible paths
  return `r[T]`.

## Resources

- [Project README](../../flext-quality/README.md)
- [Project catalog](generated/catalog.md) entry and generated API reference under `docs/api-reference/generated/flext-
  quality.md`
- Project documentation under `flext-quality/docs/`
- Related projects: `flext-core`, `flext-cli`, `flext-observability`, `flext-web`, `flext-infra`

## Support & issues

- GitHub issues: <https://github.com/flext-sh/flext-quality/issues>
- Discussions: <https://github.com/flext-sh/flext-quality/discussions>
- Follow the workspace `AGENTS.md` and the project's own `AGENTS.md` before proposing doc or code changes so this page
  stays aligned with the portal.
