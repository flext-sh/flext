# FLEXT session router

Read `.agents/skills/flext-context-routing/SKILL.md` first. It is the sole
always-loaded FLEXT skill and selects the applicable entries from
`surfaces.on_demand` in `.agents/provider.toml`.

Load `.agents/skills/flext-law/SKILL.md` for FLEXT-law work and
`.agents/skills/flext-inviolable-rules/SKILL.md` for governance. Do not eagerly
load undeclared local surfaces.
