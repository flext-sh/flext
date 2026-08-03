"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "test"
# what = "all"
# domain = "quality"
# summary = "Run tests in selected projects"
# description = "Runs the canonical _test_default target via orchestrator."
# example = "make test PROJECT=flext-infra MATCH=test_foo"
# target = "_test_default"
# mutates = false
# aliases = []
# params = [
#   { name = "PYTEST_ARGS", help = "Extra pytest arguments", required = false, default = "" },
#   { name = "FILE", help = "Single test file", required = false, default = "" },
#   { name = "FILES", help = "Multiple test files", required = false, default = "" },
#   { name = "MATCH", help = "pytest -k filter", required = false, default = "" }
# ]
# rules = ["dev-gate"]
# ///
