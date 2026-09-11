"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "ship"
# what = "push"
# domain = "release"
# summary = "Push branches and tags for selected projects"
# description = "Runs the canonical _push target."
# example = "make ship WHAT=push APPLY=Y"
# target = "_push"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "DRY_RUN", help = "Show what would be pushed", required = false, default = "0", choices = ["0", "1"] }
# ]
# rules = ["release"]
# ///
