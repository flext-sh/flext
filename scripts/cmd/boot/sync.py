#!/usr/bin/env python3
# /// flext-command
# verb = "boot"
# what = "sync"
# domain = "workspace"
# summary = "Sync project Makefiles and lazy imports"
# description = "Runs the legacy _sync target to refresh project Makefiles and __init__.py lazy imports."
# example = "make boot WHAT=sync"
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
    return run_make("_sync")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
