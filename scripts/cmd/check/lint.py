#!/usr/bin/env python3
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

import os

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    gates = os.environ.get("CHECK_GATES", "lint,pyrefly")
    return run_make("_check_default", extra_env={"CHECK_GATES": gates})


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
