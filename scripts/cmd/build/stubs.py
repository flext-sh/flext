#!/usr/bin/env python3
# /// flext-command
# verb = "build"
# what = "stubs"
# domain = "build"
# summary = "Run repo-wide stub supply-chain validation"
# description = "Runs the legacy _stubs target."
# example = "make build WHAT=stubs"
# mutates = false
# aliases = []
# params = []
# rules = ["build", "type-check"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_stubs")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
