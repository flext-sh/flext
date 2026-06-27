#!/usr/bin/env python3
"""Render the promoted command surface from the scripts registry."""
# /// flext-command
# verb = "makefile"
# what = "all"
# domain = "meta"
# summary = "Show command surface from scripts/cmd"
# description = "Displays all promoted verbs and WHAT options."
# example = "make makefile WHAT=all"
# mutates = false
# aliases = []
# params = []
# rules = ["meta"]
# ///

from __future__ import annotations

from scripts.dispatch import discover, promoted_main, render_global_help


def main() -> int:
    """Print global dispatcher help from discovered command metadata."""
    print(render_global_help(discover()))
    return 0


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
