from collections.abc import Generator, Sequence

from ._hooks import HookImpl

"""
Call loop machinery
"""
type Teardown = Generator[None, object, object]

def run_old_style_hookwrapper(
    hook_impl: HookImpl, hook_name: str, args: Sequence[object]
) -> Teardown: ...
