# 02 — Review of plan V7: claim versus measured reality

Each row records a V7 claim, what the survey measured (section of `01-evidence.md`) and
the correction V8 adopts. No correction reduces V7's goal; each puts it at the right
owner with the right proof.

| # | V7 claim | Measured reality | V8 correction |
|---|---|---|---|
| A1 | F1(b): `flext-core` builds an auto-CLI factory | The kernel may not import `flext-cli`; `flext-cli` already owns `model_command`, `ResultCommandRoute`, `register_result_routes` (§4) | The core owns the operation contract (S3); `flext-cli` adds one method, `service_routes`, over the existing routes (S5) |
| A2 | F2: wire the core's `FlextCli.main()`, `FlextApi`, `FlextBase` | Hand-written skeletons kept for NS-LAYOUT; no-op console script; names duplicate the real `flext-cli`/`flext-api` facades (§5) | **D1 = A (operator, 2026-09-25):** delete them and the console script; NS-LAYOUT derives the requirement (S7) |
| A3 | "FlextService(BaseModel)" is new | It already is a Pydantic model (§1) | The work is validation and truth |
| A4 | Dependencies are validated ports | They skip validation; every service schema fails; `ban-skip-validation` exempts the core (§1, §5) | `t.Port[P]`, validated seeds, working schema (S1); rule fixed in S7 |
| A5 | "The pydantic container validates and injects" | Two concepts conflated; the container lies about duplicates and names (§2) | Pydantic validates ports; `api.py` composes; truthful container (S2); Protocol keys and `compose` only after a clean typing spike (S2b, else D3) |
| A6 | `fetch_global()` stays the accessor | It builds `cls()` with no dependencies; flext-law forbids hidden singletons (§1, §8) | Only for port-free services; port services are composed at the root |
| A7 | The runtime hook is typed | Implemented by about 40 bases, declared nowhere, read by `getattr` (§1) | Read through `p.RuntimeBootstrapProvider`; never declared on `x` (that would force a fleet `@override` sweep) |
| A8 | `p.Service` mirrors the service | `isinstance` is False; 17 sub-protocols inherit phantom members (§1, §7) | Own slice S4, consumers first |
| A9 | Eight fail-soft sites | Seven exist; the real total is 42 (§3) | S8/S9 by owner, with failure-path tests; beartype stays with `flext-edcqq` |
| A10 | Docs in `flext-core/docs/service-guide.md` | The canonical guide is `docs/guides/service-patterns.md`; two stale docs; two root contradictions (§8) | One guide; stale docs deleted; generated guides fixed at the root source |
| A11 | No ADR | A fleet service contract is an architectural decision | ADR-019 |
| A12 | "flext-cli refactor" rewires consumers | Does not exist; the owner is `flext-infra refactor` / `make mod` (§4) | Codemod rules with `ast-grep test`; `flext-infra refactor apply-renames --csv … --roots … --apply` |
| A13 | "CI green → merge" | The core integration CI is already red (§9) | Every PR is green on the gates it touches; foreign red is reported with its owning bead, never masked |
| A14 | F3/F4 in the same wave | 217 services, 15 stubs, per-member engineering (§7) | This wave ships the base and tooling; adoption is one bead and one PR per member |
| A15 | "Fail with cause" is only a law | `r.unwrap()` drops the cause (§1) | `unwrap` chains the cause (S1) |
| A16 | `check && push` protects consumers | Consumers read the core through their locks; the superproject gitlinks diverge from member tips (§5, §9) | Pre-merge validation in the fleet validation workspace at member tips; consumers refresh their lock in their own PR |

V7 laws R1–R11 stay in force; R8 (suite reds triaged at the end) applies only to reds
foreign to the slice.
