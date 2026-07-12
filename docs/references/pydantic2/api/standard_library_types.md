# Standard Library Types

Pydantic v2 validates standard library types out of the box — scalars
(`str`, `int`, `float`, `bool`, `bytes`), collections (`list`, `dict`,
`tuple`, `set`, `frozenset`), `datetime` types, `Enum`, `Path`, `UUID`,
`Decimal`, `re.Pattern`, and generic forms (`typing.Optional`, unions,
`Literal`, `Annotated`).

The authoritative table of supported standard library types and their
validation semantics is maintained upstream:

- [Pydantic supported types](https://docs.pydantic.dev/latest/api/standard_library_types/)

FLEXT note: for owned data contracts the workspace standard is Pydantic
models over the `m` facade; bare `dict`/`TypedDict` payloads are forbidden
even though Pydantic can validate them.
