
# Lazy imports to avoid circular dependencies
# Lazy import to avoid circular dependencies
# Lazy import to avoid circular dependencies
from flx.utils.lazy_import import lazy_import

"""Event system for FLX platform."""

# Lazy imports to avoid circular dependencies
Event = lazy_import('flx.events.event_bus', 'Event')
EventBus = lazy_import('flx.events.event_bus', 'EventBus')
EventHandler = lazy_import('flx.events.event_bus', 'EventHandler')

__all__ = ["Event", "EventBus", "EventHandler"]
