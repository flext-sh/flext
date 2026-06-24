#!/usr/bin/env python3
# /// flext-command
# verb = "coordination"
# what = "all"
# domain = "governance"
# summary = "Run Beads coordination diagnostics"
# description = "Runs governance and bead-coordination reporting commands."
# example = "make coordination WHAT=all"
# mutates = false
# aliases = []
# params = []
# rules = ["governance"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_coordination")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
