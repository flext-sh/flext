#!/usr/bin/env python3
# /// flext-command
# verb = "check"
# what = "types"
# domain = "quality"
# summary = "Run typing supply chain"
# description = "Runs stubs/typing validation, optional dependency report and optional pyrefly."
# example = "make check WHAT=types"
# mutates = false
# aliases = []
# params = [
#   { name = "CHECK_GATES", help = "Optional additional gates (e.g. pyrefly)", required = false, default = "" },
#   { name = "DEPS_REPORT", help = "Run global dependency report when set to 1", required = false, default = "0", choices = ["0","1"] }
# ]
# rules = ["dev-gate", "type-check"]
# ///

from __future__ import annotations

import os

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    code = run_make("_types")
    if code != 0:
        return code
    gates = [
        item.strip()
        for item in os.environ.get("CHECK_GATES", "").split(",")
        if item.strip()
    ]
    if "pyrefly" in gates:
        return run_make("_pyre")
    return 0


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
