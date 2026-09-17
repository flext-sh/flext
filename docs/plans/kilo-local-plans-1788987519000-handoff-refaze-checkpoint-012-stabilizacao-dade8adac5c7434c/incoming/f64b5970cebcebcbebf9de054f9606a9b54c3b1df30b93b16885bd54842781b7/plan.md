# Handoff — Refazendo o Planejamento de Estabilização Checkpoint 0.12.0 (Nova Sessão)

> Criado: 2026-09-09 21:00 UTC. Motivo: encerramento da sessão anterior após descoberta
> de contradição arquitetural na lei de namespace + drift massivo de 32 submodules.
> Este documento é a fonte de verdade de entrada para a NOVA sessão de planejamento.
> Plano v2 ainda válido: `1788975180492-execution-strategy-skills-automation.md`
> Status: `1788961161018-flext-012-checkpoint-status.md`. Bead-mãe: `flext-yirgp`.

## 1. Análise de arquitetura (o que aprendemos)

### 1.1 Stack de authory (ordem obrigatória)
`~/.agents/AGENTS.md` → skill local branch-matched `flext-law` (`~/flext/.agents/skills/flext-law/SKILL.md`) → scope `AGENTS.md` do membro → Bead ativa. Governança gerida por projeções AIHUB em `AGENTS.md` (não editar seção managed à mão — só via owner).

### 1.2 Camadas FLEXT (comprovadas em código)
Ordem: `settings → config → c → t → p → m → u → base → services → api → cli`

- operacionais `r/e/x/h/d/s` — `flext-infra/_constants/namespace.py:35-62`.
Índice de arquivo→camada em `flext-infra/_constants/namespace.py:48-61`
(`_settings.py`→settings rank 0 … `api.py`→api rank 9).

### 1.3 CONTRADIÇÃO CRÍTICA EXPOSTA (achado principal desta sessão)
A regra `NS-IMPORT` (`flext-infra/validate/_namespace_rules/imports.py:151`,
`_reverse_import`) proíbe runtime-import de `t/m/u` em owner de camada
settings/config — inclusive pela fachada raiz (`from flext_api import m, t, u`
também é violado porque a regra decompõe os símbolos, imports.py:104-121).
MAS todo `Flext<X>Settings` de consumidor declara um namespace-model Pydantic
aninhado em runtime (`m.BaseModel` + `m.Field` + `u.model_validator`) — padrão
presente em flext-auth, flext-quality, flext-ldif, flext-target-ldif,
flext-api (frota: `grep -rln model_validator */src/*/_[sl]ettings*.py`).
E o único caminho alternativo (import `pydantic` direto) é proibido para
consumidores por `ENFORCE-070` (runtime-census: "owner flext-core").
**flext-core escapa só porque é o dono de pydantic** (`from pydantic import
model_validator` em `flext-core/src/flext_core/_settings.py:36`).
→ Nenhum padrão consumidor ممکن fecha ambos. Ou a regra é alterada no dono
(flext-infra), ou a arquitetura de settings dos 13+ consumidores é reescrita.
**Decisão pendente do operador** (falta gravíssima sem ordem explícita):

- **A) (recomendada)** Carve-out em `_reverse_import`: owner rank ≤ 1
  (settings/config) permite runtime-import das facades de DECLARAÇÃO `m`/`u`
  (`t` continua TYPE_CHECKING-only). ~5 linhas no owner + testes
  `flext-infra/tests/unit/check/`, depois `make gen/mod` propaga.
- B) Mover namespace-models de `_settings` para `_models` em toda a frota
  (muda contrato em 13 membros, pesado, quebra padrão estabelecido).
- C) Suspender regra para settings (buraco na lei — proibido pelo operador).

### 1.4 Segunda regra a fechar por automação
`NS-CONTRACT` (annotations banidas `dict/object/Any/Optional` — `namespace.py:78-83`,
checado em `validate/_namespace_rules/contracts.py:85-108`):
mapa canônico: `dict[K,V]` → `t.MappingKV[K,V]`; mutação local → `MutableMapping`
(inferido, sem annotation); `object` → `t.JsonValue`/`t.JsonPayload`; `Any` →
uniao concreta por contexto; `Optional[X]` → `X | None`.
**Automação alvo**: codemod ast-grep registrado no catálogo `make mod`
(flext-infra), aplicável por membro cwd (`make mod` é cwd-scoped —
Makefile root:1061). TODO: mapear onde registramos codemods
(`flext-infra/src/flext_infra/_utilities/private_import_facades.py` é o exemplo
existente; testes em `tests/unit/codemod/`).

### 1.5 Estado do check flext-infra
RED 1427 erros (namespace=1388, duplication=24, silent-failure=6, loc-cap=5,
mypy=2, pyrefly=1, runtime-census=1) — **residuais aceitos** pelo operador no
checkpoint (correção salva: `closeout.checkpoint_0_12_0`), donos
flext-h2ffh/flext-1wjg1.16.34/flext-ct0mo/flext-nnquz.

## 2. Estado atual (evidência)

