# Handoff — Estabilização mypy/CI + ciclo de integração da frota (2026-09-23)

<!-- TOC START -->

- [1. Missão (diretrizes do operador, mais recente vence)](#1-missao-diretrizes-do-operador-mais-recente-vence)
- [2. Causas raiz encontradas e estado das correções](#2-causas-raiz-encontradas-e-estado-das-correcoes)
- [3. Estado atual no momento do handoff (capturado)](#3-estado-atual-no-momento-do-handoff-capturado)
- [4. Passo a passo de execução (nova sessão)](#4-passo-a-passo-de-execucao-nova-sessao)
- [5. Armadilhas duras (aprendidas nesta sessão)](#5-armadilhas-duras-aprendidas-nesta-sessao)

<!-- TOC END -->

> Documento de continuidade. Esta sessão encerrou no meio do **gen14** (morto por
> disputa de lane); a nova sessão deve retomar do **Estado atual** abaixo e seguir o
> **Passo a passo** na ordem. Não re-fazer o que já está pousado.

## 1. Missão (diretrizes do operador, mais recente vence)

1. `make docs` = ciclo docs-only (generate → fix → fmt → validate → audit) — **entregue
   e provado**.
2. Findings de qualidade do flext-infra = **warning, sem bloquear CI**; nada de brigar
   com gerador/fixer — causa raiz sempre no dono; projeção gerada é canônica.
3. **mypy e pyrefly ficam no CI** (obrigatório, com plugin pydantic); erros corrigidos
   pela causa raiz; tipagem strict e correta, nunca "aberta demais".
4. Sincronizar com tips de integração (0.12.0-dev; não há branches `dev` nos remotes),
   corrigir TODO erro de CI, subir **PR** do trabalho, rodada de merge via PR **no-ff**
   dos subprojetos com contribuição, **green/green**, projeções alinhadas,
   funcionalidade 100%, **e parar**.

## 2. Causas raiz encontradas e estado das correções

| #   | Causa raiz                                                                                                                                                                                                                                                             | Correção                                                                                                                                                                                                        | Estado                                                                                        |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| R1  | **pydantic-settings 2.15.0** (floor bump da toolchain lane) introduziu `_env_prefix_target`; o plugin pydantic/mypy **crasha** (`All arguments must be fully typed`) e, no modo JSON do gate, degrada facades para **Any silenciosamente** (a "cascata" no-any-return) | Hold `pydantic-settings>=2.14.0,<2.15` no SSOT `flext-infra/config/codegen.yaml` (2 entradas) + remoção dos re-exports 2.15-only (`ConfigFileSourceType`, `Traversable`) de `flext-core/_models/pydantic.py`    | **Pousado no tip do infra e do core** (infra 9250a54c8; core 34110f0bf). Venv local em 2.14.2 |
| R2  | **`allow_redefinition` removido** das boolean-settings do mypy (SSOT) — o rebind canônico das facades degradava para Any                                                                                                                                               | Restaurado com racional documentado (`tooling.yaml:314`, commit aa9fd7d53/95e19d42d) + forma strict mro-j47u nos 5 módulos-raiz do infra (alias `_cli_*` + rebind `c: type[FlextInfraConstants] = ...`)         | **Pousado e projetado** (pyprojects raiz+infra+membros com `allow_redefinition = true`)       |
| R3  | **Cache envenenado do mypy** pela era do crash: runs locais oscilavam 0 ↔ 99 findings com config idêntica (o cache reproduzia resultados degradados)                                                                                                                  | Diagnóstico: limpar `.mypy_cache` (raiz e membros) antes de medir. CI sempre roda cache frio → não sofre disso                                                                                                  | Entendido; sem ação permanente necessária                                                     |
| R4  | Dívida pré-existente de tipos no infra (~99 no-any-return em facades m/u compostas) — tornada visível quando o passo **check complement (CI=N make check)** entrou no CI                                                                                               | Postura **warning** por dois mecanismos: `WARNING_GATE_IDS` (constante, 6e964f28c) e `check_policy.warning_gates` no `tooling.yaml` do repositório checado (propriedade da #812). Dívida = bead **flext-1pquc** | Pousado no tip do infra                                                                       |

Investigação concluída: **nenhuma outra variável do mypy foi removida** (diff seccional
ontem→hoje: só o override stale do módulo `dcdoc`, sem relação). O `warn_return_any`
existe desde julho. Os "99" são dívida real + efeito R3; o crash R1 já foi eliminado (0
INTERNAL ERROR com 2.14.2).

## 3. Estado atual no momento do handoff (capturado)

- **Raiz** (`flext`): tip local `55915989e2` ("wip", da lane) — pins de gitlinks **podem
  estar defasados** (ver passo 3). `docs/plans` contém este arquivo (não-commitado).
- **flext-infra**: local == origin tip `ed20f39a0b` (lane estabilizou). Contém R1..R4.
- **flext-core**: checkout local `2fb55f750` ATRASADO do origin tip `3e8c88ac83` (lane
  andou; não é bloqueio — pins usam o tip do remote).
- **flext-cli**: checkout na branch da lane `fix/hold-pydantic-settings-below-215`
  (`d14933f2`, o hold) — **o hold ainda NÃO está no tip 0.12.0-dev do cli**; veículo =
  **PR #190** (bloqueada só por flake externo de mirror apt, ver passo 5b).
- **PR #812** (infra, `fix/lazy-init-deterministic-order`): aberta, mergeable, carrega a
  seção canônica do mypy; CI precisa re-rodar depois que a lane estabilizar (último run
  cancelado por push concorrente).
- **gen14**: **GEN_EXIT=0** (fixed point atingido localmente com o gerador publicado na
  madrugada de 23/09). Membros ficaram com projeções não-commitadas — o próximo passo é
  pousá-las (passo 4). Nenhum erro pendente do gen.
- **Beads**: `flext-ob8gp` (campanha warning-findings) e `flext-1pquc` (dívida de tipos)
  abertos com evidência; `flext-ir0ag` fechado (docs verb).

## 4. Passo a passo de execução (nova sessão)

1. **Quiescência**: confirme que infra/core/cli tips não mudam por ~3 min
   (`git ls-remote origin 0.12.0-dev` repetido). Se uma lane estiver empurrando, espere.
2. **Sync dos checkouts-chave** (sem reset): `git merge origin/0.12.0-dev --no-edit` em
   flext-infra; em flext-core/flext-cli, se o checkout estiver em branch de lane, NÃO
   troque — os pins usam o SHA do remote (passo 4).
3. ~~make gen~~ **JÁ FEITO**: gen14 exit 0 no estado atual (fixed point válido). Apenas
   confirme que `git status` da raiz mostra os membros com projeções pendentes.
4. **Landar**: membros com dirty
   (`git add <paths>; commit "chore(gen): project at the fixed point"; push`) e depois
   **pins da raiz** — usar
   `git update-index --cacheinfo 160000,$(git -C <m> rev-parse origin/0.12.0-dev),<m>`
   por membro (o `git add` de submodule grava o HEAD do checkout, que pode estar em
   branch de lane — já causou órfão "not our ref" no CI), commit e push.
5. **CI green/green**: acompanhe
   `gh run list --repo flext-sh/<r> --workflow CI --branch 0.12.0-dev --limit 1` para
   raiz + membros. Falhas conhecidas e curas:
   - `gen fixed point`: alguém pousou projeção defasada → repetir 3–4.
   - setup `not our ref <sha>`: pin órfão → passo 4 (update-index).
   - `E: Failed ... apt` 404 (libreoffice): flake de mirror do runner — rerun.
6. **PRs (no-ff, CI green antes)**:
   - **PR #190** (cli, hold 2.15): rerun do CI (`gh run rerun <id> --failed`) quando o
     mirror sarar → `gh pr merge 190 --merge` (no-ff). Isso publica a metadata do cli
     com o hold e destrava a resolução do infra em modo versionado.
   - **PR #812** (infra): com o tip absorvido e CI verde → `gh pr merge 812 --merge`.
   - Varra outras branches contributivas: `git branch -r --no-merged origin/0.12.0-dev`
     (ignorar histórico: audit/_, recovery/_, validate/\*, 0.20.0-dev, dolt).
7. **Re-pin final da raiz** (update-index de novo, tips podem ter andado com os merges)
   - push → CI da raiz deve passar do setup E do gen fixed point.
8. **Prova canônica** (nesta ordem, todos exit 0): `make gen` → `make docs` →
   `make check` (warnings permitidos: markdown 61, silent-failure 1, mypy ~99, pyrefly,
   namespace, duplication, tier-whitelist — todos visíveis, nenhum FAIL).
9. **Fechamento**: comentar/fechar `flext-ob8gp` e `flext-1pquc` com as evidências;
   atualizar a memória (`docs-verb-reorg-laws-20260922.md`); **PARAR**.

## 5. Armadilhas duras (aprendidas nesta sessão)

- O journal do codegen vive em `.git/flext-infra-codegen-transaction-journal.json` (não
  no `.state`); estado `prepared/recovering` com árvore ausente já tem cura anti-impasse
  pousada (recovery classifica noop — 17502f121).
- `codegen conform --scope self` **na raiz é inválido** (o lazy-init spana membros);
  usar `make gen` all-scope.
- `make` pode ser SIGKILLado (137) por lanes — simplesmente reexecutar.
- Após `git worktree remove`, o cwd do shell morre — `cd` absoluto antes de git.
- Mimosa bloqueia escrita de código via Bash (usar Write/Edit) e escrita em
  `flext-infra` via paths relativos errados; hooks avisam antes de push sem scan.
- O checkout compartilhado troca de branch sozinho (lanes): **nunca** dar checkout nele;
  usar worktrees destacados para trabalhar em branches.
- Oscilação local 0↔99 findings = cache do mypy (R3): limpar `.mypy_cache` antes de
  concluir qualquer medida.
