---
title: Beads reconciliation boundary
updated_at: 2026-09-25T17:27:00Z
---

# Beads reconciliation boundary

<!-- TOC START -->

- No sections found

<!-- TOC END -->

The active coordination item named by repository authority is `aihub-l42it`. Preserve
its existing intent, relationships and evidence; do not create a replacement record.

At handoff creation, both of these canonical reads failed with exit 1:

```bash
direnv exec /home/marlonsc/flext gc bd show aihub-l42it --json
direnv exec /home/marlonsc/flext gc bd --city /home/marlonsc/gc show aihub-l42it --rig aihub --json
```

The exact failure is `PROJECT IDENTITY MISMATCH`: local metadata identifies
`5e6a1521-55b4-4d51-9920-f683fa085f58`, while the running Dolt server presents
`a85fa192-f2e1-48f5-a62f-9d5947920786`. `gc rig list --json` proves city root
`/home/marlonsc/gc`; only the `gc` HQ rig is running and the `aihub` and `flext` rigs
are suspended.

Therefore no Bead was claimed, updated or closed during handoff creation. The next
session may continue the separately authorized Git/PR/CI work, but phase closure stays
open until the existing canonical record is reachable and its four-source evidence is
reconciled. Never run `bd init`, export `BEADS_DIR`/`BEADS_DOLT_*`, choose a port, or
initialize an embedded database.

When the configured store is healthy, read `aihub-l42it` and all related children,
compare registered state, Git history, measured runtime and current code intent, then
append exact repository SHAs, PR URLs, gate reports and integration evidence. Close only
after the fleet closure condition in `plan.md` is actually met.
