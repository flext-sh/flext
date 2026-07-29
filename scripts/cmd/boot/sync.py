"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "boot"
# what = "sync"
# domain = "workspace"
# summary = "Sync project Makefiles and lazy imports"
# description = "Runs the canonical _sync target to refresh project Makefiles and __init__.py lazy imports."
# example = "make boot WHAT=sync"
# target = "_sync"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["workspace-bootstrap"]
# ///
