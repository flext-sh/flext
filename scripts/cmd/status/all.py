#!/usr/bin/env python3
"""Show Beads runtime status through read-only status commands."""
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

from scripts.dispatch import Dispatch


class StatusAllCommand:
    """Run read-only Beads status checks."""

    @staticmethod
    def run() -> int:
        """Run the read-only Beads status command set."""
        commands = (
            ("bd", "status", "--json"),
            ("bd", "dolt", "show"),
            ("bd", "backup", "status", "--json"),
        )
        code = 0
        for command in commands:
            result = Dispatch.run_shell(command)
            if result != 0 and code == 0:
                code = result
        return code


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, StatusAllCommand.run)
