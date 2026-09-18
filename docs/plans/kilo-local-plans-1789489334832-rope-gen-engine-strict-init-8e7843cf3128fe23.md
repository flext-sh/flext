# Plano Unificado v4 — Engine Rope-Gen + LOC-Cap + Fechamento 0.12.0

Unificação de 4 planos: `1789489334832-rope-gen-engine-strict-init` (v3, engine),
`1789475880081-p0-finish-rewrite` (p0-finish),
`1789476032590-facade-loc-cap-convergence` (superseded) e
`1789489330487-loc-cap-config-landing-plan` (v3, pouso `_config`). Este arquivo é a
única autoridade; os demais são histórico.

## 0. Lições operacionais (consolidadas, obrigatórias)

1. Research-first: reusar recipe provado (rope/`make mod`/rules-as-data); jamais
   reimplementar na mão o que a engine automatiza.
2. Gate canônico APÓS cada onda; onda que não couber na sessão NÃO inicia (batch
   realista).
3. Commit escopado + push incremental imediato; mutação longa sem commit = trabalho
   adotado por terceiro (já aconteceu 2×).
4. Beads com evidência por grão (comando/exit/SHA) via `direnv exec <repo> gc bd ...`;
   bloqueio de ferramenta → registrar comando+erro exato, nunca silenciar nem burlar.
5. Coordenação ANTES de agir: board post + janela de quiescência (≤2 min sem mutação nos
   src) antes de gen/commit; máx 3 ciclos de corrida → adotar, registrar, seguir. REGIME
   17:51 do operador (prevalece): agentes ÚNICOS sobre flext com total desbloqueio —
   coordenação vira auditoria+adoção fix-forward; quiescência aplica-se só a edição
   humana concorrente (input-CAS converte corrida mid-run em falha limpa).
6. Fix-forward/adopt SEMPRE; proibido reset/restore/stash/rebase/force-push de trabalho
   compartilhado. Exceção única: descartar MINHA cópia local redundante já superseded
   por commit pousado = adoção.
7. Commit por paths explícitos (nunca `git add -A`); arquivos de peer nunca entram no
   meu commit; gen é o ÚNICO escritor de projeções.

## 1. Estado de verdade (2026-09-15 17:55Z, verificado)

| Item               | Estado                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| flext-infra tip    | `c3f574807` (`0.12.0-dev`): markers `f5a3bd711`, split `_codegen` `70dea697b`, split `_conform`+depth `b6926051b`/`c3f574807`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Working tree infra | 21 paths: 6× `M _conform/*` (stale drift → adotar tip), 13× `?? _models/_config/*.py` + `M _config/__init__.py` (2942→63) + `M _models/__init__.py` (split genuíno a pousar)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| LOC-cap tema       | 3 alvos: codegen ✔ (peer), conform ✔ (peer), **config ✘ (F0 meu)**; residual `_codegen/__init__.py` 51KB → F2.W1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| gen                | Nunca verde ×2; abortos por corrida com peer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Tests wms-family   | Pousados nos tips (`a1f077c`..`2d301a2`); offline gate tap corrigido                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Beads              | `flext-471ws` (loc-cap, meu), `flext-wjozx` (missão), `flext-fkfmu` (lock/journal), `flext-c4k44` (suíte infra timeout), `flext-5fxu6.4` (dono gerador), `flext-7pa7o` (épico settings — FORA)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Superprojeto       | gitlink `flext-infra` atrás; `m` em vários membros = lanes de outros, intocar; `flext-infra-worktrees/` = lane estrangeira, NUNCA tocar                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Ferramentas        | `bd` bloqueado por permissão nesta sessão (registrar comando+erro); `rg` shim quebrado (usar grep/make/git)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Snapshots paridade | intactos em scratch: `pre/post_{codegen,config,conform}.json`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Frota (subagentes) | 10 despachados (sessão fleet, plano `1789475884207`): **cli DONE c/ evidência** (tier-whitelist 10→1, total 615→606, in-tree NÃO-commitado; editou flext-core `_utilities/config.py` p/ `u.Yaml.*` → **landing coordenado core→cli, gitlinks do lote juntos**); **core DONE forte** (namespace 0, 8 gates 0, **2682 testes passando**; NS-LAYOUT criado; adotou cooperativamente o Yaml do cli + fixou IndentationError `_loaders.py`; tree NÃO-commitada; core+cli INTERDEPENDENTES → lote coordenado core→cli + revalidação no pouso); tests/ldif DONE relatório vazio (auditar trees); web/db-oracle/grpc/meltano/dbt-oracle FAILED 503 gateway (resumíveis via task_id, contexto preservado); observability em curso (último); codemod 25 errs restantes = infra (operador) + tests (auditar). Relatório vazio = auditar tree SEMPRE |

