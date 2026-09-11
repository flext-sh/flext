"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "check"
# what = "pyright"
# domain = "quality"
# summary = "Run pyright quality gate"
# description = "Runs the canonical check orchestrator with CHECK_GATES=pyright."
# example = "make check WHAT=pyright"
# target = "_check_default"
# target_env = { CHECK_GATES = "pyright" }
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate", "type-check"]
# ///
