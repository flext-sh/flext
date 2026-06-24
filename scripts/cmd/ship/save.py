#!/usr/bin/env python3
# /// flext-command
# verb = "ship"
# what = "save"
# domain = "release"
# summary = "Commit all changes in selected projects"
# description = "Runs the legacy _save target. Requires MESSAGE=."
# example = "make ship WHAT=save APPLY=Y MESSAGE='chore: update'"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "MESSAGE", help = "Commit message", required = true, default = "" }
# ]
# rules = ["release"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_save")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
