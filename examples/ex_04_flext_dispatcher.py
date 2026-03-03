"""FlextDispatcher — exercises ALL public API methods with golden file validation."""

from __future__ import annotations

import sys
from pathlib import Path

from flext_core import FlextDispatcher, r
from pydantic import BaseModel

# --- Golden file checker infrastructure ---
_RESULTS: list[str] = []


def _check(label: str, value: object) -> None:
    _RESULTS.append(f"{label}: {_ser(value)}")


def _section(name: str) -> None:
    if _RESULTS:
        _RESULTS.append("")
    _RESULTS.append(f"[{name}]")


def _ser(v: object) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, str):
        return repr(v)
    if isinstance(v, list):
        return "[" + ", ".join(_ser(x) for x in v) + "]"
    if isinstance(v, dict):
        pairs = ", ".join(
            f"{_ser(k)}: {_ser(val)}"
            for k, val in sorted(v.items(), key=lambda kv: str(kv[0]))
        )
        return "{" + pairs + "}"
    if isinstance(v, type):
        return v.__name__
    return type(v).__name__


def _verify() -> None:
    actual = "\n".join(_RESULTS).strip() + "\n"
    me = Path(__file__)
    expected_path = me.with_suffix(".expected")
    n = sum(1 for line in _RESULTS if ": " in line and not line.startswith("["))
    if expected_path.exists():
        expected = expected_path.read_text(encoding="utf-8")
        if actual == expected:
            sys.stdout.write(f"PASS: {me.stem} ({n} checks)\n")
        else:
            actual_path = me.with_suffix(".actual")
            actual_path.write_text(actual, encoding="utf-8")
            sys.stdout.write(
                f"FAIL: {me.stem} — diff {expected_path.name} {actual_path.name}\n"
            )
            sys.exit(1)
    else:
        expected_path.write_text(actual, encoding="utf-8")
        sys.stdout.write(f"GENERATED: {expected_path.name} ({n} checks)\n")


# --- Message models (Pydantic v2) ---


class RoutableMessage(BaseModel):
    command_type: str = ""
    query_type: str = ""
    event_type: str = ""


class CreateUser(RoutableMessage):
    command_type: str = "create_user"
    username: str


class GetUser(RoutableMessage):
    query_type: str = "get_user"
    username: str


class DeleteUser(RoutableMessage):
    command_type: str = "delete_user"
    username: str


class FailingDelete(RoutableMessage):
    command_type: str = "failing_delete"
    username: str


class AutoCommand(RoutableMessage):
    command_type: str = "auto_command"
    payload: str


class Ping(RoutableMessage):
    command_type: str = "ping"
    value: str


class UnknownQuery(RoutableMessage):
    query_type: str = "unknown_query"
    payload: str


class UserCreated(RoutableMessage):
    event_type: str = "user_created"
    username: str


class NoSubscriberEvent(RoutableMessage):
    event_type: str = "no_subscribers"
    marker: str


# --- Handlers (all protocol variants) ---


class CreateUserHandler:
    """HandleProtocol — uses .handle() method."""

    message_type = "create_user"

    def handle(self, message: object) -> str:
        if isinstance(message, CreateUser):
            return f"created:{message.username}"
        return "created:"


class GetUserDispatcher:
    """DispatchMessageProtocol — uses .dispatch_message() method."""

    message_type = "get_user"

    def dispatch_message(self, message: object) -> dict[str, str]:
        if isinstance(message, GetUser):
            return {"username": message.username, "state": "active"}
        return {"username": "", "state": "active"}


class DeleteExecutor:
    """ExecuteProtocol — uses .execute() method."""

    message_type = "delete_user"

    def execute(self, message: object) -> str:
        if isinstance(message, DeleteUser):
            return f"deleted:{message.username}"
        return "deleted:"


class FailingDeleteCallable:
    """Callable handler returning FlextResult failure."""

    message_type = "failing_delete"

    def __call__(self, message: object) -> r[str]:
        if isinstance(message, FailingDelete):
            return r.fail(f"deletion blocked for {message.username}")
        return r.fail("deletion blocked")


class PingCallable:
    """Callable handler returning bare value."""

    message_type = "ping"

    def __call__(self, message: object) -> str:
        if isinstance(message, Ping):
            return f"pong:{message.value}"
        return "pong:"


class AutoHandler:
    """Auto-discovery handler — uses .can_handle() method."""

    def can_handle(self, message: object) -> bool:
        if isinstance(message, type):
            return issubclass(message, AutoCommand)
        return isinstance(message, AutoCommand)

    def handle(self, message: object) -> str:
        if isinstance(message, AutoCommand):
            return f"auto:{message.payload}"
        return "auto:"


