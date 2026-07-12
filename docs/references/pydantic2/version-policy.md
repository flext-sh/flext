# Version Policy (Pydantic reference)

This page tracks the versioning stance of the vendored Pydantic v2
documentation reference under `docs/references/pydantic2/`.

- **Upstream policy**: Pydantic follows semantic versioning; the canonical
  statement is the [Pydantic version policy](https://docs.pydantic.dev/latest/version-policy/).
- **This tree** is a reference mirror for offline consultation, excluded from
  the published site (`tool.flext.docs.exclude_docs`). It is refreshed as a
  whole when the workspace Pydantic dependency moves, not edited piecemeal.
- The Pydantic version pinned for the workspace is declared in the root
  dependency set; `flext-core` owns the runtime dependency and consumers
  inherit it.

For the FLEXT workspace's own version policy, see
[docs/version-policy.md](../../version-policy.md).
