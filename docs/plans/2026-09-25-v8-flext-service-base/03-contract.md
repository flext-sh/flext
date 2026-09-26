# 03 — Target contract (normative)

<!-- TOC START -->

- [1. Layer roles](#1-layer-roles)
- [2. Service](#2-service)
- [3. Ports (S1)](#3-ports-s1)
- [4. Composition root (api.py)](#4-composition-root-apipy)
- [5. Operations are the API (S3)](#5-operations-are-the-api-s3)
- [6. Derived CLI (cli.py, S5)](#6-derived-cli-clipy-s5)
- [7. Settings, config and the runtime hook](#7-settings-config-and-the-runtime-hook)
- [8. Failure semantics](#8-failure-semantics)
- [9. Forbidden forms](#9-forbidden-forms)
- [10. Migration of existing code](#10-migration-of-existing-code)

<!-- TOC END -->

This is the pattern the whole fleet follows. It feeds
`flext-core/docs/guides/service-patterns.md` (S1–S3, S5) and ADR-019. The slice that
makes each piece available is in parentheses.

## 1. Layer roles

Sources: flext-law `:31-50,100-102`, `internal-clean-architecture` `:15-19`, ADR-010
`:104-105`.

| Layer            | File or folder                                                 | Role                                                          | May import                                                                                   |
| ---------------- | -------------------------------------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| External input   | `_settings.py`, `settings` singleton                           | Environment and CLI knobs                                     | stdlib, Pydantic (through the core), upstream base                                           |
| Business facts   | `_config.py`, `config/*.yaml`, `config` singleton              | Validated rules                                               | Same                                                                                         |
| Declarations     | `c → t → p → m → u`                                            | Data, types, contracts, models, helpers                       | The lower layer; reverse imports only under `TYPE_CHECKING`                                  |
| Project base     | `base.py`                                                      | `class Flext<X>ServiceBase(s[...])`, `s = …`, runtime hook    | Declarations                                                                                 |
| Use cases        | `services/`                                                    | One service per use case                                      | Declarations and `p` ports at runtime; never an adapter, executable, global or other service |
| Adapters         | A package folder outside `services/` (for example `adapters/`) | Implement ports                                               | Declarations and the owner's third-party libraries (tier-whitelist)                          |
| Composition root | `api.py`                                                       | **Only** place that builds adapters and port-bearing services | Everything above                                                                             |
| Transport        | `cli.py`                                                       | Translates input and propagates the first failure             | `api.py` and `flext-cli`                                                                     |

Existence rule (D1 = A, S7): `api.py` exists only when the project composes services;
`cli.py` only with a console script **and** operations. The kernel has neither, nor
`base.py`, nor a console script. An empty facade or a no-op `main()` is a violation.

## 2. Service

```python
class FlextLdapSearch(s[m.Ldap.SearchResult]):
    """LDAP search use case."""

    connection: t.Port[p.Ldap.Connection] = m.Field(
        exclude=True, description="Bound LDAP connection used for every search."
    )

    def search(self, request: m.Ldap.SearchRequest) -> p.Result[m.Ldap.SearchResult]:
        """Search entries under a base DN."""
        return self.connection.search(request)
```

- Extends the project base (`s`), which extends the core `FlextService`.
- The service module imports `p`, `t` and `m` **at runtime**: Pydantic resolves field
  annotations when the class is created and `model_rebuild` is forbidden. Service to
  declarations is a forward import.
- Fields are ports or business parameters filled by the root from `config`/`settings`.
- A service never calls another service's `fetch_global()`, never reads global
  `settings`/`config`, and never builds infrastructure (including
  `u.PrivateAttr(default_factory=…)` that creates a facade or adapter).

## 3. Ports (S1)

```python
class FlextLdapProtocolsConnection:
    @runtime_checkable
    class Connection(p.Base, Protocol):
        """Bound LDAP connection capability consumed by the search use case."""

        def search(
            self, request: m.Ldap.SearchRequest
        ) -> p.Result[m.Ldap.SearchResult]: ...
```

- A port is a `@runtime_checkable` Protocol extending `p.Base` with the minimal consumed
  capability, published as `p.<Ns>.<Name>`. Its type is a **plain Protocol class**; a
  subscripted generic or a TypeVar is rejected when the service class is created.
- Field form: `name: t.Port[p.<Ns>.<Port>] = m.Field(exclude=True, description="…")`,
  with `t.Port[P] = Annotated[P, SkipJsonSchema()]`. Pydantic validates by `isinstance`
  on construction and on assignment. `exclude=True` stays on the field.
- Forbidden on a port: `SkipValidation`, `InstanceOf[concrete class]`, a `None` default,
  a `default_factory` that builds infrastructure, a concrete type.
- Runtime seeds are the only typed absence:
  `runtime_settings: t.Port[p.Settings | None]` and
  `initial_context: t.Port[p.Context | None]` (never `t.Port[p.X] | None`, which
  publishes `{"type": "null"}`). Every runtime-only field of `x`, including
  `settings_type`, is out of the JSON Schema.

## 4. Composition root (`api.py`)

Pure DI (default):

```python
class FlextLdap(FlextLdapSearch, FlextLdapModify):
    """LDAP facade: the composed service."""


ldap: FlextLdap = FlextLdap(connection=FlextLdapConnection(settings=settings.Ldap))
```

- A shared adapter is a variable passed to several constructors. Constructing an adapter
  performs no I/O; connecting happens on first use, so importing `api.py` (and the CLI's
  `--help`) touches no infrastructure.
- Truthful container (S2): the `FlextContainer` stays the registry of the core runtime;
  empty, duplicate and reserved names fail through one write path; services and adapters
  never call it.
- Protocol keys and `compose` (S2b, conditional):
  `container.bind(p.Ldap.Connection, adapter)` then `FlextLdap.compose(container)`, only
  if the signature type-checks cleanly under mypy (`type-abstract`), pyright and
  pyrefly; otherwise D3 goes to the operator and the fleet keeps pure DI. `compose`
  fills only required `t.Port` fields; two ports of one Protocol need an explicit
  argument.
- `fetch_global()` stays for port-free services; a port-bearing service's
  `fetch_global()` raises `ValidationError`, which is the correct, tested behavior.

## 5. Operations are the API (S3)

- **Which methods:** plain functions (per `inspect.getattr_static`), public, declared in
  MRO classes below `FlextService`. Excluded: every name in `dir(FlextService)` even
  when overridden (`execute`, `track`, `model_*`, …), properties, computed fields,
  classmethods, staticmethods, Pydantic validators and serializers.
- **Shape:** `def name(self) -> p.Result[X]` or
  `def name(self, request: M) -> p.Result[X]` with `M` a Pydantic model subclass; a
  one-line docstring; not async, not generic; no `*args`/`**kwargs`, keyword-only
  parameters or defaults. The return type is left to the static checkers.
- **Discovery:** `u.service_operations(ServiceType)` is **lazy** (called by the CLI and
  tools, never at class creation) and returns frozen `m.ServiceOperation` values (name,
  summary, request model or `None`). Annotation resolution without `eval`: read
  `inspect.get_annotations(func)` unevaluated, require a dotted name, resolve its first
  part in `func.__globals__` and the rest by `getattr`, require a Pydantic model
  subclass. It raises `TypeError` naming the operation, annotation, module and fix on a
  wrong shape, a missing docstring, an unresolvable name, a sibling-class name
  collision, or a service with zero operations.

## 6. Derived CLI (`cli.py`, S5)

```python
app = cli.create_app_with_common_params(name="flext-ldap", help_text="FLEXT LDAP")
cli.register_result_routes(app, cli.service_routes(FlextLdap, provide=...))
exit_code = cli.finalize_result(cli.execute_app(app, prog_name="flext-ldap"))
```

- The module follows the `cli.py.j2` template (a `Flext<X>Cli` class and the canonical
  `main()` entry, the ADR-014 exception); no loose function, no local import.
- Routes come from the service **class**; the instance comes from the provider only when
  a command executes, so `--help` builds no adapter and needs no configured environment.
  S5 fixes the exact form of `provide` within the one-class-per-module law.
- Each operation becomes one command: kebab-case name, summary help, options from the
  request model (`model_command`); an operation without input uses one shared empty
  model from `flext-cli`.
- The border validates with `model_validate`; invalid input becomes `e.fail_validation`
  with the original `ValidationError` as cause and exits non-zero (`finalize_result`).
  Success is rendered by the `flext-cli` output mechanism.
- Derivation fails loudly on a required `exclude=True` request field or an annotation
  without an option mapping.
- Singer connectors keep ADR-006 (`Service().cli_main(args)`).

## 7. Settings, config and the runtime hook

- `config.<Ns>.*` holds facts, `settings.<Ns>.*` knobs; the core uses `config.*` /
  `settings.*` (D-SET).
- The **root** reads the singletons and passes values through fields or the runtime; a
  service never reads a global (flext-law:44-45).
- The project base declares its settings type once, in the classmethod
  `runtime_bootstrap_options() -> p.RuntimeBootstrapOptions`; the core reads it through
  `p.RuntimeBootstrapProvider` without declaring a method on `x`.
- A base never redeclares `__init__` nor uses `settings or X.fetch_global()`.

## 8. Failure semantics

- The first failure propagates with its cause: inside a result boundary as
  `r.fail(msg, exception=exc)` or `e.fail_*`; outside as a typed `e.*` exception raised
  `from` the cause. Never `None`, `""`, `{}`, a default, a skipped item, a debug log, a
  warning, `ok(True)`, `continue` or `unwrap_or(sentinel)`.
- `unwrap()` chains the carried exception (S1).
- Invalid declarations fail early: port type at class creation, port at construction and
  assignment, operation at discovery.

## 9. Forbidden forms

1. `SkipValidation` on a dependency, including `Annotated[..., t.SkipValidation]`.
2. `getattr(x, "member", default)` on a typed member; attribute-name probes.
3. Hand-rolled singletons (`fetch_instance`, `fetch_global_instance`, local
   `_instance`).
4. `settings or X.fetch_global()`; `__init__` redeclared to inject settings.
5. A service calling another service's `fetch_global()`; infrastructure built inside a
   service, including `PrivateAttr(default_factory=…)`.
6. A no-op `main()`; an empty facade.
7. `except …: return <default>`; `contextlib.suppress` around an owner call;
   `unwrap_or(sentinel)` hiding a failure.
8. `model_copy(update=)` to build an object that must be validated.
9. Tests with mocks, patches, monkeypatching, fakes or frozen config values.
10. Compatibility aliases; old and new paths side by side.

## 10. Migration of existing code

The 217 services without ports keep their behavior; the hook stays the same classmethod
with no mandatory `@override`. Each member adopts the contract in its own bead through
`07-sessions-guide.md`; S7's detection rules count each member's backlog; repeated
patterns go through a `make mod` rule with fixtures and renames through
`flext-infra refactor apply-renames`. A base contract contracts only after its consumers
declared what they use (R17).
