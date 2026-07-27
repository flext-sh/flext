"""Run typing supply-chain checks and optional pyrefly gate."""
# /// flext-command
# verb = "check"
# what = "types"
# domain = "quality"
# summary = "Run typing supply chain"
# description = "Runs stubs/typing validation, optional dependency report and optional pyrefly."
# example = "make check WHAT=types"
# mutates = false
# aliases = []
# params = [
#   { name = "CHECK_GATES", help = "Optional additional gates (e.g. pyrefly)", required = false, default = "" },
#   { name = "DEPS_REPORT", help = "Run global dependency report when set to 1", required = false, default = "0", choices = ["0","1"] }
# ]
# rules = ["dev-gate", "type-check"]
# ///

from __future__ import annotations

from scripts.dispatch import Dispatch


class CheckTypesCommand:
    """Run typing supply-chain checks."""

    @staticmethod
    def run() -> int:
        """Run `_types`, then optional pyrefly when requested."""
        code = Dispatch.run_make("_types")
        if code != 0:
            return code
        gates = tuple(
            item.strip()
            for item in Dispatch.env_value("CHECK_GATES").split(",")
            if item.strip()
        )
        if "pyrefly" in gates:
            return Dispatch.run_make(
                "_check_default", extra_env={"CHECK_GATES": "pyrefly"}
            )
        return 0


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, CheckTypesCommand.run)
