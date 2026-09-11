# Plano 2026-09-10 — Extermínio do supply-chain cooldown + fix do scaffold fixed-point

> Status: EXECUÇÃO. Decisões do operador (2026-09-10): **consertar o scaffold
> antes de pousar**; commitar em `~/agents` apenas o arquivo novo
> `skills/tool/beads-reval/SKILL.md`; PR #238 do mcb **mantida aberta** para
> rebase pós-repin. Pouso autorizado na linha de integração `0.12.0-dev`.

## Contexto

- Ordem do operador: exterminar `exclude-newer` e família (cooldown) de tudo,
  no gerador (flext-infra), valendo para todos os projetos. Fix em projeção de
  consumidor não vale — o problema volta.
- Lane: `/home/marlonsc/flext-work/flext-infra-cooldown-extermination`
  (branch `fix/exterminate-supply-chain-cooldown` de `origin/0.12.0-dev`).
- Bead dono: `flext-fphyv`. Relacionadas: `flext-czzns` (superseded),
  `flext-3cabz` (reds pré-existentes da linha).
- Extermínio já implementado na lane (16 arquivos): models (config.py),
  protocols (base.py), conform.py, pyproject_conform.py (remoção incondicional
  das chaves — padrão gzfd2), templates (pyproject.toml.j2, workspace.yaml.j2,
  Makefile.j2), config/codegen.yaml + codegen-overrides.yaml, testes
  (overlay deletado, 5 arquivos atualizados).
- Evidência já medida: `make gen` exterminou `exclude-newer` do
  pyproject do próprio flext-infra; `make conform` (gen check) VERDE.
- As 26 falhas de teste são **prévias da linha** (provadas idênticas no
  pristine por stash-test; classe documentada em `flext-3cabz`). Delta do
  extermínio: zero falhas novas.

## Diagnóstico do defeito do scaffold (bloqueia o pouso limpo)

Sintoma: `codegen publication did not reach a fixed point: pyproject.toml` —
apply publica o render cru do template (com headers `@flext-generated`);
o verify-planeia desejado conformado (ordenado, sem headers). ~23 testes
`test_codegen_ci_matrix` vermelhos por essa causa.

Suspeitos (conform.py):

1. Guard silencioso: `if workspace is not None and codegen is not None and
   repository is not None` (:1924) pula a conformação do pyproject.
2. Fallback silencioso do taplo: `rendered = formatted.value if
   formatted.success else rendered` (:1948) engole falha de formatação.
3. Divergência de render: verify usa `project_context=None` (:1855), apply usa
   contexto completo (:1606).

## Fases

- **F1 — Diagnóstico dirigido (bounded)**: instrumentar os dois call sites de
  `_compose_project_artifact` (:1605 apply, :1864 verify), despejar o conteúdo
  composto do pyproject em cada um, localizar a primeira divergência.
- **F2 — Fix no dono (conform.py)**: um único caminho de composição pyproject
  para apply e verify; falhar alto no contexto ausente e na falha do taplo
  (extermina os dois normalized-failures). Probe `project_new` → ponto fixo
  SUCCESS antes de seguir.
- **F3 — Gates completos**: `make test` (26 vermelhas devem cair;
  `extended_cli` se persistir = 2º defeito pré-existente → discrimina,
  documenta em bead própria, não bloqueia), `make check`, gen+conform
  verde re-validado.
- **F4 — Pouso flext-infra**: commit único não-WIP (causa raiz na mensagem) →
  push → PR base `0.12.0-dev` → merge (autorizado) → retire da lane após
  `merge-base --is-ancestor` contra origin recém-fetchado.
- **F5 — Beads flext**: `flext-fphyv` DONE (SHA/PR/evidência); `flext-czzns`
  SUPERSEDED (sem cutoff, clamp óbito); `flext-3cabz` atualizada (reds
  corrigidos aqui ou documentados com causa raiz).
- **F6 — Ciclo mcb (pós-merge flext)**: repin `make deps WHAT=upgrade
  DEPENDENCY=flext-infra` (sem cutoff, `filelock>=3.32.6` resolve);
  `make gen` (remoção incondicional extermina `exclude-newer` do mcb)
  - gen check verde; rebase do PR #238 (metade `.beads/*` mantida, metade
  pyproject substituída); gates no escopo; merge develop (ruleset 1 review —
  operador edita/aprova); atualizar mcb-w2xi/uaya, CSV reval250909,
  `bd remember` final.
- **F7 — ~/agents**: commit apenas `skills/tool/beads-reval/SKILL.md` (WIP de
  outros atores intocado).

## Retomada

- Fase atual: **F1** (instrumentação dos call sites).
- Beads: `flext-fphyv` (dono), CSV `.beads/reval250909-tracker.csv` (mcb),
  memórias `bd remember` reval250909-3a-passada.
