"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "check"
# what = "mypy"
# domain = "quality"
# summary = "Run mypy quality gate"
# description = "Runs the canonical check orchestrator with CHECK_GATES=mypy."
# example = "make check WHAT=mypy"
# target = "_check_default"
# target_env = { CHECK_GATES = "mypy" }
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate", "type-check"]
# ///
