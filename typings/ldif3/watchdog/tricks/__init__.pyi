import signal

from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.utils import platform

""":module: watchdog.tricks
:synopsis: Utility event handlers.
:author: yesudeep@google.com (Yesudeep Mangalapilly)
:author: contact@tiger-222.fr (Mickaël Schoentgen)

Classes
-------
.. autoclass:: Trick
   :members:
   :show-inheritance:

.. autoclass:: LoggerTrick
   :members:
   :show-inheritance:

.. autoclass:: ShellCommandTrick
   :members:
   :show-inheritance:

.. autoclass:: AutoRestartTrick
   :members:
   :show-inheritance:

"""
logger = ...
echo_events = ...

class Trick(PatternMatchingEventHandler):
    @classmethod
    def generate_yaml(cls) -> str: ...

class LoggerTrick(Trick):
    @echo_events
    def on_any_event(self, event: FileSystemEvent) -> None: ...

class ShellCommandTrick(Trick):
    def __init__(
        self,
        shell_command: str,
        *,
        patterns: list[str] | None = ...,
        ignore_patterns: list[str] | None = ...,
        ignore_directories: bool = ...,
        wait_for_process: bool = ...,
        drop_during_process: bool = ...,
    ) -> None: ...
    def on_any_event(self, event: FileSystemEvent) -> None: ...
    def is_process_running(self) -> bool: ...

class AutoRestartTrick(Trick):
    def __init__(
        self,
        command: list[str],
        *,
        patterns: list[str] | None = ...,
        ignore_patterns: list[str] | None = ...,
        ignore_directories: bool = ...,
        stop_signal: signal.Signals | int = ...,
        kill_after: int = ...,
        debounce_interval_seconds: int = ...,
        restart_on_command_exit: bool = ...,
    ) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    @echo_events
    def on_any_event(self, event: FileSystemEvent) -> None: ...

if platform.is_windows():
    def kill_process(pid: int, stop_signal: int) -> None: ...

else:
    def kill_process(pid: int, stop_signal: int) -> None: ...
