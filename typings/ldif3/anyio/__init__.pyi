from collections.abc import Callable
from typing import TypeVar, TypeVarTuple, Unpack

from .abc import CapacityLimiter

T_Retval = TypeVar("T_Retval")
PosArgsT = TypeVarTuple("PosArgsT")

async def run_sync(
    func: Callable[[Unpack[PosArgsT]], T_Retval],
    *args: *PosArgsT,
    abandon_on_cancel: bool = ...,
    cancellable: bool | None = ...,
    limiter: CapacityLimiter | None = ...,
) -> T_Retval: ...
def current_default_thread_limiter() -> CapacityLimiter: ...
