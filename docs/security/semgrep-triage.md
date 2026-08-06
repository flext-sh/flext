# Triagem Semgrep — flext-sh/flext

Gerado do dump da plataforma Semgrep (deployment `datacosmos`, 2026-08-06).

Bead de rastreio: `mro-p57t.1`

## Resumo

**52 findings** — high 0, medium 52, low 0
Confiança: high 35, medium 0, low 17

| regra | achados |
|---|---|
| `package_managers.dependabot.dependabot-missing-cooldown.dependabot-missing-cooldown` | 34 |
| `yaml.docker-compose.security.no-new-privileges.no-new-privileges` | 8 |
| `yaml.docker-compose.security.writable-filesystem-service.writable-filesystem-service` | 8 |
| `yaml.docker-compose.security.exposing-docker-socket-volume.exposing-docker-socket-volume` | 1 |
| `package_managers.uv.uv-missing-dependency-cooldown.uv-missing-dependency-cooldown` | 1 |

## Findings

Coluna **Decisão** a preencher: `corrigir` / `falso-positivo` / `risco-aceito`.

| # | sev | conf | regra | arquivo | linha | Decisão |
|---|---|---|---|---|---|---|
| 1 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 4 | |
| 2 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 11 | |
| 3 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 18 | |
| 4 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 26 | |
| 5 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 34 | |
| 6 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 42 | |
| 7 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 50 | |
| 8 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 58 | |
| 9 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 66 | |
| 10 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 74 | |
| 11 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 82 | |
| 12 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 90 | |
| 13 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 98 | |
| 14 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 106 | |
| 15 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 114 | |
| 16 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 122 | |
| 17 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 130 | |
| 18 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 138 | |
| 19 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 146 | |
| 20 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 154 | |
| 21 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 162 | |
| 22 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 170 | |
| 23 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 178 | |
| 24 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 186 | |
| 25 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 194 | |
| 26 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 202 | |
| 27 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 210 | |
| 28 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 218 | |
| 29 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 226 | |
| 30 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 234 | |
| 31 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 242 | |
| 32 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 250 | |
| 33 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 258 | |
| 34 | medium | high | `dependabot-missing-cooldown` | `.github/dependabot.yml` | 266 | |
| 35 | medium | low | `no-new-privileges` | `docker/docker-compose.db-oracle.yml` | 4 | |
| 36 | medium | low | `writable-filesystem-service` | `docker/docker-compose.db-oracle.yml` | 4 | |
| 37 | medium | low | `no-new-privileges` | `docker/docker-compose.db-oracle.yml` | 22 | |
| 38 | medium | low | `writable-filesystem-service` | `docker/docker-compose.db-oracle.yml` | 22 | |
| 39 | medium | low | `no-new-privileges` | `docker/docker-compose.flext-auth.yml` | 5 | |
| 40 | medium | low | `writable-filesystem-service` | `docker/docker-compose.flext-auth.yml` | 5 | |
| 41 | medium | low | `no-new-privileges` | `docker/docker-compose.flext-auth.yml` | 26 | |
| 42 | medium | low | `writable-filesystem-service` | `docker/docker-compose.flext-auth.yml` | 26 | |
| 43 | medium | low | `exposing-docker-socket-volume` | `docker/docker-compose.meltano-test.yml` | 8 | |
| 44 | medium | low | `no-new-privileges` | `docker/docker-compose.meltano-test.yml` | 60 | |
| 45 | medium | low | `writable-filesystem-service` | `docker/docker-compose.meltano-test.yml` | 60 | |
| 46 | medium | low | `no-new-privileges` | `docker/docker-compose.meltano-test.yml` | 71 | |
| 47 | medium | low | `writable-filesystem-service` | `docker/docker-compose.meltano-test.yml` | 71 | |
| 48 | medium | low | `no-new-privileges` | `docker/docker-compose.meltano-test.yml` | 78 | |
| 49 | medium | low | `writable-filesystem-service` | `docker/docker-compose.meltano-test.yml` | 78 | |
| 50 | medium | low | `no-new-privileges` | `docker/docker-compose.tap-oracle-test.yml` | 4 | |
| 51 | medium | low | `writable-filesystem-service` | `docker/docker-compose.tap-oracle-test.yml` | 4 | |
| 52 | medium | high | `uv-missing-dependency-cooldown` | `pyproject.toml` | 2180 | |

## Como triar

1. Abrir `arquivo:linha` e seguir o fluxo até o sink.
2. Classificar: **corrigir** (entrada externa alcança o sink), **falso-positivo** (registrar via `nosemgrep` ou `.semgrepignore` com justificativa), **risco-aceito** (com prazo de revisão).
3. Priorizar findings high com confidence=high.

Dados brutos: `~/semgrep-violations/by-repo/flext-sh__flext.json`

