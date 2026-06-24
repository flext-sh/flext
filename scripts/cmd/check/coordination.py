#!/usr/bin/env python3
# /// flext-command
# verb = "check"
# what = "coordination"
# domain = "quality"
# summary = "Run coordination governance checks"
# description = "Executes Makefile _coordination target from legacy command path."
# example = "make check WHAT=coordination"
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
