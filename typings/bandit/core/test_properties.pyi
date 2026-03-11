from __future__ import annotations

import logging
from collections.abc import Callable

LOG: logging.Logger

def checks(*args: str) -> Callable[[Callable[..., object]], Callable[..., object]]: ...
def takes_config(
    *args: object,
) -> Callable[[Callable[..., object]], Callable[..., object]]: ...
def test_id(
    id_val: str,
) -> Callable[[Callable[..., object]], Callable[..., object]]: ...
def accepts_baseline(*args: Callable[..., object]) -> Callable[..., object]: ...
