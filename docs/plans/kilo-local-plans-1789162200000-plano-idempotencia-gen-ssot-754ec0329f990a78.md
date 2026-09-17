# Plano Aprofundado — Idempotência do `make gen/fix/fmt` e Cadeia SSOT → Publicação → Integração

> Aprofamento do plano de retomada (`1789162100000`) aos 21:41Z. Cada causa abaixo foi VIVIDA e provada
> nesta sessão (SHAs, logs de CI, diffs) — não é levantamento teórico.

## 1. O sintoma central (o "treadmill")

Cada rodada de `make gen/fix/fmt` **mudava os projetos toda hora**: 31 membros sujos → 31 PRs → rollup
de gitlinks → tips movem → gen muda de novo → … A frota nunca estabilizava e a integração nunca ficava
verde. O gate `gen-check` do CI funcionava (catching drift real); o RENDERER é que não era função pura.

## 2. Causas-raiz provadas (mapa entrada→efeito)

### CR1 — Render lê o AMBIENTE, não só o SSOT (a causa-mãe)

| Entrada ambiente                              | Efeito observado (evidência)                                                                                                                                                    |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Presença de `.flext-runtime/` no host         | `**/.flext-runtime: true` em `.vscode/.gitignore` só no host; runner renderiza diferente → drift no CI (PR #225)                                                                |
| **Árvore de trabalho** (arquivos WIP do ator) | `compose_per_file_ignores(repository_root)` (conform.py:2824) derivou `"PLC2801","SLF001"` dos arquivos WIP; árvore limpa do runner não → projeção commitada ≠ render do runner |
| Relógio do host                               | `year=time.localtime().tm_year` em `_project_render_context` — input de ambiente no render                                                                                      |
| Resolução de dependências do ambiente         | `--hash=sha256:c5132b4b…` projetado em arquivo auditável (CI PR #225) — hash pertence ao uv.lock                                                                                |

**Lei decorrente:** `render = f(SSOT, templates, PINS)` — e NADA mais. Qualquer leitura de filesystem
fora do repositório git-checkout, relógio, locale, env-var ou estado de árvore não-commitada é defeito.

### CR2 — Estado transacional keyado errado

- Journal/CAS compara **snapshot de conteúdo** sem vincular ao PIN SHA → após rollup de gitlink, snapshot
  stale gera `generation state changed` e "ancestry violations" com SHAs antigos (vivido 3×).
- Lock do journal é **global-host** (`.git/flext-infra-codegen-transaction-journal.json.lock`):
  um `check run` do ai-hub travou o workspace flext por 3h (PID 3888377, 17:53→20:52).

### CR3 — Semânticas de escrita não-canônicas

- Comparador `bytes` vs `str` (corrigido nesta sessão: `codegen_file_plan.py`, 4 regressões).
- Renderer `.vscode` com **merge-semantics** sobre o arquivo existente (`_apply_union_settings`):
  render(arquivo_existente) ≠ render(canônico) → risco de oscilação em vez de substituição de seção gerida.
- Newline final não-determinístico entre renders (diff `\ No newline at end of file` no runner).

### CR4 — Verbos mutadores sem escopo de proveniência

- `make fmt/fix` sobre árvore com WIP alheio: normalizou `qualified_names.py` (arquivo do ator) no meio
  do meu commit de teste — mix de proveniência (vivido na lane infra).

### CR5 — Ausência de superfície canônica de CHEGADA multi-repo

- O gen do umbrella ESCREVE em 31 repos num verbo, mas a publicação até a integração exigia 31 ciclos
  manuais commit→PR→merge (executados 2× nesta sessão: 31/31 e 11/11). O gargalo é estrutural:
  escrita centralizada, publicação dispersa.

## 3. Programa de Idempotência (workstreams com dono e gate)

### WS-A — Pureza de entrada (mata CR1; destrava TUDO)

1. Exclusões `.vscode/.gitignore` vindas EXCLUSIVAMENTE do SSOT (`codegen.yaml`: lista canônica de
   dirs de estado; eliminar descoberta por `iterdir`)
2. Per-file-ignores derivados do **catálogo commitado** (HEAD), nunca da árvore de trabalho
3. `year` do SSOT (campo declarado), eliminando `localtime()`
4. Hash de resolução removido de projeções auditáveis (fica no uv.lock)

- **Gate:** golden-test de idempotência — mesmo SSOT+pin renderiza bytes IDÊNTICOS em (a) host com
  `.flext-runtime`, (b) host limpo, (c) runner CI. `gen ×2` exit 0 nos três ambientes.

### WS-B — Pureza de estado (mata CR2)

1. Journal/CAS grava `pin_sha`; snapshot válido só dentro do mesmo pin; rollup de gitlink invalida limpo
2. Lock nomeado por `repository_root` (hash do caminho no nome do arquivo) — fim do bloqueio cruzado
   flext×ai-hub

- **Gate:** teste de concorrência (gen flext + check ai-hub em paralelo, zero Timeout); teste de
  rollup→gen sem falso "changed during planning".

### WS-C — Pureza de escrita (mata CR3)

1. Seções geridas substituem canonicamente (sem merge com conteúdo pré-existente fora da seção)
2. Normalização de bytes única (newline final, ordenação) no writer atômico

- **Gate:** regressão de fixed-point em fixture com arquivo pré-existente adulterado.

### WS-D — Verbos com escopo (mata CR4)

- `fix`/`fmt` operam sobre o delta do lane (paths do commit) ou exigem árvore limpa; nunca misturam
  proveniência. Registro do que foi tocado por chamada.
- **Gate:** teste — árvore com WIP alheio + fmt escopado → arquivo alheio intocado.

### WS-E — Superfície canônica de chegada (mata CR5)

- Verbo `cascade` no flext-infra: dado o tip novo de um dono (ex.: flext-infra), para cada membro:
  re-resolver pino → render → commit escopado → PR → merge com CI → ancestry-proof → rollup do umbrella.
  Automatiza o padrão provado 31/31; termina o treadmill com um passo declarado e auditável.
- **Gate:** cascade seca (nada a fazer) é no-op exit 0; cascade real executa ponta-a-ponta num membro piloto.

## 4. Cadeia alvo (depois do programa)

```
mudança no dono (ex.: flext-infra)
  → PR com CI (gen-check idempotente × ambientes) → merge --no-ff no tip
  → `cascade`: membros re-pinam → render (função pura: ZERO drift) → PRs → merges
  → umbrella rollup (gitlinks+projeções) → gen ×2 exit 0 (prova de convergência)
  → integração verde ESTÁVEL (segunda rodada de gen = no-op)
```

O passo final é o teste de fogo: **rodar gen de novo e nada mudar** — hoje é exatamente o contrário.

## 5. Ordem de execução e sessões

| Sessão | Workstream                                    | Entrega                             |
| ------ | --------------------------------------------- | ----------------------------------- |
| R1     | WS-A (4 itens) + golden-test tri-ambiente     | gen determinístico; merge #225      |
| R2     | WS-B (journal+lock) + WS-C (escrita canônica) | fim dos falsos drifts e travamentos |
| R3     | WS-D (escopo fix/fmt) + B404                  | verbos seguros; check infra         |
| R4-R6  | loc-cap ×5 (via make mod) + #688 merge        | infra 100% verde                    |
| R7     | WS-E cascade + 31 membros + runtime           | **F2 FECHADA**                      |
| R8+    | F3 crg → F4 piloto/on tipagem → F5 universal  | épico fechado                       |

## 6. Decisões que peço ao operador

1. Aprovar a lei `render = f(SSOT, templates, PINS)` como inegociável (qualquer nova entrada de ambiente = bug P0)
2. Aprovar o verbo `cascade` como superfície canônica de chegada multi-repo
3. Confirmar prioridade WS-A antes do loc-cap (idempotência destrava o resto; loc-cap só ordena o verde)

## ✅ APROVAÇÃO REGISTRADA — 21:44Z de 2026-09-11

O operador aprovou, via pedido formal:

- **"Aprovo WS-A agora"** — execução imediata do WS-A (pureza de entrada + golden-test tri-ambiente; merge #225 quando CI verde)
- **"Confirmo a lei"** — `render = f(SSOT, templates, PINS)` é lei inegociável; entrada de ambiente = P0
- **"Aprovo cascade"** — verbo canônico de chegada multi-repo aprovado (WS-E)
- **"Confirmo a ordem"** — WS-A → WS-B → B404 → loc-cap ×5 → #688 → cascade → F2

Estado da execução WS-A no fechamento desta sessão (21:4xZ):

- Investigação cirúrgica concluída: `external_tool_state_dir` (project_discovery.py:127-153) é
  computação pura de caminho (OK); `transaction_residue` (\_mise_artifacts_state.py:356-383) faz
  `iterdir` do estado (legítimo como diagnóstico de resíduo; PROIBIDO como input de render);
  `compose_per_file_ignores(repository_root)` (conform.py:2824) lê a árvore de trabalho (PROVADO:
  ignores PLC2801/SLF001 só existiam com WIP na árvore) — este é o primeiro alvo do fix;
  `year=time.localtime()` em `_project_render_context` — segundo alvo (mover para SSOT).
- Execução material do WS-A começa na próxima sessão com estes três donos exatos + golden-test
  tri-ambiente como gate. Tracker: criar bead WS-A no bd (sessão atual encerrada com bash
  bloqueado pelo ambiente de permissões; recriar ao reabrir).
