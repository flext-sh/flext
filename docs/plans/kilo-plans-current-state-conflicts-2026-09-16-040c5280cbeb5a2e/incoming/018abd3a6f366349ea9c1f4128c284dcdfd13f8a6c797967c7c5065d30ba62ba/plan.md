# Estado atual e matriz de conflitos — 2026-09-16

## Trees distintos

| Tree                                            | Estado confirmado                                                                 | Uso                                                       |
| ----------------------------------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `/home/marlonsc/flext-worktrees/rope-modernize` | super `89fc309633`; gitlink infra `96c52f1d6`; checkout infra `d83ccc616` com WIP | lane deste plano; checkout não equivale ao gitlink aceito |
| `/home/marlonsc/flext`                          | integração + WIP concorrente em `flext-infra`                                     | comparação/adjudicação, não copiar cegamente              |

## Claims Claude versus source atual

| Claim histórico                                    | Source atual da lane                                                          | Decisão                            |
| -------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------- |
| `modernizer.py` convertido para `u.validate_value` | adapters/model validation em `try/except c.ValidationError`; bindings existem | superseded; não reaplicar sem gate |
| `rewritten` ausente em release metadata            | `rewritten` está presente e consumido                                         | resolvido no tip                   |
| RET503/F841 em Mise state                          | retorno do model validado ocorre dentro do `try`; compensation no `except`    | resolvido/superseded               |
| suppression SLF001 em `_conform_gitignore`         | suppression ausente; mixin contém implementação completa                      | mudança Claude não aceita          |
| BLE001 é intencional                               | comentários registram agregação de falhas como violations                     | pendente de CLI/gate Ruff atual    |
| modernizer sem cobertura                           | CRG atual liga 19 testes à classe                                             | claim inválido                     |
| tudo implementado                                  | nenhum ciclo Make/runtime foi executado na sessão final                       | rejeitado                          |

## Conflito com o checkout principal

O plano cooperativo `/home/marlonsc/flext/.kilo/plans/1789582508056-flext-infra-runtime-modernization.md`
identificou no WIP do checkout principal:

- `_lazy_analysis` criado com files filtrados;
- `append_phase_locked()` recebendo outros dados;
- `_validate_managed_fixed_point()` referenciando `_lazy_analysis` fora de escopo.

Leitura direta confirma esse defeito em
`/home/marlonsc/flext/flext-infra/src/flext_infra/codegen/_conform/execute.py`.
Porém, o mesmo defeito **não existe** em
`rope-modernize/flext-infra@469b26b4e0`. Esse fato permanece histórico. O
checkout atual avançou para `d83ccc616` e contém WIP em
`_models/config.py` e `codegen/conform.py`; portanto a adjudicação deve ser
refeita antes de absorção ou landing.

### Resolução

1. Não editar nossa lane para “corrigir” um bug que só existe no WIP paralelo.
2. Antes de absorver a integração/WIP principal, comparar a contribuição real:
   intenção de excluir paths lazy já owned por conform versus implementação
   quebrada.
3. Se a exclusão é necessária, reimplementar atomicamente no owner de
   transaction plan, passando um único `CodegenPhaseAnalysis` filtrado ao
   append, journal e fixed-point validation.
4. Validar ProjectNew → conform → lazy-init pelo runtime e `make gen` x2 antes
   de aceitar o merge.

## Estado das fases do plano principal

| Fase                          | Estado atual                    | Evidência/decisão                                                                                         |
| ----------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 0 — Beads/tips/inventário     | ativo                           | Bead `flext-3rld2` criado/reivindicado via direnv; gitlink e checkout infra divergem e exigem adjudicação |
| 1 — setup                     | sem prova atual                 | executar no SHA atual; históricos não contam                                                              |
| 2 — mod/gen                   | parcial histórico               | gen x2 foi verde em SHA antigo; mod x2 não provado; rerun obrigatório                                     |
| 3 — modernização arquitetural | não iniciada de forma integrada | 60+ nós ≥200 LOC; nenhum slice MRO atual pousado por este plano                                           |
| 4 — ciclo corretivo           | não iniciado no SHA atual       | sem setup/gen/fix/fmt/check/test completo atual                                                           |
| 5 — testes                    | inventário parcial              | clusters históricos e auditorias; decisões remove/rewrite exigem runtime                                  |
| 6 — check                     | sem baseline atual              | contagens antigas de census/duplication são históricas                                                    |
| 7 — landing                   | parcial histórico               | PRs/merges antigos precisam reconciliar com tips atuais                                                   |

## Risco estrutural atual

O CRG de `flext-infra` lista pelo menos 60 nós ≥200 linhas. Prioridades por
tamanho não substituem causalidade de gate:

- `_models/config.py`: 3.343 linhas;
- `codegen/conform.py`: 2.990;
- `_utilities/_rope/source.py`: 1.123;
- `codegen/codegen_transaction.py`: 1.022;
- `_utilities/pyproject_conform.py`: 1.012.

O primeiro slice estrutural será o owner alcançado pela primeira falha runtime
atual, depois de centralizar `c/t/p/m/u/config/settings`.
