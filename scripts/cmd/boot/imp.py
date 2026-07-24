"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "boot"
# what = "imp"
# domain = "workspace"
# summary = "Detect/fix import violations"
# description = "Runs the canonical _imp target to detect and optionally fix import violations."
# example = "make boot WHAT=imp APPLY=Y"
# target = "_imp"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to apply fixes", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["workspace-bootstrap"]
# ///
