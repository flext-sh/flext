#!/usr/bin/env python3
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

from scripts.dispatch import promoted_main, discover, render_global_help


def main() -> int:
    print(render_global_help(discover()))
    return 0


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
