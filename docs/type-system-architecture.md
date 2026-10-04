# FLEXT Type System Architecture Guide

## Overview

FLEXT separates type aliases (`t`), dependency protocols (`p`), and validated data
models (`m`). These public facades have different responsibilities; none is a
substitute for another. Import them from the owning package root, not its private
family modules.

Each Python example is independent and includes its imports and input data.
Examples demonstrate the public contract, not a fleet-wide validation result.
They require execution in the candidate environment through the documentation
validation route before they can be cited as runtime evidence.

## Type System Hierarchy

### Project Dependency Order

`flext-core` owns the foundation contracts. `flext-cli` extends core;
`flext-ldif` consumes core and CLI; `flext-ldap` consumes those foundations and
LDIF. Dependencies point toward the foundation, never from core to a consumer.

### Architecture Layering within Projects

The facade order is `c -> t -> p -> m -> u`. Config/settings are layer-0 owners:
settings reads external runtime inputs, and config owns validated business rules.
Forward dependencies may be runtime imports. Reverse dependencies must remain
typing-only and must not create unresolved runtime model annotations.

Declarations belong to constants, typings, protocols, and models. Utilities and
services own behavior, the public API wires dependencies explicitly, and the CLI
adapts transport input and output. Generated facade files are projections; change
their canonical owners and regenerate rather than editing the projections.

## Canonical Type Patterns

### Simple type contracts

Reuse an existing alias when it already expresses the contract. The core owner
declares `t.Scalar`, `t.StrSequence`, and `t.MappingKV` among its public aliases.
Do not introduce a duplicate domain alias for the same meaning.

```python
from flext_core import t, u

label: t.Scalar = "example"
names: t.StrSequence = ("first", "second")
print(label, u.join(names, separator=", "))
```

### Validated models at boundaries

Use an `m` preset for owned model declarations. Consumers construct the actual
public model, not an imagined `m.Domain.InputModel` or `m.Tests.ValueModel`.

`m.ConfigDocument` is the existing frozen record for parsed configuration data
and optional source/schema references. This sample is a record serialization
round-trip, not an installation of application settings or business rules.

```python
from flext_core import m

document = m.ConfigDocument.model_validate_json('{"data":{"label":"example"}}')
serialized = document.model_dump_json()
restored = m.ConfigDocument.model_validate_json(serialized)
print(restored.model_dump(mode="json"))
```

The model owner supplies validation and defaults. Do not copy those defaults
into expectations or turn a mapping into a second data contract. JSON enters via
`model_validate_json`; model serialization happens at the output boundary.

### Protocol-based consumer interfaces

Use the smallest existing protocol that provides the capability consumed by the
function. For example, `p.Model` describes model-instance serialization and
copying; it is not the concrete model constructor.

```python
from flext_core import m, p, t


def serialize_model(value: p.Model) -> t.JsonDict:
    """Serialize a validated model through its public instance protocol.

    Returns:
        The model's JSON-compatible output mapping.
    """
    return value.model_dump(mode="json")


document = m.ConfigDocument.model_validate_json('{"data":{"label":"example"}}')
print(serialize_model(document))
```

The composition root supplies the validated instance. The consumer does not
resolve a dependency by string, access a container singleton, or import a private
implementation.

### Result contracts

Annotate consumer results through `p.Result` and construct them through `r`.
Do not use a result as permission to accept an unvalidated payload or manufacture
success after a failure.

```python
from flext_core import p, r

result: p.Result[str] = r[str].ok("example")
print(result.unwrap())
```

## Namespace Architecture

### Standard Namespace Structure

Core aliases and presets may be published directly on their facades. Domain
declarations use their published domain namespace, for example `m.Ldif.Entry`.
The spelling is determined by the declaring owner, not by a blanket rule that
every symbol must have an extra namespace level.

### Namespace Organization by Project

Use the project's facade to inherit upstream contracts and expose its own domain
declarations. A namespaced alias does not justify a second definition at another
level. Keep family declarations flat and use MRO composition as specified by
[ADR-014](architecture/adr/014-family-part-shape-rope-codemod-rules.md).

### Models Namespace Architecture (m.*)

An owned model extends an appropriate public `m` preset, such as `m.FrozenModel`
or `m.StrictBoundaryModel`, rather than a raw Pydantic base at a consumer.
Choose the preset for the actual validation/mutability contract. Resolve its
annotations at the declaration owner; `model_rebuild` is not an import repair.

