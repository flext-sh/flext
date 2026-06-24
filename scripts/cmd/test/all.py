#!/usr/bin/env python3
# /// flext-command
# verb = "test"
# what = "all"
# domain = "quality"
# summary = "Run tests in selected projects"
# description = "Runs the legacy _test_default target via orchestrator."
# example = "make test WHAT=all PROJECT=flext-infra MATCH=test_foo"
# mutates = false
# aliases = []
# params = [
#   { name = "PYTEST_ARGS", help = "Extra pytest arguments", required = false, default = "" },
#   { name = "FILE", help = "Single test file", required = false, default = "" },
#   { name = "FILES", help = "Multiple test files", required = false, default = "" },
#   { name = "MATCH", help = "pytest -k filter", required = false, default = "" }
# ]
# rules = ["dev-gate"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_test_default")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
