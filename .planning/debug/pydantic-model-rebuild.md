---
status: investigating
trigger: "ServiceRegistrationSpec model_rebuild() error during make codegen - p not defined via TYPE_CHECKING"
created: 2026-03-21T00:00:00Z
updated: 2026-03-21T00:00:00Z
---

## Current Focus

hypothesis: ServiceRegistrationSpec has ForwardRef fields (services, factories, resources, container_config) that need model_rebuild() after all inner classes are defined
test: Check if ServiceRegistrationSpec.model_rebuild() is called anywhere; inspect field annotations
expecting: Find ForwardRefs in the model and no corresponding model_rebuild()
next_action: Determine correct placement for model_rebuild() call

## Symptoms

expected: make codegen should complete without errors related to Pydantic model_rebuild
actual: Error message "ServiceRegistrationSpec is not fully defined; you should define `p`, then call `ServiceRegistrationSpec.model_rebuild()`"
errors: Pydantic complaining about undefined `p` during model_rebuild
reproduction: Run `make codegen` in flext-core
started: After codegen refactor to use Jinja2 templates

## Eliminated

(none yet)

## Evidence

- Evidence 1: Lines 361, 370 in container.py have comments referencing p.Settings and p.Context (but p is NOT imported in container.py; only `BaseModel | None` is used, so that's correct)
- Evidence 2: `p` is NOT imported in _models/container.py - confirmed via TYPE_CHECKING import check. This is correct design (TIER 0.5 avoids cycles)
- Evidence 3: ServiceRegistrationSpec has ForwardRef fields at runtime:
  - services: ForwardRef("...FlextModelsContainer.ServiceRegistration...")
  - factories: ForwardRef("...FlextModelsContainer.FactoryRegistration...")
  - resources: ForwardRef("...FlextModelsContainer.ResourceRegistration...")
  - container_config: ForwardRef("...FlextModelsContainer.ContainerConfig...")
- Evidence 4: These inner classes (FactoryRegistration, ResourceRegistration, ContainerConfig) ARE defined in the same FlextModelsContainer class BEFORE ServiceRegistrationSpec uses them
- Evidence 5: No model_rebuild() call exists for ServiceRegistrationSpec anywhere in codebase
- Evidence 6: model_rebuild() IS used in flext-core/tests/models.py for models with recursive/forward reference types

## Resolution

root_cause: ServiceRegistrationSpec references inner classes via string annotation, creating ForwardRefs that never get resolved. Missing model_rebuild() call after class definition.
fix: (pending - investigating best placement)
verification: (pending)
files_changed: []
