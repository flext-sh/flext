from inspect import Parameter
from typing import Any, Protocol

from pydantic_core import core_schema

"""Logic for V1 validators, e.g. `@validator` and `@root_validator`."""

class V1OnlyValueValidator(Protocol):
    def __call__(self, __value: Any) -> Any: ...

class V1ValidatorWithValues(Protocol):
    def __call__(self, __value: Any, values: dict[str, Any]) -> Any: ...

class V1ValidatorWithValuesKwOnly(Protocol):
    def __call__(self, __value: Any, *, values: dict[str, Any]) -> Any: ...

class V1ValidatorWithKwargs(Protocol):
    def __call__(self, __value: Any, **kwargs: Any) -> Any: ...

class V1ValidatorWithValuesAndKwargs(Protocol):
    def __call__(self, __value: Any, values: dict[str, Any], **kwargs: Any) -> Any: ...

type V1Validator = (
    V1ValidatorWithValues
    | V1ValidatorWithValuesKwOnly
    | V1ValidatorWithKwargs
    | V1ValidatorWithValuesAndKwargs
)

def can_be_keyword(param: Parameter) -> bool: ...
def make_generic_v1_field_validator(
    validator: V1Validator,
) -> core_schema.WithInfoValidatorFunction: ...

type RootValidatorValues = dict[str, Any]
type RootValidatorFieldsTuple = tuple[Any, ...]

class V1RootValidatorFunction(Protocol):
    def __call__(self, __values: RootValidatorValues) -> RootValidatorValues: ...

class V2CoreBeforeRootValidator(Protocol):
    def __call__(
        self, __values: RootValidatorValues, __info: core_schema.ValidationInfo
    ) -> RootValidatorValues: ...

class V2CoreAfterRootValidator(Protocol):
    def __call__(
        self,
        __fields_tuple: RootValidatorFieldsTuple,
        __info: core_schema.ValidationInfo,
    ) -> RootValidatorFieldsTuple: ...

def make_v1_generic_root_validator(
    validator: V1RootValidatorFunction, pre: bool
) -> V2CoreBeforeRootValidator | V2CoreAfterRootValidator: ...
