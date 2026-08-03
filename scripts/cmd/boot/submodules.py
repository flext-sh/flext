"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "boot"
# what = "submodules"
# domain = "workspace"
# summary = "Bootstrap workspace submodules"
# description = "Runs the canonical bootstrap target for submodule initialization."
# example = "make setup WHAT=submodules"
# target = "_boot_submodules"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["workspace-bootstrap"]
# ///
