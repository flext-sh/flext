#!/usr/bin/env python3
# /// flext-command
# verb = "build"
# what = "constraints"
# domain = "build"
# summary = "Rewrite dependency constraints"
# description = "Runs the legacy _constraints target to rewrite constraints from uv.lock."
# example = "make build WHAT=constraints"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["build"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_constraints")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
