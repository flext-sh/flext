#!/usr/bin/env python3
"""Run lint/type quality gates through the workspace orchestrator."""
# /// flext-command
# verb = "check"
# what = "lint"
# domain = "quality"
# summary = "Run lint/type gates"
# description = "Runs check gates on selected projects using orchestrator."
# example = "make check WHAT=lint"
# mutates = false
# aliases = []
# params = [
#   { name = "CHECK_GATES", help = "Lista de gates de check para o orquestrador", required = false, default = "lint,pyrefly" }
# ]
# rules = ["dev-gate"]
# ///

from __future__ import annotations

from scripts.dispatch import env_value, promoted_main, run_make


def main() -> int:
    """Run `_check_default` with the requested lint gate set."""
    gates = env_value("CHECK_GATES", "lint,pyrefly")
    return run_make("_check_default", extra_env={"CHECK_GATES": gates})


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
