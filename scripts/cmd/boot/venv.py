"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "boot"
# what = "venv"
# domain = "workspace"
# summary = "Bootstrap workspace virtualenv"
# description = "Runs the canonical bootstrap target for workspace environment setup."
# example = "make boot WHAT=venv"
# target = "_boot_venv"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["workspace-bootstrap"]
# ///
