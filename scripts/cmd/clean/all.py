"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "clean"
# what = "all"
# domain = "workspace"
# summary = "Clean build/test/type artifacts"
# description = "Runs the canonical _clean_default target to remove caches and orchestrated clean artifacts."
# example = "make clean WHAT=all"
# target = "_clean_default"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["workspace-bootstrap"]
# ///