## 2. Decisões (herdadas dos 4 planos, inalteradas na substância)

1. **Render purity**: `render = f(SSOT, templates, PINS)`; entrada de ambiente no render
   é bug P0.
2. **Rope DENTRO do gen**: `make gen` único escritor; lazy-init re-implementado sobre
   motor rope; `make mod` só estrutural à mão; um motor, dois modos
   (`codegen init`/`conform`).
3. **Init strict/total**: exports = união ordenada dos `__all__` dos irmãos; sem
   `__all__` → GEN-W001; `__all__` stale → GEN-E001 (erro); colisão → erro; exceções =
   linha em config.
4. **Três níveis**: gen EMITE warnings; fix CORRIGE autocorrigível (rope); check REPORTA
   remanescentes. Detector nunca desativado; nada vira sucesso silencioso.
5. **Resiliência transacional**: snapshot input-CAS por invocação; falha → reverse-apply
   SÓ dos efeitos da própria invocação (gen E fix); critério: diff vazio pós-falha.
6. **Rules-as-data**: regra nova = seção tipada em `config/codegen.yaml` /
   `rules/*.yaml`, nunca classe detectora ad-hoc.
7. **Taxonomia**: GEN-W001 (sem `__all__`), W002 (import absoluto self → fix
   relativiza), W003 (módulo fora do layout), W004 (formato/header), W005 (ciclo runtime
   SCC), GEN-E001 (stale `__all__`), colisão de irmãos (erro).
8. **Cobaias**: `cosmos-docgen` (externa standalone; não vira membro) porta a engine ×2
   verde antes da frota; depois `agents/` (`agents_governance`).
9. **Landing**: flext-infra via PR + `merge --admin --merge` em `0.12.0-dev`
   (autorização operador registrada no handoff); membros via push FF no tip; gates no
   SHA integrado; gitlinks bump+push por último.
10. **Checkpoint 0.12.0**: operador ACEITA violações/warnings remanescentes desde que
    flext-infra e seus verbos funcionem completos em todos os ciclos (correção
    registrada).
11. **Exemption lint** (SLF001 etc.): só com lint fresco da própria sessão, só
    path+regra escopados (precedente `_rope`), comentário OPERATOR-AUTHORIZED; nunca
    exemption ampla, nunca preemptiva.

## 3. Fases unificadas (ordem de dependência estrita; cada onda fecha com commit+push+bead)

### F0 — Estabilizar + pousar `_config` (lane loc-cap; primeira porque limpa o tree para tudo)

1. **F0.1** `git fetch`; confirmar tip;
   `git checkout -- src/flext_infra/codegen/_conform/` (descarta drift stale meu; tip é
   canônico). Status esperado: exatamente 15 paths da família `_config` (13 `??` + 2
   `M`); além disso → parar e reclassificar.
2. **F0.2** Board post (lane peer/engine): janela de pouso `_config` aberta; quiescência
   ≤2 min.
3. **F0.3** `make gen` ×2 (ponto fixo; gen reescreve meu `__init__.py` diferente →
   ADOTAR saída do gen) → `make fix` → `make fmt` (idempotentes).
4. **F0.4** Sonda paridade: AST dump `FlextInfraConfigModels` pós vs `pre_config.json`
   (107/107 dunders) via script do scratch (prova do lane, não mutação).
5. **F0.5** `make check`: loc-cap `_config` zerado; capturar lint fresco → decisão F0.6.
6. **F0.6** Exemption escopada em `config/tooling.yaml` (padrão `_rope`) SE E SOMENTE SE
   lint fresco exigir; F821/erro real → causa raiz antes do commit.
7. **F0.7** Commit escopado (`_models/_config/**`, `_models/__init__.py`, `tooling.yaml`
   se F0.6) → fetch → push FF (tip mexeu → `merge --no-ff` + revalida F0.5).
