"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "boot"
# what = "all"
# domain = "workspace"
# summary = "Bootstrap workspace .venv + submodules"
# description = "Installs all projects into workspace .venv and initializes submodules."
# example = "make boot"
# target = "_boot_default"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["workspace-bootstrap"]
# ///
