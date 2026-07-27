"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "build"
# what = "all"
# domain = "build"
# summary = "Build/package all selected projects"
# description = "Runs the canonical _build_default target via orchestrator."
# example = "make build WHAT=all"
# target = "_build_default"
# mutates = true
# aliases = ["gen"]
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["build"]
# ///
