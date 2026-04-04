from collections.abc import Mapping, Sequence

type Primitive = str | int | float | bool | None
type JsonValue = Primitive | Sequence[JsonValue] | Mapping[str, JsonValue]

def packb(o: JsonValue, **kwargs: object) -> bytes: ...
def unpackb(packed: bytes | bytearray, **kwargs: object) -> JsonValue: ...
