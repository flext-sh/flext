"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "boot"
# what = "stat"
# domain = "workspace"
# summary = "Show git status for workspace projects"
# description = "Runs the canonical _stat target to show status across declared workspace projects and root."
# example = "make setup WHAT=stat"
# target = "_stat"
# mutates = false
# aliases = []
# params = []
# rules = ["workspace-bootstrap"]
# ///
