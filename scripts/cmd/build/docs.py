#!/usr/bin/env python3
# /// flext-command
# verb = "build"
# what = "docs"
# domain = "build"
# summary = "Run docs pipeline"
# description = "Runs the legacy _docs target (DOCS_PHASE=audit|fix|build|generate|validate|all)."
# example = "make build WHAT=docs DOCS_PHASE=validate"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "DOCS_PHASE", help = "Docs phase to run", required = false, default = "all", choices = ["audit", "fix", "build", "generate", "validate", "all"] }
# ]
# rules = ["build"]
# ///

from __future__ import annotations

from scripts.dispatch import promoted_main, run_make


def main() -> int:
    return run_make("_docs")


if __name__ == "__main__":
    raise SystemExit(promoted_main(__file__, main))
