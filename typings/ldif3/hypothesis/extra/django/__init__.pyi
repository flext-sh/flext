from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypeVar

from django import forms as df
from django.conf import settings
from django.db import models as dm
from hypothesis import strategies as st

type AnyField = dm.Field | df.Field
F = TypeVar("F", bound=AnyField)

def numeric_bounds_from_validators(
    field, min_value=..., max_value=...
):  # -> tuple[float, float]:
    ...
def integers_for_field(min_value, max_value):  # -> Callable[..., SearchStrategy[int]]:
    ...
@lru_cache
def timezones():  # -> SearchStrategy[ZoneInfo] | SearchStrategy[tzinfo]:
    ...

type _FieldLookUpType = dict[
    type[AnyField], st.SearchStrategy | Callable[[Any], st.SearchStrategy]
]
_global_field_lookup: _FieldLookUpType = ...
_ipv6_strings = ...

def register_for(field_type):  # -> Callable[..., Any]:
    ...
def using_sqlite():  # -> Any | None:
    ...
def length_bounds_from_validators(field):  # -> tuple[int, Any]:
    ...

if "django.contrib.auth" in settings.INSTALLED_APPS: ...

def register_field_strategy(
    field_type: type[AnyField], strategy: st.SearchStrategy
) -> None: ...
def from_field[F: AnyField](field: F) -> st.SearchStrategy[F | None]: ...
