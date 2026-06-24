#!/usr/bin/env python3
# /// flext-command
# verb = "clean"
# what = "all"
# domain = "workspace"
# summary = "Clean build/test/type artifacts"
# description = "Runs the legacy _clean_default target to remove caches and orchestrated clean artifacts."
# example = "make clean WHAT=all"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["workspace-bootstrap"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_clean_default")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