| Local | Branch | Tip | Estado |
|---|---|---|---|
| `~/flext` (root main) | `0.12.0-dev` | `c424043b85` | limpo no root; submodules em tips remotas |
| `~/flext-release-012` (release) | `release/checkpoint-0.12.0` | `4147d43428` | publicado; **32 submodules com drift local NÃO commitado** |
| flext-infra (release lane) | `release/checkpoint-0.12.0` | `0d29f44ee` | contém fix `_builtin-self-*` fora do `{% else %}` do Makefile.j2 (commit `3a447b553` recuperado via merge no-ff `9c503e16a`) — **fix NÃO absorvido em 0.12.0-dev** (main flext-infra = `459ddf9c4`, sem o fix) |

**CRÍTICO — não perder:** o WIP do flext-api no release worktree está NO
WORKING TREE (`528c9e7f` + não commitado): refatoração `_protocols/`→
`_services/` dos transports (bead `flext-482u9`, completa até `p.` sem alias),
`_settings.py` corrigido para o padrão canônico (`from flext_api import m, t, u`
via fachada raiz + `t.MappingKV` + validador com `t.JsonValue`; runtime
comprovado `settings.Api.timeout → 30.0`), `make fix` VERDE lá. Regra
fundamental: **nunca `reset`/`checkout`/`clean`/`stash` de trabalho alheio —
fix-forward apenas**.

### Padrão de drift nos 32 submodules (clasificado)

- 30 members: ~15 arquivos (+224/-83) — docs/Makefile/examples geridos
  (resíduo fmt/gen legítimo) → absorver com commit.
- flext-api: 33 arquivos — refatoração estrutural de transports (incompleta,
  associada a `flext-482u9`) + docs. **Continuar, não reverter.**
- flext-core: 4 arquivos beartype (-17/+11) — investigar antes de absorver.

## 3. Violations remanescentes de namespace em flext-api (pós-correção settings)
`make check` RED 47: pyrefly=10, mypy=4, **namespace=33**:

- NS-STRUCT-001 module-alias: `api.py:194` (`api: FlextApi =
  FlextApi.fetch_global()`), `base.py:46` (`s = FlextApiServiceBase` — redeclaração
  proibida do operational r/e/x/h/d/s; **init**.py mapea "flext_web"→(d,e,h,r,x)
  sem "s"), singleton `settings`/tests `tests/{base,constants,models,protocols,typings,utilities}.py`
- NS-STRUCT-002: `tests/{constants,models,protocols,typings,utilities}.py:14/19`
  — facade must declare one nested `TestsFlextApi` MRO
- NS-LAYOUT-001..005: falta `cli.py`; `_constants/_typings/_models/_utilities`
  exigem `base.py` de entrada (gerador/estrutura)
- NS-IMPORT-001..003 em `_settings.py:21` — resolVIDOS pending decisão 1.3-A
- NS-CONTRACT dict — files 52/59 `_settings.py` → fechar via codemod 1.4

## 4. Cadência eedas a revisar criticamente (instrução permanente do operador)
Não aceitar o que está escrito; validar contra projeto/planos real; se bead
redundante/duplicada → avaliar regra e os blocks ANTES de fechar; nunca fechar
sem re-run de gates no SHA merged + evidência (verb, cwd, exit, output, SHA).

## 5. TODO imediato da nova sessão (re-planejamento)

1. **Confirmar decisão 1.3** com operador (A/B/C) —ependency para flext-api.
2. Re-construir planejamento v3 a partir deste handoff + beads
  (`bd ready`, revisar `flext-yirgp`, `flext-482u9`, `flext-hkz4p`, PRs api #83/#84 CI vermelho em setup bootstrap → fleet blocker `flext-cpkk`/`flext-5k9r7`).
3. Close cycle por membro (uma agulha): commit scoped → push FF → PR → merge
   no-ff na integração (`origin/0.12.0-dev`) → gates rerun no SHA merged →
   fecha bead → apaga worktree/branch do ciclo.
4. Regras em fila (uma por vez, com automação): NS-IMPORT carve-out (decisão 1.3)
   → NS-CONTRACT codemod → NS-STRUCT tests MRO → NS-LAYOUT base.py/cli.py →
   strip `class-nesting-mappings.yml` (proibido pelo operador: descoberta
   deve ser SSOT automática).
5. `make fmt/fix/check/test` full fleet após cada slice verde;
   testmon obrigatório; WAZA no fim.

## 6. Guardrails (erros que custaram tempo nesta sessão)

- `git submodule update` reseta gitlinks — usar checkout de submodule único.
- `make mod` é cwd-scoped (Makefile._builtin_mod_apply:1061) — rodar POR MEMBRO.
- Pipes com `tail` perdem exit code — guardar log completo.
- Gate `check` de flext-api demora ~45-270s (runtime-census importa módulos);
  validar runtime com `uv run --no-sync python -c` antes do gate longo.
- `uv run --project` SEM `--no-sync` ressincroniza venv compartilhado.
- TypeAliasType (PEP 695) não serve para `isinstance` — usar tipo concreto.
- Nome em annotation banida é checado até sob facade (`t.Any` ≠ permitido:
  `name_of()` extrai "Any" de `t.Any`).
