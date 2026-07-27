"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "build"
# what = "gen"
# domain = "build"
# summary = "Regenerate standardized project files"
# description = "Runs the canonical _gen target (mod + sync)."
# example = "make build WHAT=gen"
# target = "_gen"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["build"]
# ///
