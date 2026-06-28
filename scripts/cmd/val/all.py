#!/usr/bin/env python3
"""Run validation gates for project, workspace, or both scopes."""
# /// flext-command
# verb = "val"
# what = "all"
# domain = "governance"
# summary = "Run validation gates using current VALIDATE_SCOPE"
# description = "Runs workspace and/or project validation depending on VALIDATE_SCOPE."
# example = "make val WHAT=all"
# mutates = false
# aliases = []
# params = [
#   { name = "VALIDATE_SCOPE", help = "project|workspace|all", required = false, default = "project", choices = ["project", "workspace", "all"] },
#   { name = "WHAT", help = "Comando de validacao", required = false, default = "all", choices = ["all","project","workspace"] }
# ]
# rules = ["governance"]
# ///

from __future__ import annotations

from scripts.dispatch import Dispatch


class ValAllCommand:
    """Run validation gates for the selected scope."""

    @staticmethod
    def run() -> int:
        """Dispatch validation by VALIDATE_SCOPE."""
        scope = Dispatch.env_value("VALIDATE_SCOPE", "project").lower()
        if scope == "workspace":
            return Dispatch.run_make("_val_workspace")
        if scope == "project":
            return Dispatch.run_make("_val_project")
        if scope == "all":
            code = Dispatch.run_make("_val_workspace")
            if code != 0:
                return code
            return Dispatch.run_make("_val_project")
        print(f"ERRO: VALIDATE_SCOPE invalido: {scope}")
        return 2


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, ValAllCommand.run)
