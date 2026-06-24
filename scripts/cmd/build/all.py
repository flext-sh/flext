#!/usr/bin/env python3
# /// flext-command
# verb = "build"
# what = "all"
# domain = "build"
# summary = "Build/package all selected projects"
# description = "Runs the legacy _build_default target via orchestrator."
# example = "make build WHAT=all"
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
    return run_make("_build_default")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
