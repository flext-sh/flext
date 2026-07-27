"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "build"
# what = "up"
# domain = "build"
# summary = "Upgrade workspace dependencies"
# description = "Runs the canonical _up target to refresh lock, install and rewrite constraints."
# example = "make build WHAT=up"
# target = "_up"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["build"]
# ///
