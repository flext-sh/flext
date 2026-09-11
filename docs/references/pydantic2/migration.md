# Migration

This section of the reference tree covers migrating between Pydantic
versions. The complete migration guides are maintained upstream:

- [Pydantic v1 → v2 migration guide](https://docs.pydantic.dev/latest/migration/)
- [Pydantic version policy](https://docs.pydantic.dev/latest/version-policy/)

Key points already applied across the FLEXT workspace:

- All packages are on **Pydantic v2** (`BaseModel`, `ConfigDict`,
  `model_validate`/`model_dump`); no v1 API surface remains.
- Owned payloads are validated at the boundary with `model_validate(...)`
  and emitted with `model_dump(...)` — the 2-way contract (see
  [docs/standards/documentation.md](../../standards/documentation.md)).
- Deprecated v2 shims (`dict()`, `parse_obj()`, class-based `Config`) are
  treated as defects and removed at the source when found.
