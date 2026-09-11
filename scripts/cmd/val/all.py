"""Run validation gates for project, workspace, or both scopes."""
# /// flext-command
# verb = "val"
# what = "all"
# domain = "governance"
# summary = "Run validation gates using current VALIDATE_SCOPE"
# description = "Runs workspace and/or project validation depending on VALIDATE_SCOPE."
# example = "make val WHAT=all"
# mutates = false
# aliases = ["validate"]
# params = [
#   { name = "VALIDATE_SCOPE", help = "project|workspace|all", required = false, default = "all", choices = ["project", "workspace", "all"] },
#   { name = "WHAT", help = "Comando de validacao", required = false, default = "all", choices = ["all","project","workspace"] }
# ]
# rules = ["governance"]
# ///

from __future__ import annotations

from typing import Annotated, Literal

from flext_tests import m, u
from scripts.dispatch import Dispatch


class FlextRootValAllCommand:
    """Run validation gates for the selected scope."""

    class Options(m.Value):
        """Validated validation command options."""

        model_config = m.ConfigDict(
            extra="forbid", frozen=True, validate_assignment=True
        )

        scope: Annotated[
            Literal["project", "workspace", "all"],
            u.Field(description="Validation scope to execute."),
        ] = "all"

        @u.field_validator("scope", mode="before")
        @classmethod
        def normalize_scope(cls, value: str | None) -> str:
            """Normalize the environment value before Literal validation."""
            return (value or "all").strip().lower()

        @property
        def targets(self) -> tuple[str, ...]:
            """The private Make targets for the validated scope."""
            if self.scope == "workspace":
                return ("_val_workspace",)
            if self.scope == "project":
                return ("_val_project",)
            return ("_val_workspace", "_val_project")

    @staticmethod
    def run() -> int:
        """Dispatch validation by VALIDATE_SCOPE."""
        try:
            options = FlextRootValAllCommand.options()
        except ValueError:
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
                "scope": Dispatch.env_value("VALIDATE_SCOPE", "all").lower()
            })
        )
        return options


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, FlextRootValAllCommand.run)
