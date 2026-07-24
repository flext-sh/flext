"""Run the default check pipeline through promoted Make targets."""
# /// flext-command
# verb = "check"
# what = "all"
# domain = "quality"
# summary = "Run quick default checks"
# description = "Runs lint and pyrefly gates using the lightweight default profile."
# example = "make check WHAT=all"
# mutates = false
# aliases = ["lint"]
# params = [
#   { name = "CHECK_GATES", help = "Optional override for lint gate set", required = false, default = "lint,pyrefly" },
#   { name = "WHAT", help = "Comando de check", required = false, default = "all", choices = ["all","boundary","coordination","cqrs","docker_standardization","fmt","format","go","lint","loc-cap","markdown","mypy","pol","pyre","pyrefly","pyright","scan","silent-failure","types"] }
# ]
# rules = ["dev-gate"]
# ///

from __future__ import annotations

from scripts.dispatch import Dispatch


class CheckAllCommand:
    """Run the selected quality gate set."""

    @staticmethod
    def run() -> int:
        """Run the selected lint gate set."""
        gate_env = {"CHECK_GATES": "lint,pyrefly"}
        if value := Dispatch.env_value("CHECK_GATES"):
            gate_env["CHECK_GATES"] = value
        return Dispatch.run_make("_check_default", extra_env=gate_env)


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, CheckAllCommand.run)
