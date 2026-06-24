#!/usr/bin/env python3
# /// flext-command
# verb = "build"
# what = "gen"
# domain = "build"
# summary = "Regenerate standardized project files"
# description = "Runs the legacy _gen target (mod + sync)."
# example = "make build WHAT=gen"
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
    return run_make("_gen")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
