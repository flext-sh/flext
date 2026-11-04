---
name: flext-context-routing
description:
  Route a FLEXT repository to its law, the root AGENTS.md section "FLEXT core" at the
  package's branch.
---

# FLEXT context routing

A repository detected as internal FLEXT, one that depends on `flext-core` and is not a
fork, follows the root `AGENTS.md` section "FLEXT core". In workspace mode that is the
root of the checkout in use. A standalone checkout uses the same file in `flext-sh/flext`
at the branch or release the package is built from, never `main`. A fork follows its
upstream. The `flext-law` skill holds the change procedure, and the active bead holds the
state of the work.
