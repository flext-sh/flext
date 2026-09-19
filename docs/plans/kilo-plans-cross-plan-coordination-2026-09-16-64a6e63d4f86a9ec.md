# Coordenação entre planos e agentes — 2026-09-16

<!-- TOC START -->

- [Planos relacionados](#planos-relacionados)
- [Decisões harmonizadas](#decisoes-harmonizadas)
- [Divisão de trabalho cooperativa](#divisao-de-trabalho-cooperativa)
- [Critérios de aceite de resultados de outros agentes](#criterios-de-aceite-de-resultados-de-outros-agentes)
- [Próximo alinhamento obrigatório](#proximo-alinhamento-obrigatorio)

<!-- TOC END -->

## Planos relacionados

| Plano                                                                    | Papel aceito                                    | Limite                                                |
| ------------------------------------------------------------------------ | ----------------------------------------------- | ----------------------------------------------------- |
| `../1789582669805-flext-infra-ruff-codemod-repair.md`                    | autocrítica fleet-wide e histórico Ruff         | não é estado runtime atual                            |
| `../1789564109553-rope-modernize-execution-plan.md`                      | evidência histórica de R0, PRs e ondas          | SHAs/contagens exigem reread                          |
| `../1789565900000-wip-hier-refactor.md`                                  | produto separado para o operador de frota       | seu refactor não bloqueia flext-infra                 |
| `~/flext/.kilo/plans/1789582508056-flext-infra-runtime-modernization.md` | plano cooperativo do checkout principal         | contém WIP `_lazy_analysis` que não existe nesta lane |
| `~/flext/.kilo/plans/2026-09-16-flext-infra-continuation-plan.md`        | inventário detalhado de Beads, testes e conform | evidência histórica, revalidar no tip                 |

## Decisões harmonizadas

1. Runtime e Make são autoridade; CRG/testes orientam, não aprovam.
2. Gas City Beads é o único tracker; planos/adendos são handoff/proveniência.
3. `setup → gen x2 → mod x2 → gen x2 se mod mudou owner → fix x2 → fmt x2 → check → test`
   `→ build`.
4. Centralizar `c/t/p/m/u/config/settings` antes de decompor god modules.
5. Facade alvo: `_<module>/`, classes coesas, `base.py` MRO, facade pública fina,
   `__init__.py` gerado, sem `_part`/shim/dual path.
6. Absorção do tip na lane é fix-forward; entrega da lane na integração é PR com merge
   commit `--no-ff`.
7. Longos em processo rastreado; análise de logs delegada; nenhum output truncado vira
   evidência.

## Divisão de trabalho cooperativa

- **Coordenador desta lane:** plano, conflitos, qualidade de aceite e estado
  consolidado; não implementa.
- **Checkout principal:** adjudicar/corrigir o WIP `_lazy_analysis` e publicar uma
  contribuição íntegra ou descartá-la antes da absorção.
- **Worker setup/runtime:** primeiro gate atual e owner de provisioning.
- **Worker conform/codegen:** ProjectNew, lazy-init, journal e fixed point.
- **Worker testes:** classificar por contrato público, sem alterar produção para salvar
  teste inválido.
- **Worker arquitetura:** somente após baseline verde; centralização e slices MRO/LOC
  pequenos.
- **Revisor independente:** CRG/diff/runtime/Make antes de aceitar cada slice.

## Critérios de aceite de resultados de outros agentes

Um resultado só entra no plano como concluído quando contém:

- tree/repo/branch/SHA exatos;
- Bead autoritativo e intent;
- contribuição real versus tip atual;
- source owner e consumidores;
- comando canônico, cwd, exit e saída decisiva;
- runtime público e gates no candidate SHA;
- commit/push/PR/merge SHA quando aplicável;
- rerun no SHA integrado;
- indicação explícita de trabalho superseded/resíduo.

Self-report “feito”, CRG risk 0, linha presente, teste isolado ou relatório de SHA
antigo não são aceitos como conclusão.

## Próximo alinhamento obrigatório

1. Reler Beads/PRs/branches via `direnv`/Git na abertura da sessão de execução.
2. Adjudicar o WIP `_lazy_analysis` do checkout principal contra nossa lane.
3. Executar `make setup` no tree escolhido; a primeira falha atual define o worker e o
   primeiro slice.
4. Atualizar este adendo e o plano principal somente após cada landing, não a cada
   tentativa intermediária.
