# FLEXT CLI

<!-- TOC START -->

- [Status & health](#status-health)
- [Quick start](#quick-start)
- [Architecture & modules](#architecture-modules)
  - [Layering policy](#layering-policy)
  - [Core modules & responsibilities](#core-modules-responsibilities)
- [Key features](#key-features)
- [Quality & compliance](#quality-compliance)
- [Resources & references](#resources-references)
- [Support & contributions](#support-contributions)
<!-- TOC END -->

FLEXT CLI is the production-ready command-line foundation that wires Click, Rich, and Tabulate behind the FlextResult/Railway discipline so every downstream project shares the same CLI contracts, configuration patterns, and output helpers.

## Status & health

- **Version**: 0.10.0 (October 2025)
- **Python**: 3.13+ only
- **Production readiness**: 32+ projects rely on this unified CLI surface
- **Tests**: 1 016 passing (see `reports/pytest/`) with zero pytest failures
- **Coverage**: 96%+ per `reports/coverage-scan-*` snapshots
- **Quality gate**: `make validate` (ruff + pyrefly + bandit + pytest + coverage + docstring checks)
- **Type safety**: Pyrefly strict mode + MyPy strict mode pass, `Any`, `cast`, and `# type:` ignores are forbidden

## Quick start

```bash
# install for day-to-day work
poetry add flext-cli
# or for experiments
pip install flext-cli
```

```python
from flext_cli import FlextCli
from flext_core import FlextResult

cli = FlextCli()

result = (
    cli.file_tools.read_json_file("config.json")
    .flat_map(lambda cfg: cli.config.validate(cfg))
    .map(lambda cfg: cli.formatters.print("Config loaded", style="green"))
)

if result.is_failure:
    cli.formatters.print(f"Config error: {result.error}", style="red")
```

Use `FlextCli.create_table`, `file_tools`, and `prompts` for the ready-made helpers described in `docs/getting-started.md`, `docs/api-reference.md`, and `docs/architecture.md` inside the project.

## Architecture & modules

### Layering policy

- **Tier 0**: `constants.py`, `typings.py`, `protocols.py` define the foundation constants, namespace aliases, and protocols imported only by lower tiers.
- **Tier 1**: `models.py` and `utilities.py` expose Pydantic models and helper facades (`FlextCliModels`, `FlextCliUtilities`) that re-export flext-core short aliases (`m`, `u`).
- **Tier 2**: `cli.py`, `formatters.py`, `file_tools.py`, `prompts.py`, and `tables.py` provide the Click/Rich/Tabulate abstractions (only `cli.py` imports Click, only `formatters.py`/`tables.py` import Rich/Tabulate).
- **Tier 3**: `services/*.py` and `api.py` compose the CQRS services, command execution, authentication, and the `FlextCli` facade that downstream projects depend on.

### Core modules & responsibilities

- `FlextCli` (`api.py`): single facade exposing `formatters`, `file_tools`, `prompts`, `output`, `command` helpers and the authentication context.
- `services/cmd.py`: command execution service with FlextService wiring.
- `services/output.py`: output management with Rich + Tabulate wrappers.
- `file_tools.py`: JSON/YAML/CSV helpers with railway-oriented builders.
- `prompts.py`: interactive prompt, confirm, choice APIs.
- `formatters.py`: Rich-safe output helpers and styling utilities.

## Key features

- Click + Rich + Tabulate abstractions with zero direct imports outside the designated files.
- Direct access API (`cli.formatters`, `cli.file_tools`, `cli.prompts`) so projects avoid low-level dependencies.
- Authentication helpers, configuration validation, and reusable command registration.
- Comprehensive examples (`examples/01_getting_started.py`, etc.) plus migration guidance from v0.9.x (`docs/refactoring/MIGRATION_GUIDE_V0.9_TO_V0.10.md`).
- Railway-oriented error handling (`FlextResult[T]`) in every module.

## Quality & compliance

- **Ruff**: all linting violations addressed (QA table allows 5 test-specific exceptions).
- **Pyrefly / MyPy**: strict mode with zero reported errors.
- **Bandit**: no high/medium findings in `reports/lint-output/`.
- **Zero tolerance rules**: no `Any`, no `cast()`, no `TYPE_CHECKING`, no metaclasses, no root aliases; honored by architecture guidelines in `flext-cli/CLAUDE.md`.
- **Testing**: 1 016 tests, organized by feature, all passing in `reports/pytest/`.

## Resources & references

- [Project README](../../flext-cli/README.md)
- [CLAUDE governance](../../flext-cli/CLAUDE.md) for architecture layering & zero-tolerance rules
- `docs/getting-started.md`, `docs/api-reference.md`, `docs/architecture.md` inside `flext-cli/docs/`
- `examples/` folder for ready-made use cases
- `reports/coverage-scan-*`, `reports/lint-output/*`, `reports/pytest/*` for the QA evidence mentioned above

## Support & contributions

- GitHub issues: <https://github.com/flext-sh/flext-cli/issues>
- Discussions: <https://github.com/flext-sh/flext-cli/discussions>
- Follow `docs/standards/README.md` and the workspace `CLAUDE.md` before proposing doc or code changes so this brief stays aligned with the global portal.
