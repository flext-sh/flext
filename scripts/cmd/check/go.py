"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "check"
# what = "go"
# domain = "quality"
# summary = "Run Go quality gate"
# description = "Runs the canonical check orchestrator with CHECK_GATES=go."
# example = "make check WHAT=go"
# target = "_check_default"
# target_env = { CHECK_GATES = "go" }
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate"]
# ///
