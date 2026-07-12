# Pydantic Types

Pydantic v2 ships a rich set of constrained and domain types beyond the
standard library: `Strict*` variants, constrained numerics
(`PositiveInt`, `NegativeFloat`, …), `SecretStr`/`SecretBytes`,
`EmailStr` (with the `email` extra), `AnyUrl` and URL variants,
`PaymentCardNumber`, `Json`, `Base64Bytes`, and the `Annotated` constraint
machinery (`Field`, `StringConstraints`, `Interval`, …).

The full type inventory with semantics and examples lives upstream:

- [Pydantic types](https://docs.pydantic.dev/latest/api/types/)

For FLEXT-specific typing discipline (no `Any`/`object`, `t.*` aliases for
composites, models as the only data contract), see
[docs/api/types.md](../../../api/types.md).
