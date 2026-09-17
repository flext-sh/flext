# SUPERSEDED by rev5 — .kilo/plans/1789070856000-checkpoint-012-resume-ci-green.md (Checkpoint 0.12.0 rev5 unified). Do not execute; items absorbed there

# Plano — Zerar as pendências do ciclo Make 0.12.0-dev e pousar na integração sem erros

Motivação do operador: "resolver o conflito e pendências — é culpa e responsabilidade sua";
atualizar as regras canônicas em `~/agents`; integrar tudo em `0.12.0-dev` validado, sem erros.

## Estado atual (evidência)

- Landed e pushado em `origin/0.12.0-dev`: `make` apply-por-default (`APPLY ?= Y`), guard
  `filter-out`, unknown inputs → `$(warning)`, `setup` com `--refresh` local (sem apagar
  `uv.lock`), residue self-heal (`cleanup_scope_residue`), piso click 8.3.3.
  Raiz `fcf2aefb2`, flext-infra `ca15e5c4c`, flext-core `58f24765e` — local == remoto.
- `make gen` verde (2×, 4m40s fixed point); `make setup` verde (281 pacotes).
- Pendências assumidas: gates vermelhos do flext-infra (namespace=1385, loc-cap=5),
  lane rope órfã não commitada, `docs/guides/*.bak` commitados no flext-api,
  4 testes de setup falhando no HEAD base, regras `~/agents` desatualizadas.

## Tarefas (fatias pequenas, cada uma validada antes da próxima)

### T0 — Preflight e congelamento

- Matar qualquer processo zumbi (`ps -ef | grep -E "make gen|codegen conform"`; nada vivo segurando
  `~/flext/.git/flext-infra-codegen-transaction-journal.json.lock`).
- Provar venv sano: `uv run python -c "import click, typer, flext_infra"` e `make setup` green.
- Baseline: `git status --short` nos 32 members + raiz; snapshot dos remanescentes só-por-lane.

### T1 — Limpeza de junk commitado (flext-api e frota)

- Remover `docs/guides/*.md.*.bak` (e quaisquer `*.bak` de crash) que estão COMITADOS nos members.
- Commit por member: `chore: remove committed crash backups from generated docs`; push por member.
- Validação: `make gen` verde pós-limpeza no member tocado; sem `.bak` comitados
  (`git ls-files '*.bak'` limpo na frota).

### T2 — Adjudicação da lane rope órfã (flext-infra)

Só um dos dois desfechos, sem descartar trabalho (fix-forward):

- 2a. Se inventário mostrar WIP coerente (imports resolvem, `codemod/rope_rules/` tem `__init__`,
  testes de fixtures/process_boundary passam): terminar o necessário (associar em `models.py`,
  cli, testes), rodar `make fix` + `make check --gates affected`, e commit+push
  `feat(codemod): adopt rope-rule loader lane`.
- 2b. Se truncado: commitar todo o WIP em branch `wip/rope-codemod-rules` e push dessa branch;
  `0.12.0-dev` fica com árvore limpa; bead registrando a continuação pendENTE (`bd create`).
- Validação: `git status --short` em flext-infra vazio após T2; ADR 014 commitado junto.

### T3 — Gates vermelhos do flext-infra (namespace 1385 / loc-cap 5)

- Inventário primeiro (subagente paralelo): rodar
  `flext_infra check run --gates namespace,loc-cap` e agrupar erros por arquivo/regra
  (`[ENFORCE-067]` "2 top-level classes > cap 1", `class_prefix`, loc-cap).
- Correção por arquivo.top (subagentes batelados, 5–8 arquivos por lote):
  - NS-000: absorver classes extras como mixins MRO privados (padrão Flext: `_models`), mantendo
    exatamente uma classe pública por módulo; nunca silenciar o gate.
  - loc-cap: extrair seções de módulo >cap em private facets no mesmo domínio.
  - `class_prefix`: renomear para o prefixo do projeto (`FlextInfra*`, `Re*`), com depara de imports.
- Validação a cada lote: `flext_infra check run --gates namespace,loc-cap --projects .`
  — contagem desce monotonicamente; ao final 0 erros.
- No fim: `make check` completo do flext-infra VERDE (regra do operador: "não pode gerar erros").

### T4 — Testes lentos de setup falhando no HEAD base

- Diagnóstico do porquê (fixtures rodam bootstrap real de mise; suspeita: rede/probe de mise
  ou stub errado no fixture). Fix no dono (fixture `test_u.Tests` ou template), nunca skip.
- Validação: pytest dos 4 tests alvo verde; suíte fast continua verde (10 passed baseline).

### T5 — Regras canônicas em `~/agents`

Inventário já feito: `~/agents` é git repo (`feat/reval250909-adoption`), `~/.agents` é symlink
para ele; projeção via `make propagate`.

- Atualizar superfícies que owned a lei do Make FLEXT:
  - `skills/framework/flext-development/` e `.claude`-equivalente: verbos rodam sem variável;
    `APPLY` é binário (default apply; token não-Y falha fechada); nunca apagar `uv.lock`.
  - `rules/` que mencionam para flext: alinhar ao novo contrato (zero variável no uso
    diário; = inválido, não read-only).
- Commit+push na branch ativa do repo `agents`; rodar `make propagate` (verb canônico
  do repo agents) para regenerar `CLAUDE.md` etc.; `make check` do repo agents no que couber.
- Validação: grep "obrigatório para verbos flext" só existe em contexto histórico;
  nenhuma instrução contradizendo o guard binário.

### T6 — Pouso final na integração

- Ord fix.face-upup: flext-infra (T2+T3+T4) → members afetados (T1, projeções regeneradas) → raiz
  (gitlinks + qualquer projeção).
- `make gen` (timed) verde 2×; `make check` flext-infra verde; suíte owned de make-environment
  verde; `git ls-remote` local == remote em root + flext-infra + flext-core.
- Relatório final: tempos medidos, SHAs, contagens de gates 0/0, pendências restantes (se houver)
  com bead.

## Ord fix dependencies

T0 → T1 ∥ T2 → T3 (precisa árvore limpa) → T4 ∥ T5 → T6.

## Riscos

- Volume do T3: distribuição desconhecida (diagnóstico anterior foi abortado). a inventário decide
  batching; se erros se concentrarem em 3–5 arquivos (suspeita: `_models/base.py`,
  `gate_contract_errors.py`), um lote resolve a maior parte.
- Lane rope pode ter um ator vivo: T0 congela; se aparecer escritor ativo, aguardar/adotar, nunca
  reverter.
- T4 depende de rede (mise/uv releases): se sem rede, registrar `NOT EXECUTED` no bead e pousar com
  pendência explícita — não verde-falso.

## Fora de escopo

- Refatoração do Makefile do repo `agents` (REQUIRE_APPLY/REJECT_APPLY são lei DELE, não do flext).
- Qualquer nova feature; somente fechar o ciclo existente.
