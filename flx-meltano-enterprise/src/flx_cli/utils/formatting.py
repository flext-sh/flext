"""
Formatting utilities for CLI output.
"""

from datetime import datetime
from typing import Optional


def format_datetime(dt: Optional[datetime]) -> str:
    """Format datetime for display."""
    if not dt:
        return "Never"

    now = datetime.now(dt.tzinfo)
    delta = now - dt

    if delta.days > 7:
        return dt.strftime("%Y-%m-%d %H:%M")
    elif delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds > 3600:
        hours = delta.seconds // 3600
        return f"{hours}h ago"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"{minutes}m ago"
    else:
        return "Just now"


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds for display."""
    if seconds is None:
        return "-"

    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
