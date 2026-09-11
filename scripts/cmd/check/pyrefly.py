"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "check"
# what = "pyrefly"
# domain = "quality"
# summary = "Run pyrefly scoped type check"
# description = "Runs the canonical check orchestrator with CHECK_GATES=pyrefly."
# example = "make check WHAT=pyrefly"
# target = "_check_default"
# target_env = { CHECK_GATES = "pyrefly" }
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate", "type-check"]
# ///
