# P0 — Extermínio de stubs/fallback/silenciamento + Conclusão da estabilização 0.12.0 (plano otimizado com finish line)

## Objetivo e ponto de finalização (HARD STOP)

Concluir a estabilização do ciclo 0.12.0-dev pela causa raiz e **PUBLICAR a versão final
nos tips dos projetos afetados**. A sessão termina quando:

1. Todos os gates obrigatórios verdes ×2 consecutivos (idempotência) nos escopos
   afetados: `make setup/gen/fix/fmt` exit 0; `make check` com Ruff/Mypy/Pyright/Pyrefly
   = 0 erros (barra de aceite do operador registrada no handoff: gates custom podem
   ficar vermelhos com evidência explícita); `make test` verde ou com receipt de timeout
   de suíte documentado (defeito conhecido flext-infra, não bloqueia publicação —
   handoff §"Última suíte concluída").
2. Stubs, fallbacks, silenciamento de erros (`except: pass/return None` como lógica,
   `# type: ignore`/`# noqa` sem justificativa, defaults silenciosos,
   try/except-fallback) exterminados nos escopos varridos, comprovados pelos detectores
   `silent-failure`/`smells` do `make check`.
3. PR(s) de entrega merged com `gh --admin --merge` (autorização do operador 2026-09-15)
   **somente com runs de CI reais verdes no SHA merged**.
4. Beads, ADRs, docs, skills e o plano P1 atualizados no mesmo ciclo.
5. Worktrees/branches da minha lane concluídas (merge+push+limpeza); trabalho paralelo
   de outro ator: **fix-forward adopt, nunca concluir por ele** (adjudicação fica com o
   operador).

## Lei de execução (consolidada das diretivas do operador)

- Base **sempre** o tip `origin/0.12.0-dev` (fetch → merge --no-ff se divergiu →
  trabalhar). Nunca rebase/force-push em branch compartilhada.
- Trabalho em **worktree dedicada por lane** (`.worktrees/<lane>` no membro); workspace
  padrão fica nos tips e recebe os merges; push/sync incremental verde direto no tip é
  obrigatório, não opcional.
- Fix-forward adopt: qualquer WIP paralelo (peer agent, aihub pipeline, lanes de
  worktree) é input de propriedade de outro ator — adotar por merge, preservar, nunca
  reset/discard/restore/stash (PROIBIDO).
- Lanes abandonadas do tema podem ser assumidas; propagar para a branch de integração e
  validar em runtime.
- `bd` sempre via `direnv exec .` (padrão Gas City: banco shared `flext`,
  `dolt_mode: server`; NUNCA `bd init` em membros — incidente 2026-09-15 recuperado, ver
  bead `flext-wjozx`).
- Runtime define o contrato; tests validam comportamento+runtime e o PLANEJADO, nunca
  "como é feito" nem internals privados. Tests nunca definem o ambiente. Exterminar
  fake/mock/hardcoded/tautológico/fabricado pela tip e propagar.
- Comandos sempre canônicos (`make setup/gen/fix/fmt/check/test/mod`); OBEDECER o que os
  verbos geram (não o contrário); ferramenta quebrada = defeito no dono (flext-infra),
  consertar e rerodar. Causa raiz para TUDO: warnings, cosméticos e pré-existentes
  incluídos.
- **LOC**: reduzir módulos usando melhor `c,t,p,m,u` (subutilizado — maior alavanca de
  LOC), DRY/SOLID/YAGNI/SSOT; quebrar GOD modules para o padrão Single Class Nested
  flext.
- **Padrão facade obrigatório** (strict, MRO): pasta `_[modulo]/` com `base.py` + partes
  `*.py`; `base.py` só importa/agrega as classes internas
  (`from ._[modulo] import ...`); `make gen` gera `__init__`; a classe fachada importa
  tudo sem mais nenhum conteúdo. Camadas canônicas: settings, config, c,t,p,m,u, base,
  services/, api, cli — junto com protocols e models Pydantic.
