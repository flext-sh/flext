# LOC-Cap: pouso do split `_config` e fechamento do tema (reescrita v3, 2026-09-15T17:55Z)

## 0. Autocrítica pesada — atualizada com os fatos mais novos

Autocrítica da sessão (já registrada em `1789476032590`) mantida e AMPLIADA com o que a reescrita anterior também errou:

1. **(herdado)** Reinventei o emitter AST em vez de reencontrar o recipe provado
   (`rope_emit2.py`) — 8 ciclos de bug evitáveis. "Research before mutation" violado.
2. **(herdado)** Gates só depois dos 3 splits: 115 SLF001 + 1 F821 descobertos de uma vez,
   ondas entrelaçadas, impossível atribuir causa.
3. **(herdado)** 40+ min de mutação sem commit → o ator concorrente ADOPTOU meu trabalho
   in-flight (4 commits). Fix-forward funcionou apesar do meu processo.
4. **(herdado)** Bead `flext-471ws` sem evidência nova o turno inteiro; board nunca notificado.
5. **(novo) A onda A ficou INCOMPLETA entre sessões**: `conform.py` e `codegen/__init__.py`
   foram adotados, mas os 6 arquivos `_conform/*` ficaram sujos com drift stale ( whitespace +
   depth pré-`c3f574807`) atravessando o boundary de sessão. Onda pequena que não fechou na
   sessão = onda mal dimensionada.
6. **(novo) O plano anterior sobre-prometeu escopo alheio**: W-E (mocks), W-F (jscpd/dedup),
   W-G (fecho de worktrees) pertencem às Ondas D–F do plano p0-finish do OUTRO ator
   (`1789475880081`). Duplicá-los não ajuda — colide. Lei 23 (realista, batch pequeno)
   violada na "Definição de Done".
7. **(novo) W-B planejou exemption com lint STALE**: os 115 SLF001 + F821 foram medidos
   PRÉ-adoção; após `70dea697b`/`b6926051b`/`c3f574807` a superfície mudou. Decidir
   exemption com dado velho arrisca isentar o que já foi consertado (e é planejamento sem
   pesquisa). Exemption só com lint fresco DA PRÓPRIA sessão.
8. **(novo) Reescrevi sem ler os planas MAIS NOVOS**: `1789489334832-rope-gen-engine-strict-init`
   (engine rope-gen, do outro ator) criado APÓS minha reescrita; o W1 dele quebrará o
   `__init__.py` 51KB residual de `_models/_codegen/` — área do meu tema. Coordenar antes de
   pousar, senão colisão de novo.
9. **(novo) Ferramentas quebradas consumiram turnos** (rg shim NotFound, `bd` bloqueado por
   permissão): plano deve rotear evidência por superfícies que funcionam (`make check`,
   `git diff`, snapshots) e registrar comando+erro exato quando `bd` bloquear (disciplina de
   gate), nunca silenciar.

## 1. Estado de verdade (verificado NESTA sessão, 17:51–17:55Z)

- flext-infra tip: `c3f574807` (`0.12.0-dev`). Landed pelo outro ator: `f5a3bd711` (markers),
  `70dea697b` (split `_codegen` + projeção), `b6926051b`+`c3f574807` (split `_conform` + depth).
- Working tree flext-infra (21 paths sujos, `git status` desta sessão):
  - **6× `M src/flext_infra/codegen/_conform/{base,bootstrap,execute,misc,plan,render}.py`** —
    drift STALE vs tip (diff 2–34 linhas: whitespace de header + profundidade de import
    pré-depth-fix). Cópia local redundante → ADOTAR o tip.
  - **13× `?? src/flext_infra/_models/_config/*.py`** (artifact, base, beads, contexts,
    contract, make, provider, release, render, scaffold, static, templates, workspace) —
    MEU split genuíno, não pousado por ninguém.
  - **`M _config/__init__.py`** (2942→63 linhas, shape lazy-export gerado) e
    **`M _models/__init__.py`** (projeção lazy +12 módulos) — parte do split.
