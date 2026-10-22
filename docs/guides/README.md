# Guides Index

<!-- TOC START -->

- [Canonical Guides](#canonical-guides)
- [Scope](#scope)

<!-- TOC END -->

Guides are curated documents for workflow, migration, and day-to-day maintenance. They
complement generated API reference; they do not duplicate it.

Every guide follows the [governance router](../GOVERNANCE.md) and its
[engineering conformance review](../GOVERNANCE.md#engineering-conformance-review).
Root guides are the writable source for generated member guides; strengthen the
shared owner rather than copying engineering law into each package.

## Canonical Guides

- [Onboarding (Collection Rules)](onboarding.md)
- [Migration to v0.13.0](migration-to-v0.13.0.md)
- [Getting Started](getting-started.md)
- [Development](development.md)
- [Configuration](configuration.md)
- [Testing](testing.md)
- [Troubleshooting](troubleshooting.md)
- [Using flext-core](using-flext-core.md)
- [Using flext-cli](using-flext-cli.md)
- [Using flext-tests](using-flext-tests.md)
- [Make Commands](make-commands.md)
- [Codemod Rules](codemod-rules.md)
- [Skill Automation Pattern](skill-automation-pattern.md)
- [Security Guide](security.md)

## Scope

- architecture direction belongs in `docs/architecture/`
- generated API details belong in `docs/api-reference/` and each project's local
  generated docs
- project-specific operational playbooks remain local to the owning project
