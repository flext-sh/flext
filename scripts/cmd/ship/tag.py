"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "ship"
# what = "tag"
# domain = "release"
# summary = "Create git tags for selected projects"
# description = "Runs the canonical _tag target."
# example = "make ship WHAT=tag APPLY=Y TAG=v0.20.0"
# target = "_tag"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "TAG", help = "Optional tag name (defaults to version from pyproject.toml)", required = false, default = "" },
#   { name = "DRY_RUN", help = "Show what would be tagged", required = false, default = "0", choices = ["0", "1"] }
# ]
# rules = ["release"]
# ///
