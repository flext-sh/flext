#!/usr/bin/env python3
"""Run the LOC cap quality gate through the workspace orchestrator."""
# /// flext-command
# verb = "check"
# what = "loc-cap"
# domain = "quality"
# summary = "Run loc-cap gate"
# description = "Execute orchestrator check with loc-cap gate."
# example = "make check WHAT=loc-cap"
# mutates = false
# aliases = []
# params = [
#   { name = "CHECK_GATES", help = "Override gate list for loc-cap execution", required = false, default = "loc-cap" }
# ]
# rules = ["dev-gate"]
# ///

from __future__ import annotations

from scripts.dispatch import env_value, promoted_main, run_make


def main() -> int:
    """Run `_check_default` with the LOC cap gate selected."""
    gates = env_value("CHECK_GATES", "loc-cap")
    return run_make("_check_default", extra_env={"CHECK_GATES": gates})


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
