#!/usr/bin/env python3
"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "ship"
# what = "rel"
# domain = "release"
# summary = "Interactive workspace release orchestration"
# description = "Runs the legacy _rel target."
# example = "make ship WHAT=rel APPLY=Y"
# target = "_rel"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to mutate workspace/release", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["release"]
# ///
