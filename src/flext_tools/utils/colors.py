"""Sistema de cores para output no terminal."""


class Colors:
    """Cores ANSI para terminal."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    ORANGE = "\033[38;5;208m"
    GRAY = "\033[90m"


def print_colored(message: str, color: str = "") -> None:
    """Imprime mensagem colorida no terminal."""
    if color:
        pass
    else:
        pass
