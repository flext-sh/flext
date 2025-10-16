import datetime
from collections.abc import Callable
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from warnings import deprecated

if not TYPE_CHECKING: ...
__all__ = ("custom_pydantic_encoder", "pydantic_encoder", "timedelta_isoformat")

def isoformat(o: datetime.date | datetime.time) -> str: ...
def decimal_encoder(dec_value: Decimal) -> int | float: ...

ENCODERS_BY_TYPE: dict[type[Any], Callable[[Any], Any]] = ...

@deprecated(
    "`pydantic_encoder` is deprecated, use `pydantic_core.to_jsonable_python` instead.",
    category=None,
)
def pydantic_encoder(obj: Any) -> Any: ...
@deprecated(
    "`custom_pydantic_encoder` is deprecated, use `BaseModel.model_dump` instead.",
    category=None,
)
def custom_pydantic_encoder(
    type_encoders: dict[Any, Callable[[type[Any]], Any]], obj: Any
) -> Any: ...
@deprecated("`timedelta_isoformat` is deprecated.", category=None)
def timedelta_isoformat(td: datetime.timedelta) -> str: ...
