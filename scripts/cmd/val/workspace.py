#!/usr/bin/env python3
# /// flext-command
# verb = "val"
# what = "workspace"
# domain = "governance"
# summary = "Run workspace validation"
# description = "Runs the existing _val_workspace target."
# example = "make val WHAT=workspace"
# mutates = false
# aliases = []
# params = []
# rules = ["governance"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_val_workspace")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
