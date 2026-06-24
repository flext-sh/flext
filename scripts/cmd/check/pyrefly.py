#!/usr/bin/env python3
# /// flext-command
# verb = "check"
# what = "pyrefly"
# domain = "quality"
# summary = "Run pyrefly repository or scoped type check"
# description = "Runs the legacy _pyre target configured in the Makefile."
# example = "make check WHAT=pyrefly"
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate", "type-check"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_pyre")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
