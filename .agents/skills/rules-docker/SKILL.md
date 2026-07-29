---
name: rules-docker
description: 'Rules for Docker assets in `docker/`, including compose files and image folders. Use when editing container configs, service wiring, or docker validation scripts.'
license: MIT
metadata:
  version: 1.0.0
---
# Rules Docker

## Rules

- Keep compose service names and network references consistent across related files.
- Do not leave zero-byte placeholder compose files for active environments.
- Keep environment-specific compose files explicit (`flext`, `oracle-db`, `openldap`, etc.).
- Validate docker changes with repository scripts when available.

## Instructions

- Anchor changes to exact compose file(s) under `docker/`.
- Preserve existing naming conventions for service blocks and compose filenames.
- When adding a new compose variant, document it in `docker/README.md`.

## Workflow

1. Select target compose file(s).
2. Apply minimal service/network/volume changes.
3. Check sibling compose files for consistency.

## Verification

Make gates:

- `make val VALIDATE_SCOPE=workspace` — verify script references in docker configs

File checks:

- `ls -la docker`
- `rg -n "services:|networks:|volumes:" docker/docker-compose*.yml`
- `rg -n "TODO|FIXME" docker || true`
- `bash docker/validate_docker_standardization.sh || true`
