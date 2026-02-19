<!-- TOC START -->
- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
- [Scripts](#scripts)
<!-- TOC END -->

---
name: scripts-testing
description: Testing scripts — pytest runners, test analysis, quality gates, stress tests, and distributed testing. Use when editing scripts/testing/.
---

# Scripts Testing

## Scope

- `scripts/testing/quick_pytest_analysis.py`
- `scripts/testing/run-all-tests.sh`
- `scripts/testing/run_comprehensive_pytest_analysis.py`
- `scripts/testing/run_pytest_all_projects.py`
- `scripts/testing/run_tests.py`
- `scripts/testing/stress-test.sh`
- `scripts/testing/test-distributed.sh`
- `scripts/testing/test-end-to-end-pipeline.sh`
- `scripts/testing/testing_metrics_dashboard.sh`
- `scripts/testing/testing_quality_gates.sh`
- `scripts/run_all_examples.py`

## References

- `.claude/skills/flext-quality-gates/SKILL.md`
- `.claude/skills/rules-scripts/SKILL.md`
- `base.mk`

## Rules

- Test runners must support `--help` and be runnable from repo root.
- Test output must go to stdout; structured reports to `.sisyphus/reports/` via artifact naming.
- Stress tests and distributed tests must be explicitly opt-in (not part of quick validation).

## Instructions

- When adding test runners, follow the pattern in `run_pytest_all_projects.py`.
- When modifying quality gates, ensure they align with `base.mk` targets. Coverage thresholds live in `pyproject.toml` `[tool.coverage.report] fail_under`, not in Makefiles/workflows/docker/CLI flags.
- Keep test scripts independent of each other.

## Workflow

1. Identify the testing scope (unit, integration, stress, e2e).
2. Create or modify the script under `scripts/testing/`.
3. Test locally with `--help` first.
4. Verify script syntax: `bash -n` for shell scripts, `python -m compileall` for Python.
5. Run tests via Make: `make test PROJECT=<name>` or `make test PROJECT=<name> PYTEST_ARGS="-k unit"`.

## Examples

Good (primary — use Make verbs):

```bash
make test
make test PROJECT=flext-core
make test PROJECT=flext-core PYTEST_ARGS="-k unit"
make test FAIL_FAST=1
```

Why good: Canonical Make contract, consistent with CLAUDE.md.

Good (internal — scripts behind Make):

```bash
python scripts/testing/run_pytest_all_projects.py --quick
bash scripts/testing/run-all-tests.sh
```

Why acceptable: Direct script invocation for debugging/development, but Make verbs are the recommended workflow.

Bad:

```bash
cd flext-core && pytest  # not from root
```

Why bad: Requires manual directory change, not reproducible.

## Verification

Make gates (primary):

- `make test PROJECT=flext-core` — run tests for a single project
- `make test PROJECT=flext-core PYTEST_ARGS="-k unit"` — filtered test run
- `make test FAIL_FAST=1` — run all projects, stop on first failure
- `make check PROJECT=flext-core CHECK_GATES=lint` — quick lint check

Script-level checks (internal):

- `python -m compileall scripts/testing`
- `bash -n scripts/testing/run-all-tests.sh`
- `bash -n scripts/testing/stress-test.sh`
- `rg "Owner-Skill:.*scripts-testing" scripts/testing`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/testing/quick_pytest_analysis.py` | Quick pytest analysis | `python scripts/testing/quick_pytest_analysis.py` |
| `scripts/testing/run-all-tests.sh` | Run all tests across projects | `bash scripts/testing/run-all-tests.sh` |
| `scripts/testing/run_comprehensive_pytest_analysis.py` | Comprehensive pytest analysis | `python scripts/testing/run_comprehensive_pytest_analysis.py` |
| `scripts/testing/run_pytest_all_projects.py` | Run pytest for all projects | `python scripts/testing/run_pytest_all_projects.py` |
| `scripts/testing/run_tests.py` | General test runner | `python scripts/testing/run_tests.py` |
| `scripts/testing/stress-test.sh` | Stress testing | `bash scripts/testing/stress-test.sh` |
| `scripts/testing/test-distributed.sh` | Distributed testing | `bash scripts/testing/test-distributed.sh` |
| `scripts/testing/test-end-to-end-pipeline.sh` | End-to-end pipeline testing | `bash scripts/testing/test-end-to-end-pipeline.sh` |
| `scripts/testing/testing_metrics_dashboard.sh` | Testing metrics dashboard | `bash scripts/testing/testing_metrics_dashboard.sh` |
| `scripts/testing/testing_quality_gates.sh` | Testing quality gates | `bash scripts/testing/testing_quality_gates.sh` |
| `scripts/run_all_examples.py` | Run all example scripts | `python scripts/run_all_examples.py` |
