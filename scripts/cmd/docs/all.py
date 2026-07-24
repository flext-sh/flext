#!/usr/bin/env python3
"""Run the workspace documentation pipeline through the registry."""
# /// flext-command
# verb = "docs"
# what = "all"
# domain = "documentation"
# summary = "Run docs pipeline"
# description = "Runs the canonical _docs target for DOCS_PHASE=audit|fix|build|generate|validate|all."
# example = "make docs DOCS_PHASE=validate"
# mutates = false
# mutates_when = [
#   { name = "DOCS_PHASE", values = ["all", "fix", "generate"] }
# ]
# aliases = []
# params = [
#   { name = "DOCS_PHASE", help = "Docs phase to run", required = false, default = "all", choices = ["audit", "fix", "build", "generate", "validate", "all"] },
#   { name = "APPLY", help = "Must be Y for mutating docs phases", required = false, default = "N", choices = ["Y", "N"] },
#   { name = "FIX", help = "Set to 1 to run the docs fix phase through the canonical fixer", required = false, default = "0", choices = ["0", "1"] }
# ]
# rules = ["documentation"]
# ///

from __future__ import annotations

from types import MappingProxyType
from typing import Annotated, Literal

from flext_tests import m, t, u
from scripts.dispatch import Dispatch


class FlextRootDocsAllCommand:
    """Run documentation phases with mutation guard for generated output."""

    class Options(m.Value):
        """Validated docs command options."""

        model_config = m.ConfigDict(
            extra="forbid", frozen=True, validate_assignment=True
        )

        phase: Annotated[
            Literal["audit", "fix", "build", "generate", "validate", "all"],
            u.Field(description="Documentation pipeline phase."),
        ] = "all"
        apply: Annotated[
            Literal["Y", "N"], u.Field(description="Mutation opt-in for docs phases.")
        ] = "N"
        fix: Annotated[
            Literal["0", "1"], u.Field(description="Docs fix opt-in flag.")
        ] = "0"

        @u.field_validator("phase", mode="before")
        @classmethod
        def normalize_phase(cls, value: str | None) -> str:
            """Normalize the docs phase before Literal validation."""
            return (value or "all").strip().lower()

        @u.field_validator("apply", mode="before")
        @classmethod
        def normalize_apply(cls, value: str | None) -> str:
            """Normalize the mutation opt-in flag before Literal validation."""
            return (value or "N").strip().upper()

        @u.field_validator("fix", mode="before")
        @classmethod
        def normalize_fix(cls, value: str | None) -> str:
            """Normalize the docs fix flag before Literal validation."""
            return (value or "0").strip()

        @property
        def requires_apply(self) -> bool:
            """Return whether the selected docs phase can mutate generated files."""
            match self.phase:
                case "all" | "fix" | "generate":
                    return True
                case _:
                    return False

        @property
        def has_mutation_opt_in(self) -> bool:
            """Return whether the requested mutation was explicitly approved."""
            return self.apply == "Y" or (self.phase == "fix" and self.fix == "1")

        @property
        def can_execute(self) -> bool:
            """Return whether the validated docs command can execute immediately."""
            return not self.requires_apply or self.has_mutation_opt_in

        @property
        def target_env(self) -> t.MappingKV[str, str]:
            """Return explicit Make variables for the private docs target."""
            env: t.MappingKV[str, str] = MappingProxyType({
                "DOCS_PHASE": self.phase,
                "FIX": self.fix,
            })
            return env

        @property
        def dry_run_lines(self) -> tuple[str, ...]:
            """Return the canonical dry-run message for mutating docs phases."""
            return (
                "DRY-RUN: nenhuma mutacao executada.",
                f"Comando: make docs DOCS_PHASE={self.phase}",
                "Regra: fases mutadoras de docs exigem APPLY=Y ou DOCS_PHASE=fix FIX=1.",
                "",
                "Execucao canonica:",
                f"  make docs DOCS_PHASE={self.phase} APPLY=Y",
            )

    @staticmethod
    def run() -> int:
        """Run `_docs` after validating the selected phase mutation mode."""
        try:
            options = FlextRootDocsAllCommand.options()
        except ValueError:
            return 2

        if not options.can_execute:
            for line in options.dry_run_lines:
                u.Cli.emit_raw(f"{line}\n")
            return 0
        return Dispatch.run_make("_docs", extra_env=options.target_env)

    @staticmethod
    def options() -> Options:
        """Validate environment-backed docs command options."""
        options: FlextRootDocsAllCommand.Options = (
            FlextRootDocsAllCommand.Options.model_validate({
                "phase": Dispatch.env_value("DOCS_PHASE", "all").lower(),
                "apply": Dispatch.env_value("APPLY", "N").upper(),
                "fix": Dispatch.env_value("FIX", "0"),
            })
        )
        return options


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, FlextRootDocsAllCommand.run)
