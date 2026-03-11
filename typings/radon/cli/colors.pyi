"""Type stubs for radon.cli.colors module."""

"""Module holding constants used to format lines that are printed to the
terminal.
"""

def color_enabled() -> bool: ...

GREEN: str
YELLOW: str
RED: str
MAGENTA: str
CYAN: str
WHITE: str
BRIGHT: str
RESET: str
RANKS_COLORS: dict[str, str]
LETTERS_COLORS: dict[str, str]
MI_RANKS: dict[str, str]
TEMPLATE: str
