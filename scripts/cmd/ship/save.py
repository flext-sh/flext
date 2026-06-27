#!/usr/bin/env python3
"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "ship"
# what = "save"
# domain = "release"
# summary = "Commit all changes in selected projects"
# description = "Runs the legacy _save target. Requires MESSAGE=."
# example = "make ship WHAT=save APPLY=Y MESSAGE='chore: update'"
# target = "_save"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "MESSAGE", help = "Commit message", required = true, default = "" }
# ]
# rules = ["release"]
# ///
