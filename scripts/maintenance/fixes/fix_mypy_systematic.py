#!/usr/bin/env python3
"""Systematic fixes for remaining mypy errors."""

import re
from pathlib import Path


def fix_adapter_meta_calls() -> None:
    """Fix FlxAdapterMeta constructor calls missing arguments."""
    files_to_fix = [
        "flx/src/flx/adapters/query.py",
        "flx/src/flx/adapters/operation.py",
        "flx/src/flx/adapters/management.py",
        "flx/src/flx/adapters/interface.py",
        "flx/src/flx/adapters/http.py",
        "flx/src/flx/adapters/database.py",
        "flx/src/flx/adapters/config.py",
        "flx/src/flx/adapters/analytics.py",
    ]

    for filepath in files_to_fix:
        path = Path(filepath)
        if not path.exists():
            continue

        content = path.read_text()

        # Fix FlxAdapterMeta calls - add missing version and dependencies
        content = re.sub(
            r'FlxAdapterMeta\(\s*name="([^"]+)",\s*adapter_type=([^,]+),\s*description="([^"]+)",\s*capabilities=(\[[^\]]+\])\s*\)',
            r'FlxAdapterMeta(name="\1", adapter_type=\2, description="\3", capabilities=\4, version="1.0.0", dependencies=[])',
            content,
        )

        path.write_text(content)
        print(f"Fixed FlxAdapterMeta calls in {filepath}")


def fix_adapter_result_calls() -> None:
    """Fix FlxAdapterResult constructor calls missing arguments."""
    files_to_fix = Path("flx/src").rglob("*.py")

    for path in files_to_fix:
        content = path.read_text()

        # Pattern 1: FlxAdapterResult(success=True, data={...})
        pattern1 = r"FlxAdapterResult\(success=(True|False), data=({[^}]+}|\[[^\]]+\]|[^,)]+)\)"
        replacement1 = r'FlxAdapterResult(success=\1, data=\2, message="", error=None, metadata={})'

        if re.search(pattern1, content):
            content = re.sub(pattern1, replacement1, content)
            path.write_text(content)
            print(f"Fixed FlxAdapterResult calls in {path}")


def add_missing_classes() -> None:
    """Add missing class definitions based on analysis."""
    missing_classes = {
        "flx/src/flx/infra/logging/resilience.py": [
            (
                "ResilienceState",
                """
class ResilienceState(StrEnum):
    \"\"\"States for resilience tracking.\"\"\"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CIRCUIT_OPEN = "circuit_open"
    RECOVERING = "recovering"
""",
            ),
            (
                "ResilienceMetrics",
                """
@dataclass
class ResilienceMetrics:
    \"\"\"Metrics for resilience tracking.\"\"\"
    total_requests: int = 0
    failed_requests: int = 0
    success_rate: float = 1.0
    avg_response_time: float = 0.0
    circuit_state: str = "closed"
""",
            ),
            (
                "FailureEvent",
                """
@dataclass
class FailureEvent:
    \"\"\"Event representing a failure.\"\"\"
    timestamp: float
    error_type: str
    error_message: str
    component: str = ""
""",
            ),
        ],
        "flx/src/flx/infra/ratelimit/adaptive.py": [
            (
                "RateLimitDecision",
                """
@dataclass
class RateLimitDecision:
    \"\"\"Decision from rate limiter.\"\"\"
    allowed: bool
    wait_time: float = 0.0
    reason: str = ""
    remaining_quota: int = 0
""",
            ),
            (
                "UserProfile",
                """
@dataclass
class UserProfile:
    \"\"\"User profile for rate limiting.\"\"\"
    user_id: str
    tier: str = "standard"
    quota_multiplier: float = 1.0
""",
            ),
            (
                "EndpointStats",
                """
@dataclass
class EndpointStats:
    \"\"\"Statistics for an endpoint.\"\"\"
    endpoint: str
    request_count: int = 0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
""",
            ),
        ],
        "flx/src/flx/infra/mock_data/adapters.py": [
            (
                "AdapterModel",
                """
class AdapterModel(FlxStrictModel):
    \"\"\"Model for adapter data.\"\"\"
    name: str
    adapter_type: str
    config: Dict[str, Any] = {}
""",
            ),
            (
                "AdapterCatalogEntry",
                """
@dataclass
class AdapterCatalogEntry:
    \"\"\"Entry in adapter catalog.\"\"\"
    adapter_id: str
    adapter_class: type
    metadata: Dict[str, Any] = field(default_factory=dict)
""",
            ),
        ],
        "flx/src/flx/infra/caching/adaptive.py": [
            (
                "CachePattern",
                """
class CachePattern(StrEnum):
    \"\"\"Cache access patterns.\"\"\"
    READ_HEAVY = "read_heavy"
    WRITE_HEAVY = "write_heavy"
    BALANCED = "balanced"
    TEMPORAL = "temporal"
""",
            ),
        ],
        "flx/src/flx/infra/observability/metrics.py": [
            (
                "MetricType",
                """
class MetricType(StrEnum):
    \"\"\"Types of metrics.\"\"\"
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
""",
            ),
            (
                "SystemMetric",
                """
@dataclass
class SystemMetric:
    \"\"\"System metric data.\"\"\"
    name: str
    value: float
    metric_type: str
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
""",
            ),
        ],
        "flx/src/flx/plugins/base.py": [
            (
                "PluginState",
                """
class PluginState(StrEnum):
    \"\"\"Plugin states.\"\"\"
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
""",
            ),
        ],
    }

    for filepath, classes in missing_classes.items():
        path = Path(filepath)
        if not path.exists():
            continue

        content = path.read_text()

        # Check which imports are needed
        needs_dataclass = any(
            "@dataclass" in class_def for _,
            class_def in classes)
        needs_strenum = any("StrEnum" in class_def for _, class_def in classes)
        needs_dict_any = any(
            "Dict[str, Any]" in class_def for _,
            class_def in classes)
        needs_field = any("field(" in class_def for _, class_def in classes)

        # Add imports if needed
        import_lines: list = []
        if needs_dataclass and "from dataclasses import dataclass" not in content:
            if "from dataclasses import" in content:
                content = content.replace(
                    "from dataclasses import",
                    "from dataclasses import dataclass,")
                import_lines.append("from dataclasses import dataclass")

        if needs_field and "field" not in content:
            if "from dataclasses import" in content:
                content = content.replace(
                    "from dataclasses import", "from dataclasses import field,"
                )
                import_lines.append("from dataclasses import field")

        if needs_strenum and "from enum import StrEnum" not in content:
            if "from enum import" in content:
                content = content.replace(
                    "from enum import", "from enum import StrEnum,"
                )
                import_lines.append("from enum import StrEnum")

        if needs_dict_any and "from typing import Dict," in content and "Dict" not in content:
            content = content.replace(
                "from typing import Dict,",
                "from typing import Dict, Dict,")

        # Add imports after __future__ or at the beginning
        if import_lines:
            if "from __future__ import" in content:
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if line.startswith("from __future__ import"):
                        lines.insert(i + 1, "\n".join(import_lines))
                        break
                content = "\n".join(lines)
                content = "\n".join(import_lines) + "\n\n" + content

        # Add missing classes
        for class_name, class_def in classes:
            if f"class {class_name}" not in content:
                # Add before the first function or at the end
                if "\ndef " in content:
                    content = content.replace(
                        "\ndef ", f"\n{class_def.strip()}\n\n\ndef ", 1
                    )
                    content += f"\n\n{class_def.strip()}\n"
                print(f"Added {class_name} to {filepath}")

        path.write_text(content)


