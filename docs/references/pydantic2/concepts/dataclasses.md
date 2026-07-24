> **API Documentation:** [`@pydantic.dataclasses.dataclass`][pydantic.dataclasses.dataclass]

If you don't want to use Pydantic's [`BaseModel`][pydantic.BaseModel] you can instead get the same data validation
on standard dataclasses.

```python
from datetime import datetime
from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str = "John Doe"
    signup_ts: Optional[datetime] = None


user = User(id="42", signup_ts="2032-06-21T12:00")
u.Cli.print(user)
"""
User(id=42, name='John Doe', signup_ts=datetime.datetime(2032, 6, 21, 12, 0))
"""
```

> **Note:** Keep in mind that Pydantic dataclasses are **not** a replacement for
> [Pydantic models](../concepts/models.md).
> They provide a similar functionality to stdlib dataclasses with the addition of Pydantic validation.
>
> There are cases where subclassing using Pydantic models is the better choice.
>
> For more information and discussion see
> [pydantic/pydantic#710](https://github.com/pydantic/pydantic/issues/710).

Similarities between Pydantic dataclasses and models include support for:

- [Configuration](#dataclass-settings) support
- [Nested](./models.md#nested-models) classes
- [Generics](./models.md#generic-models)

Some differences between Pydantic dataclasses and models include:

- [validators](#validators-and-initialization-hooks)
- The behavior with the [`extra`][pydantic.ConfigDict.extra] configuration value

Similarly to Pydantic models, arguments used to instantiate the dataclass are [copied](./models.md#attribute-copies).

To make use of the [various methods](./models.md#model-methods-and-properties) to validate, dump and generate a JSON
Schema,
you can wrap the dataclass with a [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] and make use of its methods.

You can use both the Pydantic's [`u.Field()`][pydantic.u.Field] and the stdlib's [`field()`][dataclasses.field]
functions:

```python
import dataclasses
from typing import Optional

from pydantic import u.Field
from pydantic.dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str = "John Doe"
    friends: t.SequenceOf[int] = dataclasses.field(default_factory=lambda: [0])
    age: Optional[int] = dataclasses.field(
        default=None,
        metadata={"title": "The age of the user", "description": "do not lie!"},
    )
    height: Optional[int] = u.Field(default=None, title="The height in cm", ge=50, le=300)


user = User(id="42", height="250")
u.Cli.print(user)
# > User(id=42, name='John Doe', friends=[0], age=None, height=250)
```

The Pydantic [`@dataclass`][pydantic.dataclasses.dataclass] decorator accepts the same arguments as the standard
decorator,
with the addition of a `settings` parameter.

## Dataclass settings

If you want to modify the configuration like you would with a [`BaseModel`][pydantic.BaseModel], you have two options:

- Use the `settings` argument of the decorator.
- Define the configuration with the `__pydantic_config__` attribute.

```python
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


# Option 1 -- using the decorator argument:
@dataclass(settings=ConfigDict(validate_assignment=True))
class MyDataclass1:
    a: int


# Option 2 -- using an attribute:
@dataclass
class MyDataclass2:
    a: int

    __pydantic_config__ = ConfigDict(validate_assignment=True)
```

You can read more about `validate_assignment` in the API reference.

> **Note:** While Pydantic dataclasses support the [`extra`][pydantic.config.ConfigDict.extra]
> configuration value, some default behavior of stdlib dataclasses may prevail.
> For example, any extra fields present on a Pydantic dataclass with
> [`extra`][pydantic.config.ConfigDict.extra] set to `'allow'` are omitted in the dataclass' string representation.
> There is also no way to provide validation [using the `__pydantic_extra__` attribute](./models.md#extra-data).

## Rebuilding dataclass schema

The [`rebuild_dataclass()`][pydantic.dataclasses.rebuild_dataclass] function can be used to rebuild the core schema of
the dataclass.
See the [rebuilding model schema](./models.md#rebuilding-model-schema) section for more details.

## Stdlib dataclasses and Pydantic dataclasses

### Inherit from stdlib dataclasses

Stdlib dataclasses (nested or not) can also be inherited and Pydantic will automatically validate
all the inherited fields.

```python
import dataclasses

import pydantic


@dataclasses.dataclass
class Z:
    z: int


@dataclasses.dataclass
class Y(Z):
    y: int = 0


@pydantic.dataclasses.dataclass
class X(Y):
    x: int = 0


foo = X(x=b"1", y="2", z="3")
u.Cli.print(foo)
# > X(z=3, y=2, x=1)

try:
    X(z="pika")
except pydantic.ValidationError as e:
    u.Cli.print(e)
    """
    1 validation error for X
    z
      Input should be a valid integer, unable to parse string as an integer
      [type=int_parsing, input_value='pika', input_type=str]
    """
```

The decorator can also be applied directly on a stdlib dataclass, in which case a new subclass will be created:

```python
import dataclasses

import pydantic


@dataclasses.dataclass
class A:
    a: int


PydanticA = pydantic.dataclasses.dataclass(A)
u.Cli.print(PydanticA(a="1"))
# > A(a=1)
```

### Usage of stdlib dataclasses with `BaseModel`

When a standard library dataclass is used within a Pydantic model, a Pydantic dataclass or a
[`TypeAdapter`][pydantic.TypeAdapter],
validation will be applied (and the [configuration](#dataclass-settings) stays the same). This means that using a stdlib
or a Pydantic
dataclass as a field annotation is functionally equivalent.

```python
import dataclasses
from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


@dataclasses.dataclass(frozen=True)
class User:
    name: str


class Foo(BaseModel):
    # Required so that pydantic revalidates the model attributes:
    model_config = ConfigDict(revalidate_instances="always")

    user: Optional[User] = None


# nothing is validated as expected:
user = User(name=["not", "a", "string"])
u.Cli.print(user)
# > User(name=['not', 'a', 'string'])


try:
    Foo(user=user)
except ValidationError as e:
    u.Cli.print(e)
    """
    1 validation error for Foo
    user.name
      Input should be a valid string [type=string_type, input_value=['not', 'a', 'string'], input_type=list]
    """

foo = Foo(user=User(name="pika"))
try:
    foo.user.name = "bulbi"
except dataclasses.FrozenInstanceError as e:
    u.Cli.print(e)
    # > cannot assign to field 'name'
```

### Using custom types

As said above, validation is applied on standard library dataclasses. If you make use
of custom types, you will get an error when trying to refer to the dataclass. To circumvent
the issue, you can set the [`arbitrary_types_allowed`][pydantic.ConfigDict.arbitrary_types_allowed]
configuration value on the dataclass:

```python
import dataclasses

from pydantic import BaseModel, ConfigDict
from pydantic.errors import PydanticSchemaGenerationError


class ArbitraryType:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"ArbitraryType(value={self.value!r})"


@dataclasses.dataclass
class DC:
    a: ArbitraryType
    b: str


# valid as it is a stdlib dataclass without validation:
my_dc = DC(a=ArbitraryType(value=3), b="qwe")

try:

    class Model(BaseModel):
        dc: DC
        other: str

    # invalid as dc is now validated with pydantic, and ArbitraryType is not a known type
    Model(dc=my_dc, other="other")

except PydanticSchemaGenerationError as e:
    u.Cli.print(e.message)
    """
    Unable to generate pydantic-core schema for <class '__main__.ArbitraryType'>.
    Set `arbitrary_types_allowed=True` in the model_config to ignore this error or
    implement `__get_pydantic_core_schema__` on your type to fully support it.

    If you got this error by calling handler(<some type>) within
    `__get_pydantic_core_schema__` then you likely need to call
    `handler.generate_schema(<some type>)` since we do not call
    `__get_pydantic_core_schema__` on `<some type>` otherwise to avoid infinite recursion.
    """


# valid as we set arbitrary_types_allowed=True, and that settings pushes down to the nested vanilla dataclass
class Model(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dc: DC
    other: str


m = Model(dc=my_dc, other="other")
u.Cli.print(repr(m))
# > Model(dc=DC(a=ArbitraryType(value=3), b='qwe'), other='other')
```

### Checking if a dataclass is a Pydantic dataclass

Pydantic dataclasses are still considered dataclasses, so using [`dataclasses.is_dataclass()`][dataclasses.is_dataclass]
will return `True`. To check if a type is specifically a Pydantic dataclass you can use the
[`is_pydantic_dataclass()`][pydantic.dataclasses.is_pydantic_dataclass] function.

```python
import dataclasses

import pydantic


@dataclasses.dataclass
class StdLibDataclass:
    id: int


PydanticDataclass = pydantic.dataclasses.dataclass(StdLibDataclass)

u.Cli.print(dataclasses.is_dataclass(StdLibDataclass))
# > True
u.Cli.print(pydantic.dataclasses.is_pydantic_dataclass(StdLibDataclass))
# > False

u.Cli.print(dataclasses.is_dataclass(PydanticDataclass))
# > True
u.Cli.print(pydantic.dataclasses.is_pydantic_dataclass(PydanticDataclass))
# > True
```

## Validators and initialization hooks

Validators also work with Pydantic dataclasses:

```python
from pydantic import u.field_validator
from pydantic.dataclasses import dataclass


@dataclass
class DemoDataclass:
    product_id: str  # should be a five-digit string, may have leading zeros

    @u.field_validator("product_id", mode="before")
    @classmethod
    def convert_int_serial(cls, v):
        if isinstance(v, int):
            v = str(v).zfill(5)
        return v


u.Cli.print(DemoDataclass(product_id="01234"))
# > DemoDataclass(product_id='01234')
u.Cli.print(DemoDataclass(product_id=2468))
# > DemoDataclass(product_id='02468')
```

The dataclass [`__post_init__()`][dataclasses.__post_init__] method is also supported, and will
be called between the calls to _before_ and _after_ model validators.

### Example

```python
from pydantic_core import ArgsKwargs
from typing_extensions import Self

from pydantic import u.model_validator
from pydantic.dataclasses import dataclass


@dataclass
class Birth:
    year: int
    month: int
    day: int


@dataclass
class User:
    birth: Birth

    @u.model_validator(mode="before")
    @classmethod
    def before(cls, values: ArgsKwargs) -> ArgsKwargs:
        u.Cli.print(f"First: {values}")
        """
        First: ArgsKwargs((), {'birth': {'year': 1995, 'month': 3, 'day': 2}})
        """
        return values

    @u.model_validator(mode="after")
    def after(self) -> Self:
        u.Cli.print(f"Third: {self}")
        # > Third: User(birth=Birth(year=1995, month=3, day=2))
        return self

    def __post_init__(self):
        u.Cli.print(f"Second: {self.birth}")
        # > Second: Birth(year=1995, month=3, day=2)


user = User(**{"birth": {"year": 1995, "month": 3, "day": 2}})
```

Unlike Pydantic models, the `values` parameter is of type [`ArgsKwargs`][pydantic_core.ArgsKwargs].