8. **F0.8** `pytest` escopado nas famílias tocadas (facades públicas, zero mocks);
   `make test` completo se orçamento permitir — senão recorte declarado honestamente.
9. **F0.9** Bead `flext-471ws` evidência por grão + board ALL: tema loc-cap 3/3 pousado.

### F1 — gen×2 + fix idempotentes no workspace (p0 Onda A/B residual)

1. **F1.1** Projeções marker pyproject (api/auth/core) se ainda pendentes: commit em
   lote `chore(pytest): project marker vocabulary` por membro + push FF (padrão tap).
2. **F1.2** dbt-oracle: zona viva do peer — NÃO adotar; só registrar no bead.
3. **F1.3** Quiescência peer (watch 60s ×2) → `make gen` ×2 exit 0 → `make fix` ×2 →
   `make fmt` ×2 (2ª rodada no-op). Corrida: máx 3 ciclos (adotar tip, repetir);
   persistir → registrar em `flext-fkfmu` e seguir para F2 (engine roda sobre gen do
   peer).

### F2 — Engine rope-gen (subsume p0 Onda C; portões explícitos)

1. **F2.W0** Docs/ADRs/beads primeiro: bead feature `discovered-from: flext-5fxu6.4`;
   ADR-014 §"rope-in-gen"; ADR-010 §3b alinhado; runbook dono→responsabilidade +
   taxonomia
   - fluxo findings + retomada.
2. **F2.W1** Adotar WIP `_models/_codegen/` (já pousado em `70dea697b`) e quebrar
   `__init__.py` 51KB residual em facade estrita (`base.py` MRO, sem `_parts/`) — ÚLTIMO
   alvo loc-cap do tema; 4 analisadores verdes no infra antes de estender.
3. **F2.W2** Engine init strict/total (Decisão 3): primitivas `refactor/` +
   `_utilities/rope_*`; contrato `LazyInitPlan` mantido; W002 com escopo da tabela
   (self-import relativo; overlay flext-core exceção declarada; lazy isento).
4. **F2.W3** Loop único por repo: snapshot autenticado → planejar TUDO (pyproject,
   templates, mise, lazy-init, docs) com 1 projeto rope/repo → publicar em lote
   transacional → recibo único (findings+timings) → guards verify-\* fundidos no
   input-CAS. Perf: medição por stage no bead; 1 projeto rope/repo; cache planner; skip
   content-hash.
5. **F2.W4** Resiliência (Decisão 5): teste obrigatório de falha injetada
   mid-publication (gen E fix) com diff vazio pós reverse-apply.
6. **F2.W5** Três níveis + rules-as-data (Decisões 4/6/7): estágio check `gen-warnings`;
   escopos src/tests/scripts/examples; **as regras de extração do p0 Onda C entram AQUI
   como dados** (import container perdido em parts, profundidade relativa pós-move,
   classmethod qualificado na part, fields dropados no split) — um detector, um
   consumidor.
7. **F2.W6** Cobaia cosmos-docgen — **PORTÃO: engine só toca a frota depois daqui ×2
   verde**: engine via CLI em branch própria; W001 provado (warn, não falha); W002→fix;
   receipt idempotente; `gen ×2` exit 0; runtime real (import + CLI); locks NÃO
   convergem aqui.
8. **F2.W7** Convergência `agents/` (`agents_governance`): máximo automatizado; não
   automatizável → bead com evidência, nunca edição manual em massa.

### F3 — Frota: re-projeção + sweeps + centralização (rope-gen W8 + p0 Ondas D/E)

1. **F3.0** Integrar fatias dos subagentes fleet (estado na §1): auditar tree por repo
   (relatório vazio ≠ sem trabalho), validar `make -C <repo> check` por fatia, landar
   escopado (regras do plano fleet: commit por classe + push FF + gitlink bump por
   lote). Cross-repo (ex.: cli depende de `u.Yaml` novo no core): landar core ANTES do
   consumidor no mesmo lote, gitlinks bump juntos. Resume dos FAILED via task_id antes
   de re-dispachar.
2. **F3.1** Re-projeção 32/32 com engine nova: gen na raiz, ponto fixo ×2,
   `fix/fmt/check/test` por fatias; findings custom colhidos e triados com evidência por
   membro.
