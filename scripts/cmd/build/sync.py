"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "build"
# what = "sync"
# domain = "build"
# summary = "Sync project Makefiles from pyproject.toml"
# description = "Runs the canonical _sync target to refresh Makefiles and __init__.py lazy imports."
# example = "make build WHAT=sync"
# target = "_sync"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["build"]
# ///
