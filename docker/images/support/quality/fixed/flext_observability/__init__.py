# Mock flext_observability for enterprise compatibility
import os
import sys


def flext_create_metric(name: str, value: float, tags: dict[str, object] = None):
    if not os.environ.get("FLEXT_OBSERVABILITY_QUIET"):
        print(f"📊 Metric: {name}={value} {tags or {}}")


def flext_create_trace(trace_id: str, operation: str, config: dict[str, object] = None):
    if not os.environ.get("FLEXT_OBSERVABILITY_QUIET"):
        print(f"🔍 Trace: {trace_id} {operation} {config or {}}")


def flext_create_log_entry(
    message: str, level: str = "info", context: dict[str, object] = None
):
    if not os.environ.get("FLEXT_OBSERVABILITY_QUIET"):
        print(f"📝 Log [{level}]: {message} {context or {}}")
