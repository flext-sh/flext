"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "ship"
# what = "pr"
# domain = "release"
# summary = "Manage pull requests for selected projects"
# description = "Runs the canonical _pr target."
# example = "make ship WHAT=pr APPLY=Y"
# target = "_pr"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "PR_ACTION", help = "Pull-request action", required = false, default = "status", choices = ["status", "create", "view", "checks", "merge", "close"] },
#   { name = "PR_BASE", help = "Pull-request base branch", required = false, default = "main" },
#   { name = "PR_BRANCH", help = "Workspace branch used by PR orchestration", required = false, default = "" },
#   { name = "PR_HEAD", help = "Pull-request head branch", required = false, default = "" },
#   { name = "PR_NUMBER", help = "Pull-request number", required = false, default = "" },
#   { name = "PR_TITLE", help = "Pull-request title", required = false, default = "" },
#   { name = "PR_BODY", help = "Pull-request body", required = false, default = "" },
#   { name = "PR_DRAFT", help = "Create draft pull request", required = false, default = "0", choices = ["0", "1"] },
#   { name = "PR_MERGE_METHOD", help = "Merge method", required = false, default = "squash", choices = ["squash", "merge", "rebase"] },
#   { name = "PR_AUTO", help = "Enable auto-merge", required = false, default = "0", choices = ["0", "1"] },
#   { name = "PR_DELETE_BRANCH", help = "Delete branch after merge", required = false, default = "0", choices = ["0", "1"] },
#   { name = "PR_CHECKS_STRICT", help = "Require strict PR checks", required = false, default = "0", choices = ["0", "1"] },
#   { name = "PR_RELEASE_ON_MERGE", help = "Run release on merge", required = false, default = "1", choices = ["0", "1"] },
#   { name = "PR_INCLUDE_ROOT", help = "Include root workspace repository", required = false, default = "1", choices = ["0", "1"] },
#   { name = "PR_CHECKPOINT", help = "Create PR checkpoint", required = false, default = "1", choices = ["0", "1"] }
# ]
# rules = ["release"]
# ///
