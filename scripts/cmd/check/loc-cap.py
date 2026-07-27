"""Run the LOC cap quality gate through the workspace orchestrator."""
# /// flext-command
# verb = "check"
# what = "loc-cap"
# domain = "quality"
# summary = "Run loc-cap gate"
# description = "Execute orchestrator check with loc-cap gate."
# example = "make check WHAT=loc-cap"
# mutates = false
# aliases = []
# params = [
#   { name = "CHECK_GATES", help = "Override gate list for loc-cap execution", required = false, default = "loc-cap" }
# ]
# rules = ["dev-gate"]
# ///

from __future__ import annotations

from scripts.dispatch import Dispatch


class CheckLocCapCommand:
    """Run the LOC cap quality gate."""

    @staticmethod
    def run() -> int:
        """Run `_check_default` with the LOC cap gate selected."""
        gates = Dispatch.env_value("CHECK_GATES", "loc-cap")
        return Dispatch.run_make("_check_default", extra_env={"CHECK_GATES": gates})


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, CheckLocCapCommand.run)
