#!/usr/bin/env python3
# /// flext-command
# verb = "ship"
# what = "pr"
# domain = "release"
# summary = "Manage pull requests for selected projects"
# description = "Runs the legacy _pr target."
# example = "make ship WHAT=pr APPLY=Y"
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
    return run_make("_pr")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
