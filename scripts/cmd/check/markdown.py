"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "check"
# what = "markdown"
# domain = "quality"
# summary = "Run Markdown quality gate"
# description = "Runs the canonical check orchestrator with CHECK_GATES=markdown."
# example = "make check WHAT=markdown"
# target = "_check_default"
# target_env = { CHECK_GATES = "markdown" }
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate"]
# ///
