#!/usr/bin/env python3
# /// flext-command
# verb = "boot"
# what = "all"
# domain = "workspace"
# summary = "Bootstrap workspace .venv + submodules"
# description = "Installs all projects into workspace .venv and initializes submodules."
# example = "make boot WHAT=all"
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
    return run_make("_boot_default")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
