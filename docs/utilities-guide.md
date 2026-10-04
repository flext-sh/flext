# FLEXT Utilities Usage Guide

## Overview

Use the owning package's public `u` facade. `flext-core` owns generic conversions
and collection operations; domain packages compose those utilities with their own
behavior. A utility is not a service locator or a replacement for a public API.

Each Python block below includes its imports and sample inputs. The samples are
demonstration data, not application configuration or assertions about configured
defaults. Run them against the candidate's installed public packages through the
root documentation validation route before treating them as runtime evidence.

## Utilities Architecture

### Inheritance Hierarchy

The utility facade inheritance follows the library dependency direction:

- `FlextCliUtilities` extends `FlextUtilities` from `flext-core`.
- `FlextLdifUtilities` extends `FlextCliUtilities`.
- `FlextLdapUtilities` extends `FlextLdifUtilities`.

Core methods are inherited directly, such as `u.to_str` and `u.join`. Domain
extensions have their published namespaces, such as `u.Cli`, `u.Ldif`, and
`u.Ldap`. Do not infer a method from a namespace name: read the declaration and
its facade before calling it.

### Import Pattern (MANDATORY)

Import the facade from the public package root. Do not import `_utilities`
implementation modules or create a second conversion implementation.

```python
from flext_core import u

label = u.to_str("example")
words = u.to_str_list(["first", "second"])
joined = u.join(words, separator=", ")
print(label, joined)
```

## Centralized Utilities in flext-core

The `u` facade composes the owning utility classes through MRO. Its implementation
is not a fixed method-count catalog; use the current public reference and source
when selecting an operation.

### String conversion

`u.to_str` accepts a JSON-compatible payload or `None` and returns a string.
For `None`, the caller can supply `default`; the method owns its behavior when
that argument is omitted. It does not validate a business payload or replace
Pydantic parsing at an input boundary.

```python
from flext_core import u

whole_number = u.to_str(12.0)
fraction = u.to_str(12.25)
label = u.to_str("example")
print(whole_number, fraction, label)
```

### Sequence conversion

`u.to_str_list` converts its input to a string sequence. It is not a nested-list
filter or a truthiness filter. Do not call the former guide's
`to_str_list_safe` or `to_str_list_truthy`: those methods are not declared by the
current core conversion owner.

```python
from flext_core import t, u

source: t.StrSequence = ("first", "second")
converted = u.to_str_list(source)
joined = u.join(converted, separator=" / ")
print(joined)
```

Use the typed input contract required by the consumer rather than assuming that
any nested collection is accepted or that a conversion rejects invalid domain
data. A conversion method with a caller-supplied default is not a fail-fast
validation boundary.

### Configuration-derived inputs

Read runtime knobs from the package's typed settings owner. Do not copy the
current debug value into a sample or assert that it is enabled or disabled.

```python
from flext_core import settings, u

debug_label = u.to_str(settings.debug)
print(debug_label)
```

For business rules, consume the owning package's typed `config` branch. Pass
the required values explicitly into services through their declared protocols;
services must not look up settings or configuration through a utility singleton.

## Project-Specific Utilities

### flext-ldif Utilities (extending flext-core)

Import `u` from `flext_ldif` for inherited core utilities and the `u.Ldif`
extension. The following sample performs a pure DN-value escaping operation; it
does not connect to a directory or choose a server dialect.

```python
from flext_ldif import u

values = u.to_str_list(["Example", "User"])
escaped_value = u.Ldif.esc(u.join(values, separator=", "))
print(escaped_value)
```

LDIF parsing belongs to the public `FlextLdif.parse_ldif` API, inherited from its
parser service and routed through the server registry. `u.Ldif.parse_entry` is
not that public parsing boundary. Supply application settings and dependencies
at the composition root; do not select an internal dialect handler directly.

### flext-ldap Utilities (extending flext-ldif)

`flext_ldap.u` inherits the LDIF and core utility surfaces and publishes LDAP
helpers through `u.Ldap`. Directory connection and synchronization are use cases
of the public `FlextLdap` facade, not generic utility operations.

### flext-cli Utilities (extending flext-core)

`flext_cli.u` inherits core conversions and exposes CLI-domain helpers through
`u.Cli`. Use the declared public operation for output, templates, structured
files, and workflow execution. Do not assume a generic `filter(...).map(...)`
chain exists on the utilities facade; result composition belongs to `r`.

## Best Practices

- Reuse the current public owner rather than copying implementation code.
- Use `t` aliases and `p` protocols for consumer annotations, and `m` presets for
  validated data declarations.
- Parse external JSON once with the owning model's `model_validate_json`; keep
  typed models inside the use case and serialize with `model_dump` at the output
  boundary.
- Keep pure utilities separate from settings discovery, dependency construction,
  I/O, and use-case orchestration.
- Do not invent methods or signatures from a historical guide. In particular,
  `find_callable` is not declared by the current core mapper owner.
- Propagate failure according to the actual result contract. Never replace an
  exception with an empty successful payload to keep an example running.

## Adding New Utilities

### When to Add to flext-core

Add behavior only when a current consumer needs it and the existing public owner
does not provide it. Generic behavior belongs in core; domain-specific behavior
belongs in that domain. A service dependency belongs behind a protocol, not in a
new global utility registry.

### How to Add

Change the canonical implementation owner, publish its declared public surface,
and regenerate projections through the root Make route. Do not hand-edit
generated utility facades. Add real public-behavior tests and a self-contained
example of the resulting operation in the same change.

The earlier `new_method` skeleton with an Ellipsis result was not an
implementation. A runnable guide must call a real public operation, as the
examples above do, rather than wrapping an unfinished body in a successful result.

## Quality Standards

Executable documentation is first-class code. Imports, annotation resolution,
lint, type checking, and actual public behavior must all be checked on the
candidate environment. A source inspection or an old green report is not a
runtime receipt.

Run the applicable root Make lifecycle and documentation gates under the
coordinator's serialized validation slot. Preserve failures, warnings, and
complete audit reports; never disable a check or relabel an executable example
to avoid validation.

## See Also

- [Type system architecture](type-system-architecture.md)
- [Architecture decisions](architecture/adr/)
- [Stabilization checkpoint](ways-of-working/stabilization-checkpoint-0.12.md)
