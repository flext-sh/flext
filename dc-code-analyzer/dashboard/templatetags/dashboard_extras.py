"""
Custom template filters for the dashboard app.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def multiply(value, arg):
    """Multiply two values."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def percentage(value, total):
    """Calculate percentage."""
    if total == 0:
        return 0
    return round((value / total) * 100, 1)


@register.filter
def severity_color(severity):
    """Get Bootstrap color class for severity level."""
    severity_colors = {
        "CRITICAL": "danger",
        "HIGH": "warning",
        "MEDIUM": "info",
        "LOW": "success",
        "INFO": "secondary",
    }
    return severity_colors.get(severity.upper(), "secondary")


@register.filter
def status_icon(status):
    """Get icon for backend status."""
    status_icons = {
        "success": "✅",
        "failed": "❌",
        "skipped": "⏭️",
        "partial": "⚠️",
    }
    return status_icons.get(status, "❓")


@register.filter
def dict_get(dictionary, key):
    """Get value from dictionary by key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, 0)
    return 0


@register.filter
def severity_badge(severity):
    """Return Bootstrap badge class for severity level."""
    severity_classes = {
        "CRITICAL": "bg-danger",
        "HIGH": "bg-warning",
        "MEDIUM": "bg-info",
        "LOW": "bg-success",
        "INFO": "bg-secondary",
    }
    return severity_classes.get(severity, "bg-secondary")


@register.filter
def status_badge(status):
    """Return Bootstrap badge class for status."""
    status_classes = {
        "success": "bg-success",
        "failed": "bg-danger",
        "skipped": "bg-warning",
        "partial": "bg-info",
        "running": "bg-primary",
        "pending": "bg-secondary",
        "completed": "bg-success",
    }
    return status_classes.get(status, "bg-secondary")


@register.filter
def format_duration(duration):
    """Format duration in a human-readable way."""
    if not duration:
        return "N/A"

    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


@register.filter
def truncate_path(path, max_length=50):
    """Truncate file path for display."""
    if len(path) <= max_length:
        return path

    # Try to keep the filename and some parent directories
    parts = path.split("/")
    if len(parts) > 1:
        filename = parts[-1]
        remaining_length = max_length - len(filename) - 3  # 3 for "..."

        if remaining_length > 0:
            # Build path from the beginning until we run out of space
            truncated_parts = []
            current_length = 0

            for part in parts[:-1]:
                if current_length + len(part) + 1 <= remaining_length:
                    truncated_parts.append(part)
                    current_length += len(part) + 1
                else:
                    break

            if truncated_parts:
                return "/".join(truncated_parts) + "/.../" + filename

    # Fallback: just truncate from the end
    return path[: max_length - 3] + "..."


@register.filter
def issue_icon(category):
    """Return FontAwesome icon for issue category."""
    icons = {
        "security": "fas fa-shield-alt",
        "quality": "fas fa-code",
        "complexity": "fas fa-flx_project-diagram",
        "dead_code": "fas fa-trash",
        "style": "fas fa-paint-brush",
        "documentation": "fas fa-book",
        "performance": "fas fa-tachometer-alt",
        "maintainability": "fas fa-wrench",
        "best_practices": "fas fa-star",
    }
    return icons.get(category, "fas fa-exclamation-triangle")


@register.simple_tag
def progress_bar(value, total, css_class="bg-primary"):
    """Generate a Bootstrap progress bar."""
    percentage = 0 if total == 0 else value / total * 100

    html = f"""
    <div class="progress" style="height: 20px;">
        <div class="progress-bar {css_class}" role="progressbar"
             style="width: {percentage}%"
             aria-valuenow="{value}"
             aria-valuemin="0"
             aria-valuemax="{total}">
            {value}/{total}
        </div>
    </div>
    """
    return mark_safe(html)
