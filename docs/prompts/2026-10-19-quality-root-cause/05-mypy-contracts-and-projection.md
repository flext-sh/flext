# Repair Mypy projection and remaining source contracts

## Authority

Read [the current FLEXT session router](../../../.agents/commands/flext-law.md)
and [this task collection](README.md) before execution. This file supplies only
the task-specific owner, diagnosis and acceptance delta.

## Exclusive ownership

Own Mypy template projection and source-level Mypy defects, coordinating template writes with prompt 01.

## Sources to inspect

flext-infra/src/flext_infra/config/tooling.yaml; templates/project/base/pyproject.toml.j2; flext-core/src/flext_core/_models and _utilities/model_options.py; dependency constraint owners.

## Required correction

First verify whether existing ruling-disable-error-codes [call-arg, prop-decorator] is still explicitly authorized and architecturally necessary, then ensure projection follows the current elected policy. Do not add new exemptions. Inspect m.Field facade typing, Pydantic preset MRO/model_construct compatibility and unreachable branches at their real owners. Investigate the removed mypy constraint through current toolchain/dependency authority; do not blindly pin an older tool.

## Acceptance evidence

Run memory-capped Mypy only through native Make, plus runtime model construction/validation tests and affected type gates. Separate lost policy projection from actual source defects. Historical full check had 59 Mypy findings; operator supplied an earlier 41-error output. Neither is a current verdict.