def fix_missing_functions() -> None:
    """Add missing function definitions."""
    # Add async_wrapper and sync_wrapper to context.py
    context_file = Path("flx/src/flx/infra/logging/context.py")
    if context_file.exists():
        content = context_file.read_text()

        if "def async_wrapper" not in content:
            wrapper_code = '''
def async_wrapper(func) -> Any:
    """Wrapper for async functions."""
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper

def sync_wrapper(func) -> Any:
    """Wrapper for sync functions."""
    def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)
    return wrapper
'''
            # Add after imports
            if "from typing import Dict," in content:
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if line.startswith("from typing import Dict,"):
                        # Find the next empty line
                        for j in range(i + 1, len(lines)):
                            if not lines[j].strip():
                                lines.insert(j + 1, wrapper_code)
                                break
                        break
                content = "\n".join(lines)
                context_file.write_text(content)
                print("Added wrapper functions to context.py")


def fix_imports() -> None:
    """Fix missing imports."""
    # Fix PluginFactory import
    factory_file = Path("flx/src/flx/plugins/factory.py")
    if factory_file.exists():
        content = factory_file.read_text()
        if "class PluginFactory" not in content:
            # It might be imported, let's define it
            factory_def = '''
class PluginFactory:
    """Factory for creating plugin instances."""

    def __init__(self) -> None:
        self._registry = {}

    def register(self, name: str, plugin_class: type) -> None:
        """Register a plugin class."""
        self._registry[name] = plugin_class

    def create(self, name: str, *args, **kwargs) -> Any:
        """Create a plugin instance."""
        if name not in self._registry:
            raise ValueError(f"Plugin {name} not registered")
        return self._registry[name](*args, **kwargs)
'''
            content += f"\n\n{factory_def}\n"
            factory_file.write_text(content)
            print("Added PluginFactory to factory.py")


def main() -> None:
    """Run all fixes."""
    print("Applying systematic fixes...")

    print("\n1. Fixing FlxAdapterMeta calls...")
    fix_adapter_meta_calls()

    print("\n2. Fixing FlxAdapterResult calls...")
    fix_adapter_result_calls()

    print("\n3. Adding missing classes...")
    add_missing_classes()

    print("\n4. Adding missing functions...")
    fix_missing_functions()

    print("\n5. Fixing imports...")
    fix_imports()

    print("\nDone! Run mypy again to check progress.")


if __name__ == "__main__":
    main()
