# FLEXT session router

Read .agents/skills/flext-context-routing/SKILL.md first. It is the sole
always-loaded FLEXT skill and selects at most three task-specific entries from
the surfaces.on_demand catalog in .agents/provider.toml.

For implementation, review, migration, or refactoring, load
.agents/skills/flext-law/SKILL.md through that router. Do not eagerly load the
full catalog or use undeclared provider surfaces.
