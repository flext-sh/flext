# Reports & Validation Artifacts

The `reports/` directory at the repository root stores every automated validation
artifact referenced from the documentation portal. Use this page as a quick map to
what lives there so you can trace statements in `docs/README.md` back to actual
scan outputs.

## Key Subdirectories

- `lint-output/` – Ruff and Bandit logs that prove the quality gates the
  documentation mentions. Each subfolder is tagged by timestamp and test run ID.
- `pytest/` and `stress-tests/` – Test runs from `make test` and the stress
  suite; the raw JUnit files and coverage summaries live underneath.
- `coverage-scan-20260202_144808` plus `coverage.xml` – Coverage snapshots that
  explain the coverage claims mentioned in the portal.
- `workflow_summary_20251230_125723.md` – Human-readable recap of the CI pipeline;
  it documents the steps that the docs portal wants readers to trust.
- `flext-cli/`, `flext-ldap/` – Project-specific scan outputs that mirror how each
  library is validated before release.
- `constants_*` – Metadata reports describing validation thresholds, guard rails,
  and quality rules used for releases. Keep these in sync when you update
  standards.

## Keeping Reports Fresh

1. Run `make val` or the narrower `make check` targets before updating
   documentation references that claim a certain scan exists.
2. After the run, copy the resulting artifact into `reports/` so the portal can
   still point to a real file.
3. Link to the relevant artifact from anywhere in `docs/` when you declare a
   quality gate, so readers always have the concrete evidence they need.

Refer to this README before you link into `reports/` so the portal never points to
a phantom log or an AI-control artifact outside the git tree.
