#!/usr/bin/env python3
# /// flext-command
# verb = "ship"
# what = "push"
# domain = "release"
# summary = "Push branches and tags for selected projects"
# description = "Runs the legacy _push target."
# example = "make ship WHAT=push APPLY=Y"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "DRY_RUN", help = "Show what would be pushed", required = false, default = "0", choices = ["0", "1"] }
# ]
# rules = ["release"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_push")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
