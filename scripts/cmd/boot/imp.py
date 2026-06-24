#!/usr/bin/env python3
# /// flext-command
# verb = "boot"
# what = "imp"
# domain = "workspace"
# summary = "Detect/fix import violations"
# description = "Runs the legacy _imp target to detect and optionally fix import violations."
# example = "make boot WHAT=imp APPLY=Y"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to apply fixes", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["workspace-bootstrap"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_imp")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
