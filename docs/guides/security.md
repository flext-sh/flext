# Security Guide

<!-- TOC START -->
- [Dependabot vulnerability governance](#dependabot-vulnerability-governance)
- [Dependency cooldown](#dependency-cooldown)
<!-- TOC END -->

Security practices are governed by project-specific policies and central architecture ADRs.

Primary references:

- `docs/architecture/adr/README.md`
- `.agents/skills/scripts-security/SKILL.md`
- `flext-core/docs/architecture/clean-architecture.md`

## Dependabot vulnerability governance

- O inventário oficial de alertas de segurança está em:
  - `docs/reports/dependabot-alerts-2026-06-24.md`
- O plano atual cobre três frentes:
  - inventariar alertas por gravidade e pacote,
  - agrupar remediações em ondas (critical/high first),
  - ampliar Dependabot para rastrear os módulos Python com `pyproject.toml` no monorepo.
- A execução de segurança deve registrar evidência por ação (alerta, commit de correção e status de fechamento) no `bd`,
  sem "close" sem trilha.

## Dependency cooldown

`flext-infra/config/codegen.yaml` owns one `dependency_cooldown_days` value.
Codegen projects it to both uv `exclude-newer` and every Dependabot ecosystem,
so routine updates cannot raise a dependency floor before uv will resolve it.

Dependabot does not delay security updates. An urgent, reviewed security floor
may therefore be listed in `dependency_cooldown_exclusions`; codegen projects
that package to uv `exclude-newer-package = false`. Keep this list narrow and
remove entries when the global cooldown naturally admits the security floor.
