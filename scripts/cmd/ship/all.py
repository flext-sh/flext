#!/usr/bin/env python3
# /// flext-command
# verb = "ship"
# what = "all"
# domain = "release"
# summary = "Interactive workspace release orchestration"
# description = "Runs the legacy _rel target (release workflow)."
# example = "make ship WHAT=all APPLY=Y"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["release"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_rel")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