3. **F3.2** Sweep stubs/fallback/silenciamento (~27 membros restantes): fan-out
   subagentes por cluster (4–6/agente) com findings dos gates; correção na causa raiz
   (`r.Fail`/`e.*` na fronteira), sem `# noqa`; auditoria de lane ≤15 min.
4. **F3.3** `make test` workspace; timeout suíte infra → diagnosticar via
   `validate/_pytest_runner/command.py`, corrigir no dono (`flext-c4k44`);
   `make test PROJECT=<m>` ×2 por membro tocado.
5. **F3.4** Centralização c,t,p,m,u em 3 fatias gen-gated (trace headers →
   `c.Observability`; contexto → `u.Context` extend, apagar ContextVars duplicadas;
   instrumentação → `u.HttpInstrumentation`, observability vira fachada fina). Padrão
   facade estrito nas novas famílias; cada fatia: lane core + lane consumidora + gen
   ×2 + pytest ×2 + bead.

### F4 — Fechamento 0.12.0 (p0 Onda F)

1. **F4.1** Varredura de conclusão: PRs por membro tocado (`merge --admin --merge`
   autorizado, CI verde no SHA merged); branches/worktrees da minha lane removidos;
   lanes abandonadas assumidas ou devolvidas com bead.
2. **F4.2** Landing flext-infra: PR + `merge --admin --merge` em `0.12.0-dev`; gates
   rerun no SHA integrado; runtime provado; gitlinks bump+push.
3. **F4.3** `make release`/tag `0.12.0` SÓ após F0–F3 verdes ×2 + CI do SHA (aceite do
   checkpoint: violações/warnings remanescentes aceitos SE verbos completos em todos os
   ciclos).
4. **F4.4** Beads: fechar `flext-471ws`, `flext-wjozx`, `flext-fkfmu`, `flext-c4k44` com
   4 fontes de evidência; `flext-7pa7o` permanece (sessão dedicada).
5. **F4.5** Docs/ADRs no mesmo ciclo: ADR-014 anotado com regras novas; ADR-016 →
   Accepted quando o épico rodar; plano P1 em `docs/plans/` (baseline 0.13.0).

## 4. Validação / aceite final (checklist duro, unificado)

- [ ] F0: `_config` pousado com paridade 107/107; loc-cap 0 nos 3 alvos; exemptions só
      com lint fresco
- [ ] F0/F1: `make setup/gen/fix/fmt` exit 0 ×2 idempotentes no workspace
- [ ] F2: gen-warnings reportados com evidência; GEN-E001/colisão falham loud;
      resiliência diff vazio (gen E fix)
- [ ] F2.W6: cosmos-docgen ×2 verde antes de qualquer toque na frota
- [ ] F3: `make check` 4 analisadores 0 (ou triagem evidenciada); `make test` workspace
      verde ou timeout documentado
- [ ] F4: PRs merged com CI no SHA; gitlinks bump; tag 0.12.0; beads fechados com
      evidência
- [ ] Nenhum arquivo de peer em commit meu; nenhum rollback/force-push em nenhuma fase

## 5. Riscos / mitigações

- **Peer ativo no mesmo repo**: board + quiescência antes de cada ciclo; input-CAS
  converte corrida mid-run em falha limpa; máx 3 ciclos → adotar e seguir.
- **Gen reescreve outputs de forma divergente do split manual**: gen vence sempre (é o
  escritor); split manual é input de adoção, não autoridade.
- **Falsos verdes na engine**: cada transformação prova 1 caso real da classe ANTES do
  lote; segunda passada no-op (fixpoint) como critério.
- **Timeout de suíte / gates longos**: testmon + xdist; escopo tocado primeiro; abortar
  nunca subir limite.
- **Ferramentas bloqueadas (`bd`, `rg`)**: evidência via make/git/board; bloqueio
  registrado com comando+erro exato.

## 6. Fora de escopo (explícito)

- Épico FlextSettings/FlextConfig (`flext-7pa7o` + ADR-016) — sessão dedicada.
- Validação de consumidores externos (ai-hub/cosmos-main/algar-\*) — pertence ao épico.
- `flext-infra-worktrees/` — lane estrangeira, nunca tocar nem concluir por ela.
- Remoção APPLY/uv.lock/mise.lock; mudanças em `flext_core/lazy.py`; convergência de
  locks das cobaias.
