# Canonical Settings & Config Pattern (ADR-005 companion guide)

## Contract and ownership

[ADR-005](adr/005-config-settings-constants-templates-schemas-ssot.md) owns the
configuration decision. Settings and config are independent public owners:

- `settings` exposes typed runtime inputs, including environment-tunable knobs.
- `config` exposes validated business rules and declarative inputs.
- `c` exposes invariant constants, not copied configuration values.

Import the owning package's published objects at the composition root. Use the
fields that the package actually declares; there is no universal `X` namespace
that consumers may invent. A service receives required configuration values and
dependencies explicitly instead of looking up a process-global singleton.

## Read settings through the public owner

`FlextSettings` in core supplies the settings foundation. Package settings
subclasses add their actual fields and publish their settings object at the root.
The following block reads the inherited debug knob without asserting its default:

```python
from flext_cli import settings

print(settings.debug)
```

Field definitions, validation, environment names, and namespace shape belong to
the declaring package. Do not copy endpoint, retry, timeout, or logging defaults
from this guide into application code or tests. Do not clone the old guide's
synthetic settings class to create a competing owner.

## Read configuration through its typed domain

The CLI configuration owner validates its loaded YAML through its configuration
models and publishes a typed `Cli` domain. Its declared identity fields are
`name` and `version`:

```python
from flext_cli import config

print(config.Cli.name, config.Cli.version)
```

The sample consumes the same typed SSOT as production, not a duplicate mapping
or a frozen expectation of today's package identity. The underlying core config
foundation is frozen; a package's typed domain model owns its field validation.
Do not infer that every package permits arbitrary extra fields because a loader
uses an open intermediate representation.

## Declaration and loading boundaries

Keep configuration and settings declarations below their facade consumers in
the dependency graph. The core loading foundations own file discovery and
settings parsing. Package configuration owners own the validation of their
declared domains. Any generated facade is a projection of those declarations,
not a second place to implement loading behavior.

Core configuration discovery resolves the declaring package's configuration
directory, including its packaged distribution and declared overrides. It does
not make business rules depend on the caller's current working directory. The
package owns the schema, declaration, and loading path together; a consumer must
not reconstruct that path or read arbitrary environment variables itself.

MRO composition follows the current package declarations. Do not impose the old
guide's blanket ban on inheritance composition, invent raw Pydantic namespace
classes at consumers, or use typing-only branches to hide unresolved runtime
annotations.

## Publication and change procedure

Change the existing canonical declaration, schema, or configuration input.
Publish symbols through the owner's explicit public exports and regenerate
derived surfaces through root `make gen` under the authorized lifecycle. Never
hand-edit the package's generated `__init__.py` or generated configuration files.

Validate the real public consumer with the candidate's physical environment,
then run the applicable root checks, tests, and documentation gates. Tests and
executable documentation read expected configurable facts from the same typed
owner; valid configuration changes must not break hardcoded expectations.

## Consumer boundaries

- Parse owned external payloads through the appropriate model boundary.
- Read published typed fields rather than subscripting an unchecked mapping.
- Inject dependencies and the required configuration values at the public API.
- Keep pure utilities independent of service construction and global lookup.
- Remove superseded declarations and consumers in the same cutover. Never add
  compatibility aliases, lazy import repairs, or model rebuilding at consumers.

Configuration records such as `m.ConfigDocument` describe validated data at a
loader boundary; they are not replacements for a package's live `config` owner.
Use the public CLI loading operation when a use case requires file loading,
rather than implementing a second YAML or schema engine locally.

## See Also

- [Type system architecture](../type-system-architecture.md)
- [Utilities usage](../utilities-guide.md)
- [Settings/config singleton contract](adr/016-settings-config-singleton-contract.md)
