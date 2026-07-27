"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "build"
# what = "docs"
# domain = "build"
# summary = "Run docs pipeline"
# description = "Runs the canonical _docs target (DOCS_PHASE=audit|fix|build|generate|validate|all)."
# example = "make build WHAT=docs DOCS_PHASE=validate"
# target = "_docs"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "DOCS_PHASE", help = "Docs phase to run", required = false, default = "all", choices = ["audit", "fix", "build", "generate", "validate", "all"] }
# ]
# rules = ["build"]
# ///
