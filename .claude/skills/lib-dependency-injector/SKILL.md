<!-- TOC START -->

- [Scope](#scope)
  - [Subproject Usage Map](#subproject-usage-map)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: lib-dependency-injector
description: dependency_injector bridge patterns for FLEXT runtime and container internals. Trigger when adding DI wiring, provider registration, or scoped test containers.

---

## Scope

- Primary implementation: `flext-core/src/flext_core/runtime.py`, `flext-core/src/flext_core/container.py`
- Public contracts: `flext-core/src/flext_core/protocols.py`
- Usage validation: `flext-core/tests/unit/test_runtime_utils.py`, `flext-core/tests/unit/test_di_incremental.py`
- Dependency pins: `flext-core/pyproject.toml`

### Subproject Usage Map

- `flext-core`: owns all direct `dependency_injector` imports and bridge APIs.
- `flext-cli`, `flext-quality`, `flext-meltano`, `flext-api`, other `flext-*`: consume `FlextContainer`/`FlextRuntime` APIs only; no direct DI framework imports.
- `flext-core/tests/*`: verifies bridge semantics (`create_layered_bridge`, `register_factory`, `register_resource`, `wire`).

## References

- `AGENTS.md` — canonical governance source
- `flext-core/src/flext_core/runtime.py`: `class DependencyIntegration`, `class BridgeContainer`, `Provide`, `inject`
- `flext-core/src/flext_core/container.py`: `class FlextContainer`, `_services/_factories/_resources`, `scoped()`
- `flext-core/src/flext_core/protocols.py`: `class DI(Protocol)` signatures (`register`, `get_typed`, `wire_modules`)
- `flext-core/tests/unit/test_runtime_utils.py`: real execution checks for `register_object/register_factory/register_resource`
- `flext-core/tests/unit/test_di_incremental.py`: bridge creation and provider behavior
- `flext-core/pyproject.toml`: `dependency-injector>=4.41.0`

## Rules

- Never import `dependency_injector` directly in app/business modules; import `FlextContainer`/`FlextRuntime` bridge APIs.
- Keep provider registration in `FlextContainer` and `FlextRuntime.DependencyIntegration` only.
- Use `scoped()` for test isolation and subproject-specific overlays.
- Keep registries typed and explicit:
  - `_services: dict[str, m.Container.ServiceRegistration]`
  - `_factories: dict[str, m.Container.FactoryRegistration]`
  - `_resources: dict[str, m.Container.ResourceRegistration]`
- Keep bridge components layered and synchronized:
  - `_di_bridge: containers.DeclarativeContainer`
  - `_di_services: containers.DynamicContainer`
  - `_di_resources: containers.DynamicContainer`
  - `_di_container: containers.DynamicContainer`
- Always use `Provide`/`inject` from runtime bridge (`FlextRuntime.DependencyIntegration.Provide`, `.inject`).
- **Zero Tolerance for Hacks**: Prohibited use of `model_rebuild()`, `eval()`, `exec()`, `cast()`, and `inline imports`. Wait for definition time or use Protocol decoupling.
## Instructions

- Follow these declarations and signatures exactly when extending DI:

```python
class FlextRuntime:
    class DependencyIntegration:
        class BridgeContainer(containers.DeclarativeContainer):
            config = providers.Configuration()
            services = providers.DependenciesContainer()
            resources = providers.DependenciesContainer()

        Provide = wiring.Provide
        inject = staticmethod(wiring.inject)

        @classmethod
        def create_layered_bridge(
            cls, config: ConfigMap | None = None
        ) -> tuple[
            containers.DeclarativeContainer,
            containers.DynamicContainer,
            containers.DynamicContainer,
        ]: ...
```

```python
class FlextContainer(FlextRuntime, p.DI):
    def initialize_di_components(self) -> None: ...
    def register(self, name: str, service: t.RegisterableService) -> r[bool]: ...
    def register_factory(
        self,
        name: str,
        factory: p.ResourceFactory[t.RegisterableService],
    ) -> r[bool]: ...
    def register_resource(self, name: str, factory: p.ResourceCallable) -> r[bool]: ...
    def get(self, name: str) -> r[object]: ...
    def get_typed[T](self, name: str, type_cls: type[T]) -> r[T]: ...
    def wire_modules(
        self,
        *,
        modules: Sequence[ModuleType] | None = None,
        packages: Sequence[str] | None = None,
        classes: Sequence[type] | None = None,
    ) -> None: ...
    def scoped(...) -> FlextContainer: ...
```

- Import patterns to keep:
  - `from flext_core import FlextContainer`
  - `from flext_core import FlextRuntime`
  - `from flext_core import inject` only where exported by package API.
- Registration intent:
  - `register` -> concrete object provider (`providers.Object`)
  - `register_factory` -> `providers.Singleton` or `providers.Factory` via `cache`
  - `register_resource` -> `providers.Resource`

## Workflow

1. Inspect `runtime.py` and `container.py` signatures before editing behavior.
2. Keep direct framework calls in `DependencyIntegration` and `FlextContainer` only.
3. If adding provider types, mirror updates in `p.DI` protocol signatures.
4. Validate scoped behavior by checking `scoped()` cloning semantics (`services/factories/resources`).
5. Verify no new `dependency_injector` imports appear outside `flext-core` bridge files.

## Examples

Good:

```python
from flext_core import FlextContainer

container = FlextContainer.get_global()
_ = container.register_factory("token_factory", lambda: {"token": "abc123"})


@container.inject
def consume(token=container.provide["token_factory"]):
    return token
```

Why good: uses bridge API, keeps app code framework-agnostic, and stays compatible with `scoped()`.

Bad:

```python
from dependency_injector import containers, providers


class AppContainer(containers.DynamicContainer):
    token_factory = providers.Factory(lambda: {"token": "abc123"})
```

Why bad: bypasses `FlextContainer` registries and runtime bridge, breaks project rule that direct DI imports remain in bridge layer.

Good:

```python
test_container = FlextContainer.get_global().scoped(
    subproject="tests",
    services={"clock": "fake-clock"},
)
```

Why good: isolated scope avoids polluting global singleton state in tests.

Bad:

```python
container = FlextContainer.get_global()
_ = container.register("clock", "fake-clock")
# no cleanup, mutates shared singleton for unrelated tests

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

```

Why bad: shared mutable DI state causes cross-test leakage.

## Verification

Make gates:

- `make check PROJECT=flext-core` — lint + type gates verify DI import boundaries
- `make test PROJECT=flext-core` — DI integration tests
- `make validate PROJECT=flext-core` — complexity gates

Pattern checks:

- `rg -n "from dependency_injector|class DependencyIntegration|class BridgeContainer|Provide = wiring\.Provide|inject =" flext-core/src/flext_core/runtime.py`
- `rg -n "class FlextContainer|def register\(|def register_factory\(|def register_resource\(|def get_typed|def scoped\(|_services: dict\[str, m\.Container\.ServiceRegistration\]" flext-core/src/flext_core/container.py`
- `rg -n "class DI\(|def wire_modules\(|def get_typed" flext-core/src/flext_core/protocols.py`
- `rg -n "create_layered_bridge|register_factory|register_resource|wire\(" flext-core/tests/unit/test_runtime_utils.py flext-core/tests/unit/test_di_incremental.py`
- `rg -n "dependency-injector>=4\.41\.0" flext-core/pyproject.toml`
- `rg -n "from dependency_injector" flext-*/src | rg -v "flext-core/src/flext_core/(runtime|container)\.py"`
