#!/usr/bin/env python3
# /// flext-command
# verb = "val"
# what = "project"
# domain = "governance"
# summary = "Run project validation"
# description = "Runs the existing _val_project target."
# example = "make val WHAT=project"
# mutates = false
# aliases = []
# params = []
# rules = ["governance"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_val_project")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
