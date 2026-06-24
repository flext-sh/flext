#!/usr/bin/env python3
# /// flext-command
# verb = "ship"
# what = "tag"
# domain = "release"
# summary = "Create git tags for selected projects"
# description = "Runs the legacy _tag target."
# example = "make ship WHAT=tag APPLY=Y TAG=v0.12.0"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "TAG", help = "Optional tag name (defaults to version from pyproject.toml)", required = false, default = "" },
#   { name = "DRY_RUN", help = "Show what would be tagged", required = false, default = "0", choices = ["0", "1"] }
# ]
# rules = ["release"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_tag")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
