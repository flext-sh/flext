---
name: scripts-security
description: Security scripts — secrets management, vault operations, and security auditing. Use when editing scripts/security/.
---

# Scripts Security

## Scope

- `scripts/security/_base_security_script.py`
- `scripts/security/decrypt_secrets_vault.py`
- `scripts/security/example_usage.py`
- `scripts/security/generate_production_secrets.py`
- `scripts/security/__init__.py`
- `scripts/security/security_audit.py`

## References

- `.claude/skills/rules-scripts/SKILL.md`
- `docs/guides/security.md`

## Rules

- Security scripts must never log or print secrets to stdout/stderr.
- All scripts must be non-interactive by default; interactive prompts require `--interactive` flag.
- Secrets must be read from environment variables or encrypted vaults, never hardcoded.
- Security audit output must go to `.sisyphus/reports/` using artifact naming contract.

## Instructions

- When modifying vault scripts, verify decryption still works with test fixtures.
- When adding security checks, wire them into the security audit entrypoint.
- Keep the `_base_security_script.py` as the base class for new security scripts.

## Workflow

1. Identify the security concern to address.
2. Create or modify the script under `scripts/security/`.
3. Ensure the script extends `_base_security_script.py` if applicable.
4. Test with `python scripts/security/<script>.py --help`.
5. Verify no secrets leak in output.
6. Run security gate: `make security PROJECT=<name>` or `make check PROJECT=<name> CHECK_GATES=security`.

## Examples

Good (primary — Make verbs for security gates):

```bash
make security PROJECT=flext-core                     # dedicated security check
make check PROJECT=flext-core CHECK_GATES=security   # security via check gate selector
make check PROJECT=flext-core                        # all 4 gates including security
```

Good (internal — security audit scripts):

```bash
python scripts/security/security_audit.py --output .sisyphus/reports/scripts-security--json--audit-latest.json
```

Why good: Make verbs for standard security gates; artifact naming for detailed audits.

Bad:

```bash
echo "$SECRET_KEY" | python decrypt.py
```

Why bad: Secrets piped through shell, no structured output.

## Verification

Make gates (primary):

- `make security PROJECT=flext-core` — run bandit security check
- `make check PROJECT=flext-core CHECK_GATES=security` — security via gate selector
- `make check PROJECT=flext-core` — all 4 gates including security

Script-level checks (internal):

- `python -m compileall scripts/security`
- `python scripts/security/security_audit.py --help`
- `rg "Owner-Skill:.*scripts-security" scripts/security`

## Scripts

| Path | Purpose | Invocation |
|------|---------|------------|
| `scripts/security/__init__.py` | Package marker | — |
| `scripts/security/_base_security_script.py` | Base class for security scripts | (imported by other security scripts) |
| `scripts/security/decrypt_secrets_vault.py` | Decrypt secrets from vault | `python scripts/security/decrypt_secrets_vault.py` |
| `scripts/security/example_usage.py` | Security script usage examples | `python scripts/security/example_usage.py` |
| `scripts/security/generate_production_secrets.py` | Generate production secrets | `python scripts/security/generate_production_secrets.py` |
| `scripts/security/security_audit.py` | Run security audit | `python scripts/security/security_audit.py` |