- `_config/__init__.py` já está no shape gerado correto (lazy map, `__all__`, 63 linhas).
- Snapshots de paridade intactos no scratch: `pre/post_{codegen,config,conform}.json`.
- Superprojeto: `M flext-infra` (gitlink atrás) + `m` em vários membros — lanes de outros,
  NÃO tocar. `flext-infra-worktrees/` = lane estrangeira, nunca tocar.
- `bd` bloqueado por permissão nesta sessão (comando negado no ato). `rg` shim quebrado.

## 2. Mapa de propriedade (3 planos vivos, zero sobreposição)

| Plano                             | Dono                               | Escopo                                                                        |
| --------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------- |
| `1789489334832-rope-gen-engine`   | outro ator                         | engine rope-gen; W1 quebra `_codegen/__init__.py` 51KB; W8 re-projeção frota  |
| `1789475880081-p0-finish-rewrite` | outro ator                         | gen×2, `make mod` rules, sweep fleet, centralização c/t/p/m/u, release 0.12.0 |
| **este plano**                    | **esta lane (bead `flext-471ws`)** | **SÓ o pouso do split `_config` + fechamento do tema loc-cap**                |

O tema loc-cap tem 3 alvos; 2 já pousados pelo peer (codegen, conform). Falta 1: `_config`.

## 3. Invariantes (inalteradas + reforçadas)

1. Fix-forward/adopt SEMPRE; `git checkout --` permitido SÓ para descartar MINHA cópia
   local redundante em favor do estado já pousado pelo peer (adoção, não destruição).
2. Base = tip; `git fetch` antes de cada onda; push FF; tip mexeu → `merge --no-ff` + revalida.
3. Superfície canônica apenas: `make setup/gen/fix/fmt/check/test`; nunca ferramenta nua.
4. Gate canônico APÓS cada onda; onda que não couber na sessão NÃO inicia.
5. Janela de quiescência (≤2 min sem mutação nos src do infra) antes de gen/commit; máximo
   3 ciclos de corrida → adotar, registrar, seguir.
6. Commit por paths explícitos; JAMAIS `git add -A`; nunca incluir arquivos do peer.
7. Bead com evidência por grão (comando/exit/SHA); `bd` bloqueado → registrar comando+erro
   exato no board e seguir (nunca silenciar, nunca burlar).

## 4. Ondas (pequenas, gateadas, dimensionadas PARA ESTA sessão)

### W1 — Adotar tip nos 6 paths stale (<3 min)

1. `git fetch` + confirmar tip `c3f574807` (ou mais novo → reavaliar diff antes).
2. `git checkout -- src/flext_infra/codegen/_conform/`
3. `git status`: esperado exatamente 15 paths (13 `??` + `M _config/__init__.py` +
   `M _models/__init__.py`), todos da família `_config`. Qualquer coisa além → parar e
   reclassificar (não é meu → não tocar).

### W2 — Coordenação + quiescência (<5 min)

1. Board post para o lane do peer: vou pousar `_models/_config/**` nos próximos minutos;
   engine rope-gen W1 dele NÃO é afetado (área `_codegen/`), mas seu gen futuro regenerará
   meu `__init__` — meu pouso é o input que ele adota.
2. Watch de mutação nos src (2 min sem mudança) → janela aberta.

### W3 — Pouso do split `_config` (a onda central)

1. `make gen` ×2 (ponto fixo; se o gen reescrever meu `__init__.py` de forma diferente,
   ADOTAR a saída do gen — gen é o único escritor).
2. `make fix` → `make fmt` (idempotentes; 2ª rodada no-op).
3. Sonda de paridade: dump AST de `FlextInfraConfigModels` pós-split vs
   `pre_config.json` do scratch (107/107 dunders) — via script existente do scratch
   (é ferramenta de prova do meu lane, não superfície de mutação do projeto).
4. `make check`: alvo = loc-cap `_config/__init__.py` ZERADO; capturar lint restante real.
5. Commit escopado: `src/flext_infra/_models/_config/**` + `src/flext_infra/_models/__init__.py`
   (+ `config/tooling.yaml` SE W4 aprovar exemption). Mensagem:
   `feat(models): split _config god module into facade family (13 parts + MRO base)`.
