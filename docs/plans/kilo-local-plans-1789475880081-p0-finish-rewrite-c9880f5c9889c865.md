# P0-FINISH — Autocrítica e reescrita do plano de encerramento 0.12.0 (2026-09-15T17:50Z)

<!-- TOC START -->

- [0. Autocrítica pesada (o que fiz de errado e a lição operacional)](#0-autocritica-pesada-o-que-fiz-de-errado-e-a-licao-operacional)
- [1. Estado de verdade hoje (evidência da sessão)](#1-estado-de-verdade-hoje-evidencia-da-sessao)
- [2. Ondas de execução (ordem de dependência estrita; cada onda fecha com commit+push+bead)](#2-ondas-de-execucao-ordem-de-dependencia-estrita-cada-onda-fecha-com-commitpushbead)
  - [Onda A — Adotar e estabilizar o working tree (só o meu escopo)](#onda-a-adotar-e-estabilizar-o-working-tree-so-o-meu-escopo)
  - [Onda B — gen ×2 (a pedra angular; agora sem WIP quebrado no caminho)](#onda-b-gen-2-a-pedra-angular-agora-sem-wip-quebrado-no-caminho)
  - [Onda C — Engine make mod (a automação pedida; ANTES de qualquer reparo manual novo)](#onda-c-engine-make-mod-a-automacao-pedida-antes-de-qualquer-reparo-manual-novo)
  - [Onda D — Gates e tests (obedecer o que os verbos geram)](#onda-d-gates-e-tests-obedecer-o-que-os-verbos-geram)
  - [Onda E — Centralização c,t,p,m,u (gen-gated, agora desbloqueado)](#onda-e-centralizacao-ctpmu-gen-gated-agora-desbloqueado)
  - [Onda F — Fechamento e publicação](#onda-f-fechamento-e-publicacao)
- [3. Regras inegociáveis (reafirmadas)](#3-regras-inegociaveis-reafirmadas)
- [4. Fora de escopo deste plano](#4-fora-de-escopo-deste-plano)
- [5. Aceite final (checklist duro)](#5-aceite-final-checklist-duro)

<!-- TOC END -->

## 0. Autocrítica pesada (o que fiz de errado e a lição operacional)

1. **Whack-a-mole manual onde a engine mandava**: reparei ~7 defeitos de extração de
   famílias (`def __all__`, import `mm` perdido, `..deps` vs `...deps` ×3, fields
   Pydantic dropados, MRO com base abstrata antes dos parts, classmethod qualificado na
   part, classe duplicada morta) UM A UM, manualmente — enquanto o operador pedia
   explicitamente engine (`make mod`/ast-grep/rope/rules-as-data). **Nunca rodei
   `make mod` na sessão.** → Onda 2 do novo plano automatiza essa classe de defeito na
   engine ANTES de qualquer novo reparo manual.
2. **Corrida com o peer antes de coordenar**: ~6 tentativas de gen colidindo
   (`atomic source changed`, `identity changed`, `unowned journal`) ao longo de 2h+
   antes de postar a nota de coordenação no `flext-fkfmu`. Coordenação era passo ZERO (o
   handoff já alertava: atores concorrentes são o risco dominante).
3. **Agentes de fundo abandonados sem auditoria**: os 3 subagentes wms falharam em
   silêncio criando worktrees vazias; deixei 2 deles ~50min sem verificar o lane.
   Deveria ter auditado o lane em ≤15min e assumido.
4. **Escopo estreito demais na Onda 2 original**: o sweep stubs/fallback/silenciamento
   (silent-failure/smells) nos outros ~27 membros NÃO começou — só wms-family foi.
5. **Onda 4 nunca começou**: zero PRs, zero conclusão de branches/worktrees soltos, zero
   tag; beads ainda abertos (`flext-wjozx`, `flext-fkfmu`, `flext-c4k44`).
6. **Centralização zerada em execução**: colhi o backlog (harvest jscpd+crg) mas não
   executei nenhuma fatia — e não sequenciei explicitamente atrás do desbloqueio do gen.
7. **Validação canônica incompleta**: provei pytest por membro, mas nunca `make test`
   workspace nem o diagnóstico do timeout da suíte infra (`flext-c4k44`).

Lição única: **desbloquear a engine primeiro, coordenar antes de agir, auditar
delegações em ≤15min, e fechar ondas em ordem de dependência (gen → mod → check → test →
publicar).**

## 1. Estado de verdade hoje (evidência da sessão)

| Item             | Estado                                                                                                                                                                                                                                                                                                           |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| flext-infra      | Meus reparos de adoção PARCIAIS NÃO-COMMITADOS (bootstrap fields, render staticmethod, beads.py container import, base.py MRO); `_models/_codegen/` adotado em `70dea697b`; `_conform` depth commitado (`c3f574807`); peer ainda com `_models/_config/` untracked e `conform.py` re-export 11 linhas uncommitted |
| gen              | Nunca verde ×2; última tentativa abortada; progresso camada-a-camada (imports → pydantic → MRO → template root → model_rebuild → repository_provider)                                                                                                                                                            |
| wms-family tests | POUSADO nos tips (a1f077c, 1d0344d, 1a9b7bb, 28bf20c, 2d301a2); offline gate tap corrigido (item.path pytest 9)                                                                                                                                                                                                  |
| Marcadores SSOT  | `f5a3bd711` pousado; projeção fleet parcialmente aplicada pelo conform do peer                                                                                                                                                                                                                                   |
| Beads            | `flext-wjozx` in_progress (missão), `flext-fkfmu` open (lock/journal), `flext-c4k44` open (suíte infra), `flext-7pa7o` open (épico settings — sessão dedicada, FORA deste plano)                                                                                                                                 |
| Superprojeto     | `8a524a755d` sincronizado; ADR-016 + épico docs pousados                                                                                                                                                                                                                                                         |
| Lanes sujas      | dbt-oracle (peer WIP `_config` etc.), flext-api/auth/core pyproject marker projections (1 arquivo cada), flext-infra-worktrees/ = lane estrangeira NÃO TOCAR                                                                                                                                                     |

## 2. Ondas de execução (ordem de dependência estrita; cada onda fecha com commit+push+bead)

### Onda A — Adotar e estabilizar o working tree (só o meu escopo)

1. Commitar os reparos não-commitados do flext-infra como UM commit de adoção
   (`fix(codegen): complete _conform split adoption — fields, MRO order, part-qualified`
   `calls, container import`): `bootstrap.py` (fields graft), `base.py` (MRO: parts
   antes de `s[...]`), `render.py` (`_managed_gitlinks` staticmethod + owner-qualified),
   `beads.py` (runtime container import), mais qualquer `parent.parent` de profundidade
   errada que o `grep` apontar em `_conform/`.
2. dbt-oracle: NÃO adotar agora (zona viva do peer) — apenas garantir que a remoção do
   `services/base.py` duplicado permanece (já pousada) e registrar no bead.
3. Projeções de marcador (pyproject 1-arquivo) em api/auth/core: commitar em lote
   `chore(pytest): project marker vocabulary` por membro + push (padrão já usado no
   tap).

### Onda B — gen ×2 (a pedra angular; agora sem WIP quebrado no caminho)

1. Quiescência do peer (watch 60s ×2) → `make gen` ×2 consecutivos exit 0.
2. Se o peer quebrar de novo: adotar o estado DELE pousado (fetch/merge) e repetir —
   MÁXIMO 3 ciclos; se persistir, registrar em `flext-fkfmu` e seguir para Onda C (a
   engine pode rodar com o gen que o PRÓPRIO peer produziu — mesma fonte editável).
3. `make fix` ×2 e `make fmt` ×2 (idempotência).

### Onda C — Engine make mod (a automação pedida; ANTES de qualquer reparo manual novo)

1. `make mod` no workspace (rope + ast-grep regras YAML): validar que a engine reproduz
   os reparos manuais desta sessão (import perdido, profundidade relativa, fields) — é o
   teste de regressão da automação.
2. Para as classes de defeito sem regra hoje, adicionar LINHAS YAML em
   `flext-infra/rules/*.yaml` (rules-as-data; ADR-014):
   - import de container perdido em parts de família (`NameError`/`AttributeError` de
     alias de mixins);
   - profundidade relativa errada pós-move (`codegen.deps` inexistente);
   - classmethod qualificado na part chamando irmão via `cls.` (falha de MRO);
   - fields de fachada dropados no split (probe de construção no mod-fixpoint).
3. Se uma regra não couber em YAML: validador tipado em `flext-infra/validate/` seguindo
   os detectores existentes, ligado ao fixpoint do `batch_apply` (nunca detector
   ad-hoc).
4. Aceite: `make mod` aplica e a segunda passada é no-op (fixpoint), sem falsos verdes.

### Onda D — Gates e tests (obedecer o que os verbos geram)

1. `make check`: meta Ruff/Mypy/Pyright/Pyrefly = 0; findings custom (silent-failure,
   smells, duplication, loc-cap) colhidos e triados com evidência.
2. Sweep stubs/fallback/silenciamento (Onda-2 original agora executada de verdade):
   fan-out de subagentes por CLUSTER de membros (4-6/agente) com os findings dos gates —
   correção na causa raiz (`r.Fail`/`e.*` na fronteira), sem `# noqa`.
3. `make test` workspace; suíte infra timeout → diagnosticar pelo runner
   (`validate/_pytest_runner/command.py`) e corrigir no dono — bead `flext-c4k44`.
4. `make test PROJECT=<membro>` ×2 para cada membro tocado nas ondas A-C.

### Onda E — Centralização c,t,p,m,u (gen-gated, agora desbloqueado)

1. Fatia 1 (constantes): trace headers → `c.Observability.TraceHeaders`; substituir os
   6+ sites em flext-observability; gen + tests ×2.
2. Fatia 2 (contexto): estender `u.Context` (trace_id/span_id/baggage já têm
   `CORRELATION_ID` no core) e consumir de flext-observability — extender, não
   bulk-move; apagar as ContextVars duplicadas do membro.
3. Fatia 3 (instrumentação): `u.HttpInstrumentation` (httpx sync/async + aiohttp);
   flext-observability vira fachada fina re-exportando.
4. Cada fatia: lane core + lane consumidora + gen ×2 + pytest ×2 + bead comment. Padrão
   facade OBRIGATÓRIO nas novas famílias core (`_[modulo]/` + `base.py` agregador MRO,
   sem `_part/`), DRY/SOLID/YAGNI/SSOT, c,t,p,m,u primeiro.

### Onda F — Fechamento e publicação

1. Varredura de conclusão: PRs por membro tocado (`gh --admin --merge` autorizado, CI
   verde no SHA merged), branches/worktrees da minha lane removidos, lanes abandonadas
   do tema assumidas ou devolvidas com bead.
2. `make release`/tag `0.12.0` nos repos afetados — SOMENTE após ondas A-E verdes ×2 e
   CI do SHA merged.
3. Beads: fechar `flext-wjozx` (missão), `flext-fkfmu` (com evidência viva do lock),
   `flext-c4k44` (suíte); `flext-7pa7o` permanece para a sessão dedicada.
4. Docs/ADRs/skills: ADR-014 anotado com as novas regras de extração; ADR-016 → Accepted
   quando o épico rodar; plano P1 em `docs/plans/` (baseline 0.13.0: coordenação
   peer-first, engine-first, publicação por fatia).

## 3. Regras inegociáveis (reafirmadas)

- fix-forward adopt SEMPRE; proibido rollback/restore/stash; never force-push.
- Tip da branch de integração como base; worktree dedicada por lane; workspace padrão
  recebe merges/push incremental verde.
- bd SEMPRE via `direnv exec .`; padrão Gas City (nunca `bd init` em membro).
- Obedecer o que setup/gen/fix/fmt/check/test geram; causa raiz para TUDO
  (warnings/cosméticos/pré-existentes).
- Facade pattern estrito: `_[modulo]/` + `base.py` agregador MRO sem `_part/`; Single
  Class Nested; DRY/SOLID/YAGNI/SSOT; c,t,p,m,u primeiro.
- jscpd + code-review-graph + ast-grep + make mod como superfícies de detecção;
  subagentes com auditoria de lane em ≤15min.
- Máximo 3 tentativas por ciclo bloqueado por corrida: adotar, registrar, seguir.

## 4. Fora de escopo deste plano

- Épico FlextSettings/FlextConfig (`flext-7pa7o` + ADR-016) — sessão dedicada.
- Validação de consumidores externos (ai-hub/cosmos-main/algar-\*) — pertence ao épico.
- `flext-infra-worktrees/` — lane estrangeira, nunca tocar nem concluir por ela.

## 5. Aceite final (checklist duro)

- [ ] `make setup/gen/fix/fmt` exit 0 ×2 idempotentes no workspace
- [ ] `make mod` fixpoint com as novas regras (2ª passada no-op)
- [ ] `make check`: 4 analisadores 0; customs triados com evidência por membro
- [ ] `make test` workspace verde ou receipt de timeout documentado no bead
- [ ] Membros tocados: `make test PROJECT=<m>` ×2 verde
- [ ] PRs merged com CI verde no SHA; worktrees/branches da lane limpos
- [ ] Beads fechados com 4 fontes de evidência; ADR-014/016 e docs atualizados no mesmo
      ciclo
- [ ] Plano P1 escrito em `docs/plans/`
