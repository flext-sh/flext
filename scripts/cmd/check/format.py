"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "check"
# what = "format"
# domain = "quality"
# summary = "Run formatting gates"
# description = "Runs the canonical _fmt target."
# example = "make check WHAT=format APPLY=Y"
# target = "_fmt"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to apply formatting", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["dev-gate"]
# ///
