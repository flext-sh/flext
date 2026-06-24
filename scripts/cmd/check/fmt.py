#!/usr/bin/env python3
# /// flext-command
# verb = "check"
# what = "fmt"
# domain = "quality"
# summary = "Run formatting gates"
# description = "Runs ruff, gofmt/goimports and markdownlint over current selection."
# example = "make check WHAT=fmt"
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_fmt")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
