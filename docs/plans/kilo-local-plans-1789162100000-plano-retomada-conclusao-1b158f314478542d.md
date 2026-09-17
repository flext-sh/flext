# Plano de Retomada — Conclusão da Retomada Unificada (épico flext-cpzjo)

> Retomada do plano `1789132212795-retomada-unificada-sweep-gov-ssnc7.md` aos 21:37Z de 2026-09-11.
> Complementar à proposta `1789162000000-proposta-f2-100-green.md` (causas-raiz provadas).

## Onde estamos (reavaliação com evidência)

| Fase                    | Bead          | Estado              | Evidência                                                                                                                                                 |
| ----------------------- | ------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F0 estrutura+correlação | flext-cpzjo.1 | ✅ CLOSED           | lint 0 ×3 trackers; 322/134/33 com rota                                                                                                                   |
| F1 remote-ização+host   | flext-cpzjo.2 | ✅ CLOSED           | 9 worktrees → PRs → removidas c/ 3 provas; f73ii pousada (#682)                                                                                           |
| F2 fila de pousos       | flext-cpzjo.3 | 🔶 ~60%             | budget resolvido na raiz (36 regressões); #689 MERGED; #688/#225 OPEN; gen exit 0 alcançado 1×; 31+11 absorções membro pousadas; rollups 219-222 pousados |
| F3 crg                  | flext-cpzjo.4 | ⏳ bloqueada por F2 | —                                                                                                                                                         |
| F4 piloto               | flext-cpzjo.5 | ⏳ bloqueada        | —                                                                                                                                                         |
| F5 universal            | flext-cpzjo.6 | ⏳ bloqueada        | —                                                                                                                                                         |

Bloqueios ativos (provados): P1 deriva ambiente-dependente do gen-check (exclusões por filesystem,
journal por conteúdo, lock global-host, hash em projection) · loc-cap ×5 · B404 · 224 erros tipagem root.

## Sessões de retomada (ordem de destravamento)

### SR1 — P1: gen determinístico runner×rig (dona a destravar TUDO)

1. P1b: exclusões `.vscode/.gitignore` derivadas só do SSOT (`config/codegen.yaml` declara nomes; zero `iterdir`)
2. P1c: journal keyado por PIN SHA (validade do snapshot = pin; conteúdo comparado só no mesmo pin)
3. P1d: lock nomeado por `repository_root` (hash do caminho no nome) — fim do travamento cruzado flext×ai-hub
4. P1e: hash de resolução jamais projetado em arquivo auditável (fica no uv.lock)
5. Regressões: fixed-point no host COM e SEM `.flext-runtime`; CI verde no PR #225

- **Gate:** `make gen` ×2 exit 0 no rig E no runner; merge #225 CI-verde (sem admin)

### SR2 — P3 B404 + fecho do check infra

1. `_mypy_supervisor` usa `u.Cli.run_raw` (runner tipado canônico) — elimina `import subprocess` pela raiz
2. Render-absorb final; check infra resta só loc-cap

- **Gate:** `make check` no infra sem B404; PR #688 só vermelho por loc-cap

### SR3-SR5 — P2 loc-cap ×5 (split estrutural via `make mod`)

Ordem: `codegen.py` (piloto) → `rope_analysis.py` → `test_codegen_conform.py` → `conform.py` → `_models/config.py`

- Cada split: crg impact → make mod → gen ×2 → facade-contract test (exports idênticos) → check → PR
- **Gate:** `make check` infra 100% verde → **merge #688 CI-verde** → F2 green

### SR6 — P5 cascata + runtime + FECHO F2

1. Verbo canônico `cascade` no flext-infra (automatiza bump de pino + render + PR por membro — padrão provado 2×)
2. 31 membros cascateados; gitlinks do umbrella re-rollados; gen ×2 exit 0 final
3. Slots restantes F2: detector v3 (ssnc7.1), gates markdown no super (ssnc7.3), slot sweep (rota F4 se ondas 1-2 não verdes)
4. Runtime provado no workspace vivo; beads F2 fechada com 4 evidências

- **Gate:** barra §3.0 completa → **flext-cpzjo.3 CLOSED**

### SR7+ — F3 (crg nos tips) → F4 (ondas do piloto + P4 tipagem root) → F5 (universal + tags + épico)

## Regras fixas (sem exceção)

- Nenhum merge sem CI verde legítimo (zero --admin)
- Trabalho só nas lanes dedicadas `~/flext-work/sweep-p/`; estado em voo do ator = absorção fix-forward via PR com proveniência
- Split/codemod só via `make mod`; projeções só pelo gerador; teste de facade antes/depois de cada split
- Cada unidade: bead + 4 evidências + gates no SHA merged; divergência plano×realidade conserta o PLANO

## Próxima ação imediata (SR1.1)

`flext-infra`: localizar a derivação das exclusões (consumidor de `state_directory_name` no render de
`.vscode/settings.json`/`.gitignore`), mover para leitura do SSOT declarado, regressão com/sem estado
ambiente, PR — destrava o ciclo render-absorb do #225 e todo o resto da fila.
