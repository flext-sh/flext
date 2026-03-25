<!-- TOC START -->

- [Scope](#scope)
- [References](#references)
- [Rules](#rules)
- [Instructions](#instructions)
- [Workflow](#workflow)
- [Examples](#examples)
- [Verification](#verification)
<!-- TOC END -->

---

name: rules-docker
description: Rules for Docker assets in `docker/`, including compose files and image folders. Use when editing container configs, service wiring, or docker validation scripts.

---

# Rules Docker

**Reviewed**: 2026-02-17 | **Scope**: Evidence-backed skill refresh and rule alignment

## Scope

- `docker/docker-compose.*.yml`
- `docker/images/`
- `docker/openldap/`
- `docker/oracle-db/`
- `docker/validate_docker_standardization.sh`

## References

- `docker/README.md`
- `docker/docker-compose.flext.yml`
- `docker/docker-compose.oracle-db.yml`
- `docker/validate_docker_standardization.sh`

## Rules

- Keep compose service names and network references consistent across related files.
- Do not leave zero-byte placeholder compose files for active environments.
- Keep environment-specific compose files explicit (`flext`, `oracle-db`, `openldap`, etc.).
- Validate docker changes with repository scripts when available.

## Instructions

- Anchor changes to exact compose file(s) under `docker/`.
- Preserve existing naming conventions for service blocks and compose filenames.
- When adding a new compose variant, document it in `docker/README.md`.

```bash
ls -la docker
```

## Workflow

1. Select target compose file(s).
2. Apply minimal service/network/volume changes.
3. Check sibling compose files for consistency.
4. Run docker standardization script or equivalent checks.
5. Update docs if new compose targets were introduced.

## Examples

Good:

```yaml
services:
  redis:
    image: redis:7
```

Why good: explicit service declaration in a concrete compose file.

Bad:

```yaml
services:
  cache: {}
```

Why bad: empty service stubs obscure runtime behavior and break reproducibility.

## Verification

Make gates:

- `make validate VALIDATE_SCOPE=workspace` — verify script references in docker configs

File checks:

- `ls -la docker`
- `rg -n "services:|networks:|volumes:" docker/docker-compose*.yml`
- `rg -n "TODO|FIXME" docker || true`
- `bash docker/validate_docker_standardization.sh || true`
