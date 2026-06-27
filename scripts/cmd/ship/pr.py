#!/usr/bin/env python3
"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "ship"
# what = "pr"
# domain = "release"
# summary = "Manage pull requests for selected projects"
# description = "Runs the legacy _pr target."
# example = "make ship WHAT=pr APPLY=Y"
# target = "_pr"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["release"]
# ///
