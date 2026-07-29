# Configuration Standards

This document owns FLEXT configuration and generated-projection rules. It applies to
settings models, configuration files, environment bindings, templates, generators,
tests, examples, and executable documentation.

## Ownership

Every configurable fact has one typed owner:

1. a Pydantic settings/configuration model defines its type and validation;
2. an explicitly documented config file supplies project-controlled values;
3. a generator model owns values projected into managed artifacts.

Consumers receive the validated model or its typed branch. They do not read a second
file, duplicate a default, or access `os.environ` directly from application source.

## Precedence

A settings owner documents precedence explicitly. The normal order is constructor or
command input, environment binding, project config, then model default. Do not create
implicit fallback chains in consumers. Missing required input returns a typed failure
at the boundary that loads configuration.

## Secrets

Secret values use Pydantic secret types or an approved secret provider. Never place
credentials in tracked config, examples, logs, generated artifacts, command output,
or test snapshots. Validation errors identify the field and source without echoing its
value.

## Managed projections

A file is generated only when it has an explicit generated marker or an accepted ADR
names its generator. Each managed projection must have:

- a canonical model/template source;
- a deterministic generator;
- a documented canonical command;
- a check mode that does not mutate the workspace;
- an idempotence test requiring an empty second generation diff.

Do not classify all files of a given type as generated. Curated documentation and
package-specific custom sections remain authored sources unless marked otherwise.

## Tests and examples

Tests validate behavior for arbitrary valid configuration. Expected project-owned
values come from the same typed owner used by production or from a complete
source→generator→consumer round trip. Goldens may lock structure, ordering, and
external protocol constants, but not today's endpoint, path, identifier, ranking,
model name, or default.

Use temporary directories and isolated environment mappings. Tests must not mutate the
active workspace, user environment, or shared tool configuration.

## Change procedure

1. Locate the typed owner, all readers, and any generated projections.
2. Change the owner and update consumers without a compatibility fallback.
3. Validate representative valid, missing, malformed, and secret-bearing input.
4. Generate once in isolation, validate with the real consumer, generate again, and
   require no second diff.
5. Run owner tests, direct-consumer tests, and configuration/documentation gates.

## References

- [`AGENTS.md`](../../AGENTS.md)
- [`docs/architecture/adr/004-generic-make-framework-in-flext-tests.md`](../architecture/adr/004-generic-make-framework-in-flext-tests.md)
- [`.agents/skills/lib-pydantic-settings/SKILL.md`](../../.agents/skills/lib-pydantic-settings/SKILL.md)
