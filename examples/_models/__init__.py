# AUTO-GENERATED BRIDGE FILE
# Re-exports model classes from flext-core/examples/_models

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

# Re-export all model classes from flext-core examples
try:
    from flext_core.examples._models.ex00 import Ex00UserInput, Ex00UserProfile
    from flext_core.examples._models.ex01 import (
        Ex01DemonstrationResult,
        Ex01InvalidPersonPayload,
        Ex01RunDemonstrationCommand,
        Ex01User,
        Ex01ValidPersonPayload,
    )
    from flext_core.examples._models.ex02 import (
        Ex02CacheService,
        Ex02DatabaseService,
        Ex02EmailService,
        Ex02TestConfig,
    )
    from flext_core.examples._models.ex03 import (
        Ex03Email,
        Ex03Money,
        Ex03Order,
        Ex03OrderItem,
        Ex03User,
    )
    from flext_core.examples._models.ex04 import (
        Ex04AutoCommand,
        Ex04CreateUser,
        Ex04DeleteUser,
        Ex04FailingDelete,
        Ex04GetUser,
        Ex04NoSubscriberEvent,
        Ex04Ping,
        Ex04UnknownQuery,
        Ex04UserCreated,
    )
    from flext_core.examples._models.ex05 import (
        Ex05BadProcessor,
        Ex05GoodProcessor,
        Ex05HandlerBad,
        Ex05HandlerLike,
        Ex05StatusEnum,
        Ex05UserModel,
    )
    from flext_core.examples._models.ex07 import (
        Ex07CreateUserCommand,
        Ex07DemoPlugin,
        Ex07GetUserQuery,
        Ex07UserCreatedEvent,
    )
    from flext_core.examples._models.ex08 import Ex08Order, Ex08User
    from flext_core.examples._models.ex10 import (
        Ex10CommandBusStub,
        Ex10ContextPayload,
        Ex10DerivedMessage,
        Ex10Entity,
        Ex10Message,
        Ex10ProcessorBad,
        Ex10ProcessorGood,
        Ex10ProtocolHandler,
        Ex10ServiceStub,
    )
    from flext_core.examples._models.ex11 import (
        Ex11CommandBusStub,
        Ex11EntityStub,
        Ex11HandlerLike,
        Ex11HandlerLikeService,
        Ex11Payload,
        Ex11ProcessorProtocolBad,
        Ex11ProcessorProtocolGood,
    )
    from flext_core.examples._models.ex12 import Ex12CommandA, Ex12CommandB
    from flext_core.examples._models.ex14 import (
        Ex14CreateUserCommand,
        Ex14GetUserQuery,
        Ex14UserDTO,
    )
    from flext_core.examples._models.exconfig import ExConfigAppConfig
    from flext_core.examples._models.shared import SharedHandle, SharedPerson

    __all__ = [
        "Ex00UserInput",
        "Ex00UserProfile",
        "Ex01DemonstrationResult",
        "Ex01InvalidPersonPayload",
        "Ex01RunDemonstrationCommand",
        "Ex01User",
        "Ex01ValidPersonPayload",
        "Ex02CacheService",
        "Ex02DatabaseService",
        "Ex02EmailService",
        "Ex02TestConfig",
        "Ex03Email",
        "Ex03Money",
        "Ex03Order",
        "Ex03OrderItem",
        "Ex03User",
        "Ex04AutoCommand",
        "Ex04CreateUser",
        "Ex04DeleteUser",
        "Ex04FailingDelete",
        "Ex04GetUser",
        "Ex04NoSubscriberEvent",
        "Ex04Ping",
        "Ex04UnknownQuery",
        "Ex04UserCreated",
        "Ex05BadProcessor",
        "Ex05GoodProcessor",
        "Ex05HandlerBad",
        "Ex05HandlerLike",
        "Ex05StatusEnum",
        "Ex05UserModel",
        "Ex07CreateUserCommand",
        "Ex07DemoPlugin",
        "Ex07GetUserQuery",
        "Ex07UserCreatedEvent",
        "Ex08Order",
        "Ex08User",
        "Ex10CommandBusStub",
        "Ex10ContextPayload",
        "Ex10DerivedMessage",
        "Ex10Entity",
        "Ex10Message",
        "Ex10ProcessorBad",
        "Ex10ProcessorGood",
        "Ex10ProtocolHandler",
        "Ex10ServiceStub",
        "Ex11CommandBusStub",
        "Ex11EntityStub",
        "Ex11HandlerLike",
        "Ex11HandlerLikeService",
        "Ex11Payload",
        "Ex11ProcessorProtocolBad",
        "Ex11ProcessorProtocolGood",
        "Ex12CommandA",
        "Ex12CommandB",
        "Ex14CreateUserCommand",
        "Ex14GetUserQuery",
        "Ex14UserDTO",
        "ExConfigAppConfig",
        "SharedHandle",
        "SharedPerson",
    ]
except ImportError:
    # If flext_core is not available, set empty exports
    __all__ = []
