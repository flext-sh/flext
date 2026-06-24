#!/usr/bin/env python3
# /// flext-command
# verb = "boot"
# what = "stat"
# domain = "workspace"
# summary = "Show git status for workspace projects"
# description = "Runs the legacy _stat target to show status across submodules, external projects and root."
# example = "make boot WHAT=stat"
# mutates = false
# aliases = []
# params = []
# rules = ["workspace-bootstrap"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_stat")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
