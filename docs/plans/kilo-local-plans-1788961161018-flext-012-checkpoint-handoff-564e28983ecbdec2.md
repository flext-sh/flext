# Handoff — Nova Sessão (projeto flext)

<!-- TOC START -->

- [1. Documentos de leitura obrigatória (nesta ordem)](#1-documentos-de-leitura-obrigatoria-nesta-ordem)
- [2. Estado real verificado (leitura read-only, 17:25 UTC)](#2-estado-real-verificado-leitura-read-only-1725-utc)
- [3. Diretriz operacional vigente (supersedência)](#3-diretriz-operacional-vigente-supersedencia)
- [4. Sequência de retomada (exatamente nesta ordem)](#4-sequencia-de-retomada-exatamente-nesta-ordem)
  - [Fase 0 — Publicar o gerador infra PRIMEIRO](#fase-0-publicar-o-gerador-infra-primeiro)
  - [Fase 1 — Integrar tudo na branch de integração](#fase-1-integrar-tudo-na-branch-de-integracao)
  - [Fase 2 — Fechar a lane de release local](#fase-2-fechar-a-lane-de-release-local)
  - [Fase 3 — Versionamento, aceite, publicação e verificação](#fase-3-versionamento-aceite-publicacao-e-verificacao)
  - [Fase 4 — Varredura paralela de reorganização de Beads (ativa)](#fase-4-varredura-paralela-de-reorganizacao-de-beads-ativa)
- [5. Regras de ambiente (não repetir erros)](#5-regras-de-ambiente-nao-repetir-erros)
- [6. Constantes-chave](#6-constantes-chave)
- [7. Regras de parada](#7-regras-de-parada)
- [8. Primeira ação na nova sessão](#8-primeira-acao-na-nova-sessao)

<!-- TOC END -->

> Data: 2026-09-09 17:36 UTC. Projeto: `~/flext`. Este é o handoff consolidado para
> retomar o trabalho em nova sessão, exclusivamente sobre este projeto. Os documentos de
> referência e o estado real já estão atualizados com a diretriz operacional mais
> recente.

## 1. Documentos de leitura obrigatória (nesta ordem)

1. `~/flext/.kilo/plans/1788961161018-flext-012-checkpoint-release.md` — plano de
   execução com handoff detalhado (seção "Session Handoff").
2. `~/flext/.kilo/plans/1788961161018-flext-012-checkpoint-status.md` — realidade
   verificada, classes de evidência, mapa de Beads, blockers.
3. `~/flext/AGENTS.md` — lei raiz do workspace.
4. `~/flext/.agents/skills/flext-law/SKILL.md` — skill branch-matched local.

## 2. Estado real verificado (leitura read-only, 17:25 UTC)

- **Worktree de release:** `~/flext-release-012`, branch `release/checkpoint-0.12.0` @
  `fb8b1dd5f3`. Divergência vs `origin/0.12.0-dev` (`79dcca0880`): 2 ahead / 0 behind
  (não é ancestor).
- **Árvore totalmente suja** (superprojeto + 31 membros). Nada staged.
- **flext-infra:** commit de trabalho `f2f4b526d` (PR #665 pre-landed localmente como
  merge no-ff) está **NÃO PUBLICADO**. Gitlink do superprojeto registra `9114c34627`.
  Gitlink sujo (WIP não commitado). 4 arquivos sujos na infra:
  `.github/workflows/release.yml`, `Makefile`,
  `src/flext_infra/templates/project/base/Makefile.j2`,
  `tests/unit/codegen/test_codegen_make_environment.py`.
- **PRs:** `gh pr list` → **0 PRs abertos** no root (todos MERGED/CLOSED). O bloqueio
  real é o commit `f2f4b526d` não publicado.
- **Beads:** 30+ P0 abertos fleet-wide. Mapa completo no status doc.

## 3. Diretriz operacional vigente (supersedência)

- Zero dívida: nenhum warning/violation aceito como dívida. Todas as correções são na
  causa raiz. Nada fica para depois.
- Realidade > testes. Testes validam o que o sistema faz hoje.
- Comandos canônicos apenas: `make <verb>`. Proibido `PROJECT=`, `WHAT=`,
  `PYTEST_ARGS=`, `ARGS=`, `MATCH=`. Proibido pytest/uv/ruff cru.
- testmon obrigatório em toda execução de teste (nunca full-suite cru).
- Root cause + zero resíduo: código morto removido no mesmo ciclo; consumidores rewired
  para o novo owner antes do antigo morrer; sem shims, aliases, dual-path.
- `rules/class-nesting-mappings.yml` é proibido — substituir por descoberta estrutural
  no gerador canônico (SSOT).
- Camada facade strict: settings → config → c → t → p → m → u → base.py → services/\_.py
  → api.py → cli.py. Reverse imports TYPE_CHECKING-only. Pydantic-2 in/out. Tipagem
  `t.*`/`p.*` apenas. Proibido: `Any`, `object`, `Optional[X]`, contratos
  `dict`/`TypedDict`. CA/DI via `p` protocols no composition root único.
- Fechamento completo OU nada: escopo completo + gates verdes + zero resíduo
  - commit scoped → push → PR → review resolvido → merge no-ff na branch de integração
    declarada → gates rerun no merged SHA → runtime provado no estado integrado →
    release/runtime ativo, cada com evidência própria.

## 4. Sequência de retomada (exatamente nesta ordem)

### Fase 0 — Publicar o gerador infra PRIMEIRO

1. Em `~/flext-release-012/flext-infra`: reconciliar o estado local (HEAD `f2f4b526d`,
   PR #665 pre-landed) com `origin/0.12.0-dev`.
2. `git merge --no-ff origin/0.12.0-dev` se necessário; resolver conflitos preferindo
   funcionalidade mais nova; nunca rebase/force-push em branch compartilhada.
3. Rodar `make fmt/check` no membro para validar o estado.
4. `git add` paths canônicos exatos; commit; `git push`.
5. Atualizar gitlink no superprojeto (`git add flext-infra` path exato; commit; push).
   **Não rodar `make gen` na raiz antes disso.**

### Fase 1 — Integrar tudo na branch de integração

Para cada estado de trabalho sujo (superprojeto + 31 membros):

1. `git merge --no-ff origin/0.12.0-dev` (absorve o trabalho em andamento).
2. Resolver conflitos com funcionalidade mais nova; nunca `ours`/`theirs`.
3. `make gen` → `make gen` → `make gen`.
4. `make gen` (ruff/pyrefly/pyright/mypy/duplication/WAZA).
5. `make test` (testmon canônico por membro).
6. Commit scoped; push; PR; review; `gh pr merge --merge` (no-ff) na integração; gates
   rerun no SHA merged; runtime provado.
7. Fechar o Bead relacionado com evidência (comando, cwd, exit, saída).

### Fase 2 — Fechar a lane de release local

1. `git checkout release/checkpoint-0.12.0`.
2. `git merge --no-ff origin/0.12.0-dev`.
3. `make gen/fmt/fix/check/test` na árvore unificada.
4. Commit scoped; push.
5. Remover worktree e branch local/remota apenas APÓS prova remota confirmada
   (`gh pr view` merged, gates green no SHA integrado).

### Fase 3 — Versionamento, aceite, publicação e verificação

Somente após todos os gates verdes na branch de integração:

1. `make release-plan/version/tag/build`.
2. `make publication INDEX=Y` (trusted publishing; `id-token: write` +
   `environment: pypi-public` em `release.yml.j2`).
3. Verificação de clean-install do PyPI em ambiente limpo.
4. Fechar Beads de aceite (`flext-y3qpq.5`, `flext-y3qpq.6`, `flext-1wjg1.11`,
   `flext-1wjg1.12`).

### Fase 4 — Varredura paralela de reorganização de Beads (ativa)

- Task em background: `ses_f78c27510ffeuH2lOb5fIdi2Ht` (skill `beads-organization`), tag
  `reval250909`.
- Snapshot de partida: `~/flext/beads-reval250909.json`.
- CSV de controle incremental: `~/flext/beads-reval250909.csv`.
- Regras: dedup gate primeiro (`bd find-duplicates`; >0.5 → mantém o mais recente, fecha
  o antigo com `SUPERSEDED:`); epic por epic sem pressa; bugs/hotfixes fora de epics
  (hotfix só P0/P1); órfãos re-parentados; CSV atualizado após cada mutação; retomada
  incremental.
- Na retomada: ler o CSV para ver o último ponto; continuar de lá se a varredura
  anterior não terminou; não duplicar trabalho.

## 5. Regras de ambiente (não repetir erros)

- `uv run --project` sem `--no-sync` resincroniza o venv compartilhado entre os
  conjuntos default/all-packages e REMOVE dependências de runtime
  (flask/fastapi/starlette/uvicorn/já desapareceram uma vez). Use `--no-sync` ou o gate
  canônico do membro.
- Pipe para `tail` descarta o exit code do Make. Sempre capture a saída integral e o
  exit real.
- Nenhum teste roda fora do testmon. Full-suite cru é proibido.
- Não rodar `make gen` na raiz enquanto o tip infra não estiver publicado.
- Não editem files AUTO-GENERATED (`__init__.py`, facet roots, `[MANAGED]`). Mudem o
  gerador/SSOT e rodem `make gen`, provando ponto fixo.
- `git add` por paths explícitos apenas. Fix-forward apenas; nunca
  reset/checkout/restore/clean/stash em trabalho compartilhado.

## 6. Constantes-chave

| Item                       | Valor                             |
| -------------------------- | --------------------------------- |
| Base de integração         | `origin/0.12.0-dev`               |
| Worktree de release        | `~/flext-release-012`             |
| Branch de release          | `release/checkpoint-0.12.0`       |
| HEAD infra (não publicado) | `f2f4b526d` (PR #665)             |
| Flag de mutação            |                                   |
| Flag de publicação         | `INDEX=Y` (env, não seletor Make) |
| Tag de reorganização Beads | `reval250909`                     |
| CSV de retomada Beads      | `~/flext/beads-reval250909.csv`   |
| Snapshot Beads             | `~/flext/beads-reval250909.json`  |

## 7. Regras de parada

Pare apenas para: conflito real de autoridade, ação genuinamente destrutiva, ou
exigência de decisão do operador. Formule a pergunta de forma precisa e única; caso
contrário, continue até a conclusão completa.

## 8. Primeira ação na nova sessão

1. Ler os dois docs do plano (seção 1 acima).
2. `bd ready --json` + `bd show flext-1wjg1 --json` para confirmar Beads.
3. Verificar se `flext-infra f2f4b526d` já está publicado:
   `git branch -r --contains f2f4b526d` dentro de `~/flext-release-012/flext-infra`.
4. Se não publicado: executar Fase 0. Se publicado: pular direto para Fase 1.
5. Nunca pular o CSV de reorganização Beads se a varredura paralela não terminou —
   retomar de onde parou.
