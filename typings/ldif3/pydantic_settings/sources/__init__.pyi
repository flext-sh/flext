from collections.abc import Mapping

"""Utility functions for pydantic-settings sources."""

def parse_env_vars(
    env_vars: Mapping[str, str | None],
    case_sensitive: bool = ...,
    ignore_empty: bool = ...,
    parse_none_str: str | None = ...,
) -> Mapping[str, str | None]: ...

__all__ = [
    "_annotation_contains_types",
    "_annotation_enum_name_to_val",
    "_annotation_enum_val_to_name",
    "_annotation_is_complex",
    "_annotation_is_complex_inner",
    "_get_alias_names",
    "_get_env_var_key",
    "_get_model_fields",
    "_is_function",
    "_parse_env_none_str",
    "_strip_annotated",
    "_union_is_complex",
    "parse_env_vars",
]
