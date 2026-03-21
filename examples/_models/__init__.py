# AUTO-GENERATED BRIDGE FILE
# Dynamically re-exports model classes from flext-core/examples/_models

from __future__ import annotations

from pathlib import Path
from sys import modules

# Dynamically make flext-core/examples/_models available at examples._models
# by adding it to the module namespace
try:
    # First, try to import from the installed flext-core package
    from flext_core.examples import _models as _core_models

    # Re-export everything from flext_core.examples._models
    for attr_name in dir(_core_models):
        if not attr_name.startswith("_"):
            globals()[attr_name] = getattr(_core_models, attr_name)
    # Also allow "from examples._models import *" to work
    if hasattr(_core_models, "__all__"):
        __all__ = _core_models.__all__
    else:
        __all__ = [name for name in dir(_core_models) if not name.startswith("_")]
except (ImportError, AttributeError):
    # Fallback: if flext_core is not installed, try to add the actual path to sys.modules
    flext_core_examples_models = (
        Path(__file__).parent.parent.parent / "flext-core" / "examples" / "_models"
    )
    if flext_core_examples_models.exists():
        # Try loading the module directly from the filesystem path
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "flext_core.examples._models", flext_core_examples_models / "__init__.py"
        )
        if spec and spec.loader:
            _core_models = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(_core_models)
            modules["flext_core.examples._models"] = _core_models
            for attr_name in dir(_core_models):
                if not attr_name.startswith("_"):
                    globals()[attr_name] = getattr(_core_models, attr_name)
            if hasattr(_core_models, "__all__"):
                __all__ = _core_models.__all__
    else:
        __all__: list[str] = []
