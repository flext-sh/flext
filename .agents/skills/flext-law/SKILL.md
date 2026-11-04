---
name: flext-law
description:
  Apply FLEXT's law to a change in a FLEXT repository; the law itself is the root
  AGENTS.md section "FLEXT core".
---

# FLEXT law

The law of a FLEXT change is the root `AGENTS.md` section "FLEXT core", read at the
branch the package is built from. This skill holds only the procedure for applying it.

1. Read the FLEXT core, the member's `AGENTS.md`, the accepted ADR that owns the topic
   and the bead, and correct whichever of them the change would contradict before code.
2. Change through the owner: Rope for Python semantics and imports, an authored
   ast-grep rule with its fix for a simple syntactic pattern, the template or
   configuration for a generated file; a recurring correction is one rule that
   `make mod` applies to every occurrence.
3. Show the claimed behavior on the real entry point at the claimed revision, then run
   `gen`, `fmt`, `fix`, `mod`, `check` and `tests` in every repository the change
   touches; until the verbs are validated, direct `ruff check` and `pyrefly check` on
   explicit paths give the lint verdict.
4. Land through a lane cut from the integration tip, a PR and a `--no-ff` merge into
   `0.12.0-dev`, member commits before the gitlink, with the evidence on the bead.
