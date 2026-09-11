"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "check"
# what = "scan"
# domain = "quality"
# summary = "Run security scan gates"
# description = "Runs the canonical _scan target."
# example = "make check WHAT=scan"
# target = "_scan"
# mutates = false
# aliases = []
# params = []
# rules = ["dev-gate", "security"]
# ///
