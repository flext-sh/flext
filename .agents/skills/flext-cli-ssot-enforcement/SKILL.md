---
name: flext-cli-ssot-enforcement
description: Use ALWAYS when working in any flext workspace project to ensure flext-cli SSOT for CLI domain (typer/click/rich/tabulate/process-exec/json/yaml/csv/toml/prompts/output) is not violated. Auto-fail violations.
---

# flext-cli SSOT enforcement

flext-cli is the **single source of truth** for the CLI domain across the entire FLEXT workspace. No other project may invade this responsibility. The only exception is flext-core (which cannot import flext-cli to avoid circular imports).

## Decision tree before writing/editing any .py outside flext-cli/

| Need | Use | Do NOT use |
|---|---|---|
| Print to console | `cli.print(...)` / `cli.display_message(...)` | `print(...)` / `console.print(...)` / `typer.echo(...)` / `click.echo(...)` |
| Exit | `cli.exit(code)` | `sys.exit(code)` / `os._exit` |
| CLI app | `cli.create_app_with_common_params(...)` + `cli.register_result_command(...)` | `typer.Typer()` / `click.Group()` / `argparse.ArgumentParser()` |
| Read/write JSON file | `cli.read_json_file` / `cli.write_json_file` | `json.load(open(p))` / `json.dump(data, open(p, "w"))` |
| Read/write YAML file | `cli.read_yaml_file` / `cli.write_yaml_file` | `yaml.safe_load(open(p))` / `yaml.dump(data, open(p, "w"))` |
| Read/write CSV file | `cli.read_csv_file_with_headers` / `cli.write_csv_file` | `csv.DictReader` / `csv.writer` |
| Read/write TOML file | `cli.read_toml_file` / `u.Cli.toml_load` | `tomllib.load` / `tomlkit.parse` (flext-infra exempt) |
| String JSON parsing | `u.Cli.json_loads` / `u.Cli.json_dumps` | `json.loads` / `json.dumps` |
| Process execution | `cli.run` / `cli.capture` / `cli.run_raw` / `cli.run_checked` / `cli.run_to_file` | direct stdlib `s\w+process` module / shell-based one-liners |
| Prompt user | `cli.prompt` / `cli.confirm` / `cli.prompt_choice` / `cli.prompt_password` | `input()` / `getpass.getpass()` / `typer.prompt` / `click.prompt` |
| Rich/tabulate | `cli.format_table` / `cli.show_table` / `cli.render_panel` / `cli.create_tree` | `from rich import` / `from tabulate import` |
| Capture click.Abort/ClickException | `c.Cli.CliAbortError` / `c.Cli.CliCommandError` | `from click import Abort, ClickException` |
| Auth tokens | `cli.authenticate` / `cli.fetch_auth_token` / `cli.save_auth_token` / `cli.clear_auth_tokens` | manual `Path.read_text` / `Path.write_text` on token files |
| Settings | `cli.settings` (singleton) / `cli.new_settings()` (fresh) / `p.Cli.Settings` (annotation) | `from flext_cli import FlextCliSettings` |
| Logging | `s.logger` (inherited) / `FlextLogger.fetch_logger("name")` | `logging.basicConfig` / `logging.getLogger` |

## Forbidden imports outside flext-cli (audited automatically)

```text
typer, click, argparse, rich, tabulate, colorama, prompt_toolkit, tqdm,
getpass, orjson, ujson, simplejson
process module from stdlib (banned everywhere outside flext-cli/flext-core)
```

`tomllib`/`tomlkit`: banned EXCEPT in flext-infra (workspace pyproject orchestration).

`FlextCli<X>` concrete imports: banned EXCEPT in
`<projeto>/src/<projeto>/{constants,models,protocols,typings,utilities,settings}.py`
for MRO namespace extension (the canonical SSOT pattern).

`FlextCli` (the singleton class) is allowed only inside `if TYPE_CHECKING:` blocks
of test helpers that need to type-hint inheritance.

## Detection commands

```bash
python /home/marlonsc/flext/.agents/skills/scripts-infra/audit_flext_cli_concrete_imports.py
python /home/marlonsc/flext/.agents/skills/scripts-infra/audit_banned_cli_libs.py
```

Both scripts must return exit code 0 (`OK: no ... violations.`) before any commit.
They are wired into pre-commit and `make val` gates.

## Why this matters

1. **Single source of truth**: one place owns the CLI domain. Bug fixes propagate workspace-wide.
2. **Library swap freedom**: replacing Click→Typer→Rich→Textual is contained inside flext-cli.
3. **Consistent error handling**: every CLI op returns `r[T]` (railway pattern via flext-core).
4. **Consistent UX**: every CLI tool in the workspace prints/prompts/formats the same way.
5. **Security**: `cli.run_*` enforces argv list (no shell injection), while ad-hoc process exec may not.
6. **Test isolation**: `cli.new_settings()` and `cli.settings.reset_for_testing()` give deterministic test setup.

## Architectural anchor

flext-cli depends on flext-core only (leaf in the dep graph for CLI domain).
flext-cli is consumed by every other workspace project that needs CLI capabilities.
The ban list is enforced via Ruff `[tool.ruff.lint.flake8-tidy-imports.banned-api]`
in each consumer's `pyproject.toml`, plus the two audit scripts above for the
patterns Ruff cannot statically detect (json./yaml./csv./print/sys.exit at-call-site).
