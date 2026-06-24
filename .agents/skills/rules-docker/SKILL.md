---
name: rules-docker
description: 'Use this skill to rules for Docker assets in `docker/`, including compose
  files and image folders. Use when editing container configs, service wiring, or
  docker validation scripts. DO NOT USE FOR: questions unrelated to rules-docker creating
  projects or architecture from scratch'
license: MIT
metadata:
  version: 1.0.0
---
# Rules Docker

**UTILITY SKILL**

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

## Examples

Good:

Why good: explicit service declaration in a concrete compose file.

Bad:

Why bad: empty service stubs obscure runtime behavior and break reproducibility.

## Verification

Make gates:

- `make val VALIDATE_SCOPE=workspace` — verify script references in docker configs

File checks:

- `ls -la docker`
- `rg -n "services:|networks:|volumes:" docker/docker-compose*.yml`
- `rg -n "TODO|FIXME" docker || true`
- `bash docker/validate_docker_standardization.sh || true`

## USE FOR

- Requests about rules docker.
- Workflows described in this skill.
- Operator tasks within this scope.

## DO NOT USE FOR

- questions unrelated to rules-docker.
- creating projects or architecture from scratch.

## Critical rules

- Prefer canonical sources.
- Require evidence before claiming success.

## Example

**Input:** a request.
**Output:** a concise response.

## Troubleshooting

- Unclear scope → ask.
- Missing context → state assumptions.
