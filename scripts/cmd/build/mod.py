"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "build"
# what = "mod"
# domain = "build"
# summary = "Modernize pyproject.toml files"
# description = "Runs the canonical _mod target to standardize configs without lock/install."
# example = "make build WHAT=mod"
# target = "_mod"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["build"]
# ///