class UserCreatedSubscriber:
    """Event subscriber via HandleProtocol."""

    event_type = "user_created"

    def __init__(self) -> None:
        super().__init__()
        self.events: list[str] = []

    def handle(self, message: object) -> bool:
        if isinstance(message, UserCreated):
            self.events.append(f"user:{message.username}")
        return True


class AuditSubscriber:
    """Event subscriber via DispatchMessageProtocol."""

    event_type = "user_created"

    def __init__(self) -> None:
        super().__init__()
        self.events: list[str] = []

    def dispatch_message(self, message: object) -> bool:
        if isinstance(message, UserCreated):
            self.events.append(f"audit:{message.username}")
        return True


def invalid_handler(message: object) -> str:
    """Plain function without route attributes — should fail registration."""
    if isinstance(message, RoutableMessage):
        return f"invalid:{message.command_type}"
    return "invalid:"


# --- Demos ---


def demo_register_and_dispatch() -> None:
    _section("register_and_dispatch")

    dispatcher = FlextDispatcher()

    reg_handle = dispatcher.register_handler(CreateUserHandler())
    _check("register(HandleProtocol).is_success", reg_handle.is_success)

    reg_dispatch_msg = dispatcher.register_handler(GetUserDispatcher())
    _check("register(DispatchMessageProtocol).is_success", reg_dispatch_msg.is_success)

    reg_execute = dispatcher.register_handler(DeleteExecutor())
    _check("register(ExecuteProtocol).is_success", reg_execute.is_success)

    reg_callable = dispatcher.register_handler(PingCallable())
    _check("register(callable).is_success", reg_callable.is_success)

    create_r = dispatcher.dispatch(CreateUser(username="alice"))
    _check("dispatch(command).is_success", create_r.is_success)
    _check("dispatch(command).value", create_r.value)

    get_r = dispatcher.dispatch(GetUser(username="alice"))
    _check("dispatch(query).is_success", get_r.is_success)
    _check("dispatch(query).value", get_r.value)

    ping_r = dispatcher.dispatch(Ping(value="x"))
    _check("dispatch(callable).is_success", ping_r.is_success)
    _check("dispatch(callable).value", ping_r.value)

    delete_r = dispatcher.dispatch(DeleteUser(username="alice"))
    _check("dispatch(execute).is_success", delete_r.is_success)
    _check("dispatch(execute).value", delete_r.value)


def demo_auto_discovery() -> None:
    _section("auto_discovery")

    dispatcher = FlextDispatcher()

    reg_auto = dispatcher.register_handler(AutoHandler())
    _check("register(can_handle).is_success", reg_auto.is_success)

    auto_r = dispatcher.dispatch(AutoCommand(payload="fallback"))
    _check("dispatch(auto_discovery).is_success", auto_r.is_success)
    _check("dispatch(auto_discovery).value", auto_r.value)


def demo_error_cases() -> None:
    _section("error_cases")

    dispatcher = FlextDispatcher()

    reg_invalid = dispatcher.register_handler(invalid_handler)
    _check("register(no_route_attrs).is_failure", reg_invalid.is_failure)

    no_handler_r = dispatcher.dispatch(UnknownQuery(payload="none"))
    _check("dispatch(no_handler).is_failure", no_handler_r.is_failure)

    reg_fail_handler = dispatcher.register_handler(FailingDeleteCallable())
    _check("register(failing_callable).is_success", reg_fail_handler.is_success)
    failing_r = dispatcher.dispatch(FailingDelete(username="alice"))
    _check("dispatch(handler_returns_fail).is_failure", failing_r.is_failure)


def demo_event_publishing() -> None:
    _section("event_publishing")

    dispatcher = FlextDispatcher()
    subscriber = UserCreatedSubscriber()
    audit_subscriber = AuditSubscriber()

    reg_user = dispatcher.register_handler(subscriber, is_event=True)
    _check("register(event_subscriber).is_success", reg_user.is_success)

    reg_audit = dispatcher.register_handler(audit_subscriber, is_event=True)
    _check("register(audit_subscriber).is_success", reg_audit.is_success)

    pub_one = dispatcher.publish(UserCreated(username="alice"))
    _check("publish(single).is_success", pub_one.is_success)

    pub_many = dispatcher.publish([
        UserCreated(username="bruno"),
        UserCreated(username="carla"),
    ])
    _check("publish(list).is_success", pub_many.is_success)

    _check("subscriber.events", subscriber.events)
    _check("audit_subscriber.events", audit_subscriber.events)

    pub_none = dispatcher.publish(NoSubscriberEvent(marker="ok"))
    _check("publish(no_subscribers).is_success", pub_none.is_success)
    _check("publish(no_subscribers).value", pub_none.value)


def main() -> None:
    demo_register_and_dispatch()
    demo_auto_discovery()
    demo_error_cases()
    demo_event_publishing()
    _verify()


if __name__ == "__main__":
    main()
