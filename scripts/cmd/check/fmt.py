"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "check"
# what = "fmt"
# domain = "quality"
# summary = "Run formatting gates"
# description = "Runs ruff and markdownlint over current selection."
# example = "make check WHAT=fmt APPLY=Y"
# target = "_fmt"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to apply formatting", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["dev-gate"]
# ///
