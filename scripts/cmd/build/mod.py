#!/usr/bin/env python3
# /// flext-command
# verb = "build"
# what = "mod"
# domain = "build"
# summary = "Modernize pyproject.toml files"
# description = "Runs the legacy _mod target to standardize configs without lock/install."
# example = "make build WHAT=mod"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["build"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_mod")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