6. `git fetch` → push FF. Tip mexeu → `merge --no-ff` do tip, revalidar W3.4, push.

### W4 — Decisão de lint SÓ com evidência fresca (dentro de W3.4)

- Se `make check` reportar SLF001 (ou classe equivalente) nos pacotes internos `_config/**`
  e `_codegen/**` do facade: adicionar linhas escopadas em `config/tooling.yaml` (mesma
  seção/formato do precedente `_rope`), comentário `OPERATOR-AUTHORIZED 2026-09-15` +
  justificativa (padrão facade: acesso `_.` cross-mixin compõe UMA classe MRO; pacote é
  interior privado do facade). Nunca exemption ampla; só path+regra específicos.
- Qualquer F821/erro real: corrigir na causa raiz no meu split ANTES do commit.

### W5 — Testes do escopo tocado

1. `pytest` escopado nas famílias tocadas (models/codegen/conform unit) — comportamento via
   facades públicas, sem mocks (restrição do projeto).
2. `make test` completo se o orçamento da sessão permitir; senão registrar o recorte
   executado como evidência parcial HONESTA (nunca alegar suite completa).

### W6 — Fecho do tema

1. Evidência por grão no bead `flext-471ws` (comando/exit/SHA). `bd` bloqueado → board post
   com o comando+erro exato + evidência no corpo do commit; desbloqueio fica pendente registrado.
2. Board ALL: tema loc-cap fechado (3/3 alvos pousados: codegen `70dea697b`, conform
   `b6926051b`, config `<SHA deste pouso>`); peer pode retomar a engine na árvore limpa.
3. Gitlink `flext-infra` do superprojeto: bump SÓ se nenhum peer estiver mid-sync no
   superprojeto (checar board); senão deixar para a sincronização do plano p0-finish.

## 5. Fora de escopo (explícito, com dono)

- Engine rope-gen, W1–W8 → plano `1789489334832` (peer).
- `_codegen/__init__.py` 51KB residual → rope-gen W1 do peer (é o próximo loc-cap natural).
- Mocks/tests comportamentais fleet, dedup jscpd, centralização c/t/p/m/u, release/tag
  0.12.0 → plano p0-finish Ondas D–F (peer).
- `flext-infra-worktrees/`, lanes `m` dos membros → estrangeiras, intocáveis.
- Épico settings/config (`flext-7pa7o`) → sessão dedicada.

## 6. Validação / Done desta sessão (checklist duro)

- [ ] W1: status limpo exceto família `_config` (15 paths)
- [ ] W3: `make gen` ×2 exit 0; `fix`/`fmt` idempotentes
- [ ] W3: paridade `_config` provada (107/107 dunders vs snapshot pré-split)
- [ ] W3.4: `make check` com loc-cap 0 nos 3 alvos originais do tema
- [ ] W4: exemptions (se houver) escopados por path+regra com autorização registrada
- [ ] W3.5/3.6: commit escopado + push FF (ou merge --no-ff documentado)
- [ ] W5: pytest do escopo tocado verde (recorte declarado honestamente)
- [ ] W6: bead com evidência por grão (ou registro do bloqueio `bd` com comando+erro) + board
- [ ] Nenhum arquivo do peer em nenhum commit meu

## 7. Riscos

- **Peer ativo no mesmo repo**: quiescência ≤2 min + fetch antes de cada commit; corrida →
  merge --no-ff (máx. 3 ciclos, depois registra e segue). A área dele (`_codegen/`) não
  sobrepõe minha (`_config/`); o risco real é gen/check concorrentes no MESMO tree → por isso
  a janela e o board post ANTES de W3.
- **Gen reescreve meu `__init__.py` diferente**: adotar saída do gen (ele é o escritor);
  revalidar paridade pós-gen.
- **Lint novo nos 13 arquivos**: decisão W4 é dentro da sessão, com evidência fresca;
  nada de exemption preemptiva.
- **`bd`/`rg` bloqueados**: evidência roteada por make/git/board; bloqueio registrado com
  comando+erro exato (disciplina de gate), nunca silenciado.
