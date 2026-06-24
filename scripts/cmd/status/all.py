#!/usr/bin/env python3
# /// flext-command
# verb = "status"
# what = "all"
# domain = "governance"
# summary = "Show Beads status"
# description = "Shows bead runtime status and health checks."
# example = "make status WHAT=all"
# mutates = false
# aliases = []
# params = []
# rules = ["governance"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_shell


def main() -> int:
    commands = [
        ["bd", "status", "--json"],
        ["bd", "dolt", "show"],
        ["bd", "backup", "status", "--json"],
    ]
    code = 0
    for command in commands:
        result = run_shell(command)
        if result != 0 and code == 0:
            code = result
    return code


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
