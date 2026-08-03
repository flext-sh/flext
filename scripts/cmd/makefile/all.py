"""Render the promoted command surface from the scripts registry."""
# /// flext-command
# verb = "makefile"
# what = "all"
# domain = "meta"
# summary = "Show command surface from scripts/cmd"
# description = "Displays all promoted verbs and WHAT options."
# example = "make makefile"
# mutates = false
# aliases = []
# params = []
# rules = ["meta"]
# ///

from __future__ import annotations

from scripts.dispatch import Dispatch


class MakefileAllCommand:
    """Render the promoted Make command registry."""

    @staticmethod
    def run() -> int:
        """Print global dispatcher help from discovered command metadata."""
        return 0


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, MakefileAllCommand.run)
