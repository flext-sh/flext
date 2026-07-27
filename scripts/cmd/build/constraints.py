"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "build"
# what = "constraints"
# domain = "build"
# summary = "Rewrite dependency constraints"
# description = "Runs the canonical _constraints target to rewrite constraints from uv.lock."
# example = "make build WHAT=constraints"
# target = "_constraints"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["build"]
# ///
