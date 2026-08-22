#!/usr/bin/env python3
"""Header-only promoted command; dispatcher executes the declared target."""
# /// flext-command
# verb = "build"
# what = "grpc"
# domain = "build"
# summary = "Generate canonical Python gRPC modules"
# description = "Runs the canonical _grpc target for projects that own proto schemas."
# example = "make build WHAT=grpc PROJECT=flext-grpc APPLY=Y"
# target = "_grpc"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to generate modules", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["build"]
# ///