- Padrões: reuso máximo `c,t,p,m,u` + namespaces (`r,e,x,h,d,s`); sem compat surface;
  ≤200 LOC/módulo; inglês-only.

## Estado atual (evidência desta sessão — atualizado 2026-09-15T16:1xZ)

| Item                                       | Estado                                                                                                            | Evidência                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `make setup`                               | **VERDE**                                                                                                         | EXIT 0 após remoção das tabelas `[tool.uv.workspace]` vazias em 31 membros (causa raiz do nested-workspace; dono já corrigido em ee9e5e018)                                                                                                                                                                                                                                                                                  |
| Resolução `flext_infra` no .venv workspace | **REPARADO**                                                                                                      | `uv sync --all-packages --reinstall-package flext-infra`; resolve do checkout editável                                                                                                                                                                                                                                                                                                                                       |
| Contrato beads Gas City                    | **RESTAURADO**                                                                                                    | Incidente bd-init (25 tips) recuperado: 24 commits `chore(beads): restore gen-canonical Gas City projection` pousados+pushed; flext-cli já canônico (8cc5a3d2); verificado bd membro→central (flext-fkfmu/flext-wjozx)                                                                                                                                                                                                       |
| `make gen`                                 | **1× EXIT 0 provado; ×2 bloqueado por mutação contínua do peer**                                                  | Gen verde (16:2xZ) publica projeção; pares seguintes falham por escrita concorrente documentada (`atomic source changed` em extract_all.py movido; `published generation identity changed` em \_codegen/**init**) — evidência viva do bead flext-fkfmu. Adotados 3 reparos do WIP do peer (def **all**, services/base.py duplicado, import mm perdido em \_codegen/fix.py). Reprovar ×2 quando o refactor facade dele pousar |
| Adoção da frota                            | **POUSADA + sincronizada**                                                                                        | Superprojeto `0f31d8842e` (pointers) + `f40cc641c3` (docs épico); membros: target-wms `a1f077c`, oracle-wms `1a9b7bb`+`28bf20c` (lane SSOT), 24× beads restore                                                                                                                                                                                                                                                               |
| Extermínio fake/mock/hardcoded (tests)     | **wms-family em progresso**                                                                                       | Auditoria completa (tap: 4 fabricados/4 vácuos/4 tautologias/17 freezes; target: 8 wiring+8 redundâncias; oracle-wms: 12 literais→REMOVIDOS via cross-source `28bf20c`; dbt: limpo). target `a1f077c` (contrato Singer). Agentes background: tap + target lanes                                                                                                                                                              |
| Singleton FlextSettings                    | **Épico dedicado criado**                                                                                         | ADR-016 + `docs/plans/2026-09-15-flext-settings-config-ssot-epic.md` + bead `flext-7pa7o`; P0 NÃO edita `_settings.py`; oracle-wms suite 11/12 seeds verde (seed 8 = maquinaria do épico)                                                                                                                                                                                                                                    |
| Pendências de teste                        | tap-wms (agente rodando), target-wms wiring (agente rodando), flext-infra suite timeout (-15/-9, receipt handoff) | —                                                                                                                                                                                                                                                                                                                                                                                                                            |

## Execução P0 — ondas ordenadas (cada onda: worktree → fazer → validar → merge --no-ff no tip → push → bump superprojeto → bead comment)

### Onda 1 — Convergência de gates no tip (sem novas features)

1. Janela quieta (peer idle) → `make gen` ×2 (exit 0 ambos = idempotência provada). Se o
   peer não idle em ~15min: adotar o output do gen DELE (mesma projeção canônica, mesmo
   código editável) e registrar evidência no bead `flext-fkfmu` — o lock global
   permanece o defeito estrutural, não meu bloqueio.
2. `make fix` ×2, `make fmt` ×2 (idempotentes, exit 0).
3. `make check` — meta: 4 analisadores 0 erros; findings custom → triagem (ver Onda 3),
   nunca `# noqa`/exclusão.

### Onda 2 — Varredura de stubs/fallback/silenciamento (a pedido novo do operador)

1. Mapear por `make check` (gates `silent-failure`, `smells`, `security`) +
   `code-review-graph search` (padrões `except.*pass`, `return None` em except,
   `except Exception` sem re-raise, fallback ternário) + `ast-grep` via `make mod`
   (regras YAML em `flext-infra/rules/`, nunca detector ad-hoc).
2. Fan-out **subagentes por membro** (conjuntos disjuntos; ~4-6 membros/agente): cada
   finding → correção na causa raiz no dono (propagar erro via `r.Fail`/`e.fail_*` na
   fronteira; sem try/except como lógica — lei `flext.no_fallback_ever`).
3. Reuso máximo: substituir lógica local duplicada por `c,t,p,m,u`/namespaces do
   `flext-core` (ex.: parsing→`m.*` presets Pydantic; erros→`e.*`; resultados→`r.*`;
   helpers→`u.*`). Aplicar SOLID/DRY/YAGNI/SSOT/DI/CA: um dono por fato, sem duplicação,
   sem escopo sem consumidor.
4. Validar por membro: `make check PROJECT=<m>` + pytest do membro ×2.

### Onda 3 — Revalidação de tests pendente (wms-family + infra)

1. Subagentes: auditar tap/target/oracle-wms tests por asserções de "como é feito"
   (estrutura interna, ordem de chamada, atributos privados) → reescrever para
   comportamento via fachada pública + runtime (padrão do fix flext-ldap: entrada real →
   resultado público determinístico).
2. flext-infra suite timeout: é defeito de runtime da suíte (receipt `timed_out=true`),
   não de teste — diagnosticar com o runner (`validate/_pytest_runner/command.py`,
   janela ativa do operador) e corrigir no dono; nunca deletar/weakenar cobertura.

### Onda 4 — Conclusão de PRs/branches/worktrees + publicação final

1. Minha lane: merge `--no-ff` final no tip de cada membro tocado; PR por membro tocado
   (título `<scope>: ...`), CI verde no SHA, `gh --admin --merge` (autorizado), bump
   superprojeto, push.
2. Lanes paralelas de outro ator (flext-infra-worktrees/mod-sed-import, PRs #733/#734
   draft): **adopt** se já landaram no tip; senão permanecem do dono — registrar no
   bead, não concluir por eles.
3. Publicação final: tag/release `0.12.0` nos repos afetados conforme ciclo de release
   canônico (`make release` no dono) — somente após gates ×2 + CI merged-SHA verde.
4. Fechar beads: `flext-wjozx` (missão tests), atualizar `flext-fkfmu` (evidência lock),
   `flext-c4k44`/`flext-9oljq` se no escopo; atualizar ADRs/docs/skills afetados no
   MESMO ciclo (regra 14).

### Onda 5 — Plano P1 (orientação otimizada, escrito nesta sessão)

Atualizar `docs/plans/` + este arquivo com: lições (lock global → per-repo keying;
editable stale copy → verificação de resolução no preflight; drift do peer → adotar
cedo), padrão de ondas, e o próximo objetivo do baseline `0.13.0` (ADR-002).

## Riscos e mitigação

- **Peer agent contínuo no workspace**: janelas quietas escassas → adotar output dele
  (mesma projeção canônica); lock global = defeito `flext-fkfmu` documentado com
  evidência viva.
- **Escopo infinito (stubs fleet-wide)**: limitar P0 aos findings dos detectores
  canônicos nos 32 membros; cosméticos sem detector entram em P1.
- **Suite infra timeout**: não bloqueia publicação (barra do operador), receipt
  obrigatório.

## Validação final (checklist de publicação)

- [ ] `make setup/gen/fix/fmt` exit 0 ×2 (workspace)
- [ ] `make check`: Ruff/Mypy/Pyright/Pyrefly 0 erros (custom findings triados com
      evidência)
- [ ] Membros tocados: pytest ×2 verde
- [ ] PRs merged com CI real verde no SHA merged
- [ ] Beads/ADRs/docs/skills/plano P1 atualizados
- [ ] Worktrees da lane limpas; tips pushados; tag 0.12.0 publicada
