# Épico — FlextSettings/FlextConfig: contrato de singleton, desempenho e SSOT dos clientes

<!-- TOC START -->
- [1. Motivação e evidência viva](#1-motivacao-e-evidencia-viva)
- [2. Escopo](#2-escopo)
- [3. Ondas da sessão dedicada](#3-ondas-da-sessao-dedicada)
- [4. Aceite (checklist)](#4-aceite-checklist)
- [5. Riscos](#5-riscos)
- [6. Relação com o P0 em andamento](#6-relacao-com-o-p0-em-andamento)
<!-- TOC END -->

**Estado:** planejado (2026-09-15) · execução em sessão dedicada · ADR: [ADR-016](../architecture/adr/016-settings-config-singleton-contract.md) · Bead: criado a partir deste documento (ver comentário em `flext-wjozx`).

## 1. Motivação e evidência viva

`FlextSettings`/`FlextConfig` são fundações layer-0 **namespaced, herdadas e
incrementalmente compostas** a cada uso de biblioteca, servidas como singleton
em todos os módulos (incluindo as fachadas `c,t,p,m,u`). A sessão de
2026-09-15 provou um defeito estrutural nesse contrato:

- **Intercepção em `__new__`** (`flext-core/src/flext_core/_settings.py:226-238`):
  com o singleton existente, caminhos de alocação do pydantic recebem o objeto
  cacheado e o re-inicializam in-place. Prova empírica em flext-oracle-wms:
  suíte unit com ordem aleatória falha em 7/8 seeds; ordem determinística
  passa; `tests/unit/test_config_module.py:114` falha com o payload do teste
  anterior (`''` ou `https://example.com`).
- **`clone()` re-valida fora da janela `singleton_disabled()`** — reentra na
  semântica de fábrica na derivação final.
- **Bootstrap por alias** (`settings = FlextXSettings()` em cada membro)
  depende da intercepção para manter identidade com `fetch_global()` —
  semântica implícita e frágil.

## 2. Escopo

| Camada | Repositórios | O que muda |
|---|---|---|
| Dono | `flext-core` | Ciclo de vida do singleton autoritativo (decision 1-3 do ADR-016), cache de resolução de namespaces, `_merge_overrides` sem dump+revalidate por clone |
| Frota | 31 membros `flext-*` | Bootstrap `settings`/`config` via `fetch_global()`, testes de contrato before/after, remoção de hacks de isolamento |
| Externos | `~/ai-hub`, `~/cosmos-main` (apps `cosmos-charts`, `cosmos-gitops`), `~/algar-oud-mig`, `~/algar-oud_mig`, `~/gruponos-*` (quando clonados) | Consumo tipado pela fachada (ADR-015 R1); extinção de resolução local de env/config; prova de import/identidade em runtime nos branches de integração |

## 3. Ondas da sessão dedicada

1. **Diagnóstico por grafos.** `code-review-graph` mapeando todos os sítios de
   construção/alias de settings/config na frota e nos externos; inventário de
   duplicações de resolução (`_resolve_env_file`, leituras de env ad hoc).
2. **Contrato primeiro (no dono).** Testes de contrato em flext-core
   codificando as 4 leis de identidade do ADR-016 (decisão 3) — antes de
   mexer na implementação.
3. **Corte raiz.** Remoção da intercepção de `__new__`; registro explícito em
   `fetch_global`; `clone` integral dentro de `singleton_disabled()`;
   conversão dos bootstraps da frota para `fetch_global()` via projeção
   (`make gen`), nunca edição manual de projeções.
4. **Desempenho com evidência.** cProfile antes/depois nos hot paths
   (clone/override/namespace resolution); cache com invalidação por
   identidade; benchmarks do flext-core como recibo.
5. **Clientes externos.** Por consumidor: fetch do tip de integração →
   merge `--no-ff` → migração para fachada → `make check/test` do próprio
   projeto → prova de runtime (import + identidade) → PR com CI verde no SHA.
6. **Validação de fechamento.** Frota: pytest com seeds aleatórias ≥8
   consecutivos verdes por membro tocado; `make setup/gen/fix/fmt/check` ×2
   idempotentes; ADR-016 → Accepted; beads fechados com as 4 fontes de
   evidência.

## 4. Aceite (checklist)

- [ ] Leis de identidade testadas no flext-core e verdes (antes: reprovam o estado atual).
- [ ] flext-oracle-wms unit verde em ≥8 seeds aleatórias consecutivas.
- [ ] Nenhum sítio de construção de settings/config fora da fachada na frota (detector canônico, não grep).
- [ ] Externos (`ai-hub`, `cosmos-main`, `algar-*`) com runtime comprovado nos branches de integração.
- [ ] Recibos cProfile anexados ao bead; ADR-016 Accepted; docs/skills atualizados no mesmo ciclo.

## 5. Riscos

- **Contrato implícito dependente da intercepção** (identidade
  alias×fetch_global) — mitigado pela onda 1 (mapa completo antes do corte).
- **Externos em branches próprios** — integração por merge `--no-ff`,
  nunca rebase; adjudicação de WIP concorrente com o operador.
- **Janela de migração parcial** — proibida: o corte do dono e a frota
  pousam no mesmo ciclo; externos podem pousar por PR subsequente cada um
  completo em si.

## 6. Relação com o P0 em andamento

O contexto P0 histórico foi registrado em um plano local não versionado; seu
cursor durável é o Gas City Bead correspondente, enquanto este épico permanece
em `flext-7pa7o`. O P0 NÃO depende deste épico: o teste `clone` do
flext-oracle-wms será endurecido
para before/after (contrato verdadeiro, sem congelar estado prévio) dentro do
P0; a máquina do singleton é propriedade deste épico. O P0 não edita
`_settings.py`.