Do not annotate a consumer with a concrete model when a `p` capability or a `t`
alias is the declared boundary. Construct and validate through `m`; consume
through the appropriate protocol.

## Covariance and Variance Rules

### Covariance (Subtype Compatibility)

`t.MappingKV` is backed by `collections.abc.Mapping`, and `t.SequenceOf` is backed
by `collections.abc.Sequence`. Both are read-only contracts with covariance in
their value/item parameter. `dict` and mutable collections are invariant. Sequence
is not invariant merely because it is more restrictive than Iterable.

Select `t.IterableOf` when the operation only needs iteration, `t.SequenceOf` when
it needs sequence operations, and a mutable alias only when mutation is required.

```python
from flext_core import t, u

tuple_names: t.StrSequence = ("first", "second")
list_names: t.StrSequence = ["first", "second"]
print(u.join(tuple_names), u.join(list_names))
```

### Protocol Return Types

Return a read-only collection contract when callers only read it. Covariance
does not make unrelated element types compatible: a Boolean mapping is not a
mapping of arbitrary Pydantic models. A protocol also does not make calls with
different argument counts interchangeable.

### Type Parameter Bounds

A bound specifies capabilities required of a type parameter; it does not imply
covariance. Python's PEP 695 syntax expresses generic parameters locally. Reuse
the existing public aliases instead of inventing `t.M`, `t.S`, or `t.R` exports
based on an old TypeVar inventory. Add a generic abstraction only when its
consumer needs it.

## Protocol Design

### Protocol Organization Rules

- Declare the exact operations consumed at a dependency boundary.
- Keep implementation dependencies out of protocol declarations. Respect the
  facade dependency direction for any annotations.
- Use `runtime_checkable` only for a deliberate runtime structural check. Such
  a check verifies member presence, not payload validation or every annotation.
- Use `Self` only for an operation whose real implementation returns itself;
  do not invent fluent methods to illustrate chaining.

The existing `p.Model` protocol is runtime-checkable. A validated public model
can be inspected without a local duplicate protocol definition:

```python
from flext_core import m, p

document = m.ConfigDocument.model_validate_json('{"data":{"label":"example"}}')
print(isinstance(document, p.Model))
```

## TypeVar Organization

Prefer the canonical aliases and declared generic protocols. An unresolved
quoted bound does not solve a circular dependency, and `TYPE_CHECKING` does not
provide names required when a model evaluates its annotations at runtime.
Repair the owning declaration and dependency direction; never add lazy imports,
compatibility aliases, or `model_rebuild` in a consumer.

## Migration Guide

### Migrating from Old Patterns to New

Replace a duplicate alias with the existing canonical owner and rewire all
consumers in the same change. Do not retain an old nested alias for several
releases. Replace unions of incompatible callbacks only with a protocol whose
actual callers and implementations agree on one signature.

Model construction is not a cast. Parse at the external boundary, pass the
validated model through its protocol, and serialize only when leaving the use
case. Do not copy the previous guide's incomplete class bodies or demonstration
calls that reference undefined models.

## Best Practices

- Import only published package-root symbols.
- Reuse `t` aliases, `p` protocols, and `m` presets at their intended boundaries.
- Read configurable facts from the same typed SSOT production consumes. Never
  assert today's configured values in a test or executable document.
- Keep declaration layers free of business behavior and inject service
  dependencies explicitly at the API composition root.
- Remove superseded definitions and examples instead of preserving a parallel
  compatibility surface.

## Project Status

This guide defines contracts; it does not certify every project as lint-clean or
type-safe. The former fixed counts and blanket green matrix were not current
validation evidence. Acceptance requires the candidate SHA, physical environment,
canonical command, exit status, warnings, and decisive report for each declared
scope.

## Summary

Aliases describe values, protocols describe capabilities, and models validate
owned data. Reuse their public owners without duplicating contracts or reversing
dependencies. Validate the executable examples and the changed documentation
through the root Make lifecycle; never relabel code to evade a failing check.

## See Also

- [Utilities usage](utilities-guide.md)
- [Architecture decisions](architecture/adr/)
- [Stabilization checkpoint](ways-of-working/stabilization-checkpoint-0.12.md)
