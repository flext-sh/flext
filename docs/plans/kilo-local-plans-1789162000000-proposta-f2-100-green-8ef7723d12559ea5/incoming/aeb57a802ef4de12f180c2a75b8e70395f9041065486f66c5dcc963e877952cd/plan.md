# Proposta — Resolver os bloqueios do F2 até o 100% green (retomada unificada, épico flext-cpzjo)

> Base: evidência coletada em primeira mão na sessão de 2026-09-11 (logs, SHAs, PRs #688/#689/#225,
> runs de CI 34620098915/34635120157/34648317277). Cada item tem causa-raiz provada, não hipótese.

## P1 — Gen-check vermelho por deriva ambiente-dependente (runner × rig)

Causas-raiz já provadas nesta sessão (4 sub-defeitos, 1 já corrigido):

| # | Defeito | Evidência | Reparo proposto (dono) |
|---|---|---|---|
| P1a | Comparador de drift comparava `bytes` vs `str` (sempre "diferente") | log CI: `content equal: mode-only drift` com diff vazio | ✅ JÁ CORRIGIDO (`codegen_file_plan.py` + 4 regressões) |
| P1b | Exclusões `.vscode/.gitignore` derivadas do estado AMBIENTE (presença de `.flext-runtime` no host) em vez do SSOT | diff `**/.flext-runtime: true` aparecendo só no host | Derivar a lista de exclusões 100% do `config/codegen.yaml` (nomes canônicos declarados); nunca `iterdir` do filesystem |
| P1c | Journal transacional keya em snapshot de conteúdo, não no PIN SHA → stale após rollup de gitlink | `generation state changed` falso-positivo pós-rollup | Journal grava `pin_sha` como chave de validade; conteúdo comparado só dentro do mesmo pin |
| P1d | Lock do journal é global-host: `check run` do ai-hub travou o workspace flext por 3h | PID 3888377 (17:53→20:52), `filelock.Timeout` | Lock nomeado por `repository_root` (hash do caminho no nome do arquivo); isolamento flext×ai-hub |
| P1e | Linha `--hash=sha256:c5132b4b…` renderizada no runner difere do host | log CI do PR #225 | Constraints com hash pertencem ao lock (uv.lock), nunca a arquivo gerado auditável; remover a projeção de hash para arquivo de texto ou keyar por pin |

**Validação:** `make gen` ×2 → exit 0 ×2, árvore estável, no rig E no runner (CI do PR #225 verde).

## P2 — loc-cap ×5 (bloqueia TODO pousso; dívida pré-existente ao tip)

Arquivos (LOC code > 1000): `conform.py` 3003 · `_models/config.py` 3665 · `codegen.py` 1124 ·
`tests/unit/codegen/test_codegen_conform.py` 1459 · `rope_analysis.py` 1713.

Proposta: split por famílias em módulos `_parts/` (padrão já usado pelo flext-core), executado com
`make mod` (codemods + Rope), NUNCA hand-edit. Ordem por risco crescente:

1. `codegen.py` (1124) — piloto do método
2. `rope_analysis.py` (1713)
3. `test_codegen_conform.py` (1459) — split por classe de teste
4. `conform.py` (3003) — extrair famílias (plan/render/context/budget) mantendo a facade
5. `_models/config.py` (3665) — mover specs aninhadas para `_parts/` preservando `m.Infra.*` via lazy exports

**Gate por arquivo:** contrato de exports idêntico antes/depois (teste de facade), gates verdes no SHA merged, net-LOC negativo por módulo (≤200).

## P3 — B404 (`_mypy_supervisor` importa subprocess)

Causa-raiz: supervisor executa processo bruto. Reparo pela raiz (não supressão): usar o runner tipado
canônico `u.Cli.run_raw` (já existe e é o dono de execução de processos) — elimina o `import subprocess`
e mantém fail-loud com traceback causal. 1 dia.

## P4 — Dívida de tipagem do umbrella root (224 erros medidos)

`namespace 83 · mypy 51 · pyrefly 48 · pyright 32 · duplication 9 · tier-whitelist 1`.
Ondas gate-a-gate com blast radius via crg (F3): duplication (jscpd) → namespace → pyrefly → pyright →
mypy → tier-whitelist. Cada onda: crg update → impact → make mod → gen ×2 → check → PR sem admin.

## P5 — Cascata per-membro automatizada (31 membros × bump de pino + projeções)

Padrão executado 2× manualmente nesta sessão (31/31 + 11/11 MERGED). Proposta: transformar em verbo
canônico no flext-infra (ex.: superfície `cascade`): para cada membro — re-resolver lock para o tip,
render, commit escopado, PR, merge com CI. Elimina a esteira manual e é reuso do que já provamos.

## P6 — Concorrência de atores no workspace compartilhado

Disciplina: trabalho SEMPRE nas lanes dedicadas (`~/flext-work/sweep-p/`), nunca no rig;
locks por-repo (P1d) eliminam o travamento cruzado flext×ai-hub; adoção fix-forward de estado em voo
via PR de absorção com proveniência (padrão #225).

## Ordem de execução (custo crescente, destravando o máximo primeiro)

1. **P1b+P1c+P1d+P1e** (2-3 sessões) → destrava gen verde estável
2. **Render-absorb do PR #225** (1 ciclo, após P1) → CI verde → merge
3. **P3 B404** (1 dia) → `check` do infra só resta loc-cap
4. **P2 loc-cap ×5** (3-5 sessões, make mod) → CI 100% verde no infra
5. **Merge #688 CI-verde** → **P5 cascata** (automatizada) → runtime provado → **F2 FECHADA**
6. **F3 crg** → **P4 ondas de tipagem + F4 piloto** → **F5 propagação universal + tags + épico**

Nenhum merge sem CI verde legítimo (sem --admin). Cada item com bead própria, 4 evidências, gates no SHA merged.
