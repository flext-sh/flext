

plugin_name_pattern: str
RANKING: list[str]
RANKING_VALUES: dict[str, int]
CRITERIA: list[tuple[str, str]]
CONFIDENCE_DEFAULT: str
FALSE_VALUES: list[object]
log_format_string: str
EXCLUDE: tuple[str, ...]

# Dynamically added via: for rank in RANKING: globals()[rank] = rank
UNDEFINED: str
LOW: str
MEDIUM: str
HIGH: str
