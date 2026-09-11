"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "ship"
# what = "rel"
# domain = "release"
# summary = "Interactive workspace release orchestration"
# description = "Runs the canonical _rel target."
# example = "make ship WHAT=rel APPLY=Y"
# target = "_rel"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "RELEASE_PHASE", help = "Release phase selector", required = false, default = "all", choices = ["all", "validate", "version", "build", "publish"] },
#   { name = "INTERACTIVE", help = "Run release workflow interactively", required = false, default = "1", choices = ["0", "1"] },
#   { name = "CREATE_BRANCHES", help = "Create release branches", required = false, default = "1", choices = ["0", "1"] },
#   { name = "RELEASE_NEXT_BUMP", help = "Next development version bump", required = false, default = "minor", choices = ["major", "minor", "patch"] },
#   { name = "RELEASE_DEV_SUFFIX", help = "Add development suffix", required = false, default = "0", choices = ["0", "1"] },
#   { name = "RELEASE_NEXT_DEV", help = "Prepare next development version", required = false, default = "0", choices = ["0", "1"] },
#   { name = "DRY_RUN", help = "Show release actions without applying", required = false, default = "0", choices = ["0", "1"] },
#   { name = "PUSH", help = "Push release branches/tags", required = false, default = "0", choices = ["0", "1"] },
#   { name = "VERSION", help = "Explicit release version", required = false, default = "" },
#   { name = "TAG", help = "Explicit release tag", required = false, default = "" },
#   { name = "BUMP", help = "Version bump kind", required = false, default = "", choices = ["major", "minor", "patch"] }
# ]
# rules = ["release"]
# ///
