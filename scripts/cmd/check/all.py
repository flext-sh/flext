#!/usr/bin/env python3
# /// flext-command
# verb = "check"
# what = "all"
# domain = "quality"
# summary = "Run quick default checks"
# description = "Runs fmt and lint gates using the lightweight default profile."
# example = "make check WHAT=all"
# mutates = false
# aliases = []
# params = [
#   { name = "CHECK_GATES", help = "Optional override for lint gate set", required = false, default = "lint,pyrefly" },
#   { name = "WHAT", help = "Comando de check", required = false, default = "all", choices = ["all","fmt","types","lint","pyrefly","loc-cap","boundary","coordination"] }
# ]
# rules = ["dev-gate"]
# ///

from __future__ import annotations

import os

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    code = run_make("_fmt")
    if code != 0:
        return code
    gate_env = {"CHECK_GATES": "lint,pyrefly"}
    if value := os.environ.get("CHECK_GATES"):
        gate_env["CHECK_GATES"] = value
    return run_make("_check_default", extra_env=gate_env)


if __name__ == "__main__":
    # guard via dispatch contract
    raise SystemExit(promoted_main(__file__, main))
