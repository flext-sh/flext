# Mock flext_observability
def flext_create_metric(name, value, tags=None):
    print(f"📊 Metric: {name}={value}")


def flext_create_trace(trace_id, operation, config=None):
    print(f"🔍 Trace: {trace_id} {operation}")


def flext_create_log_entry(message, level="info", context=None):
    print(f"📝 Log [{level}]: {message}")
