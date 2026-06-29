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

import sys
from typing import Annotated, Literal

from scripts.dispatch import Dispatch

from flext_tests import m, u


_VALIDATE_SCOPES: tuple[str, ...] = ("project", "workspace", "all")


class FlextRootValAllCommand:
    """Run validation gates for the selected scope."""

    class Options(m.Value):
        """Validated validation command options."""

        model_config = m.ConfigDict(
            extra="forbid",
            frozen=True,
            validate_assignment=True,
        )

        scope: Annotated[
            Literal["project", "workspace", "all"],
            u.Field(description="Validation scope to execute."),
        ] = "project"

        @u.field_validator("scope", mode="before")
        @classmethod
        def normalize_scope(cls, value: str | None) -> str:
            """Normalize the environment value before Literal validation."""
            return (value or "project").strip().lower()

        @property
        def targets(self) -> tuple[str, ...]:
            """Return the private Make targets for the validated scope."""
            mapping: dict[str, tuple[str, ...]] = {
                "workspace": ("_val_workspace",),
                "project": ("_val_project",),
                "all": ("_val_workspace", "_val_project"),
            }
            return mapping.get(self.scope, mapping["project"])

    @staticmethod
    def run() -> int:
        """Dispatch validation by VALIDATE_SCOPE."""
        try:
            options = FlextRootValAllCommand.options()
        except ValueError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 2

        for target in options.targets:
            code = Dispatch.run_make(target)
            if code != 0:
                return code
        return 0

    @staticmethod
    def options() -> Options:
        """Validate environment-backed validation command options."""
        options: FlextRootValAllCommand.Options = (
            FlextRootValAllCommand.Options.model_validate({
                "scope": Dispatch.env_value("VALIDATE_SCOPE", "project").lower(),
            })
        )
        return options


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, FlextRootValAllCommand.run)
