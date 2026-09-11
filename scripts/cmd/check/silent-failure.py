"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "check"
# what = "silent-failure"
# domain = "quality"
# summary = "Run silent-failure quality gate"
# description = "Runs the canonical check orchestrator with CHECK_GATES=silent-failure."
# example = "make check WHAT=silent-failure"
# target = "_check_default"
# target_env = { CHECK_GATES = "silent-failure" }
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate"]
# ///
