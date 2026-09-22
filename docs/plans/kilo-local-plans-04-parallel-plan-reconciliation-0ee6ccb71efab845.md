# Reconciliação dos planos paralelos

<!-- TOC START -->

- [Planos considerados](#planos-considerados)
- [Decisões reaproveitadas](#decisoes-reaproveitadas)
- [Material não incorporado](#material-nao-incorporado)
- [Próximos adendos](#proximos-adendos)

<!-- TOC END -->

## Planos considerados

- `../../1789582508056-flext-infra-runtime-modernization.md` — autoridade principal.
- `../../2026-09-16-flext-infra-continuation-plan.md` — detalhes de execução e falhas
  recentes; tratado como adendo, não substituto.
- `../../1789564863139-envrc-beads-tiered-backend-chain.md` — recorte envrc já
  parcialmente implementado/pousado.
- Planos rope-modernize de 2026-09-16 — candidatos de contribuição, dependentes de
  comparação com a tip.

## Decisões reaproveitadas

1. Runtime público antes de testes; testes não definem ambiente.
2. Comandos canônicos Make/CLI; RTK só comprime output.
3. Gerador é único writer; segunda execução obrigatoriamente no-op.
4. Fix-forward adopt; merge `--no-ff` quando a integração divergir; nunca reset,
   restore, stash, rebase ou force-push compartilhado.
5. Centralizar config/settings e `c/t/p/m/u` antes de quebrar god modules.
6. Facade strict: `_<modulo>/`, `base.py` MRO, facade pública vazia, sem `_parts/`.
7. CRG atualizado no SHA; dead-code é pista, não autorização de remoção.
8. Journal/lock por repo/PIN e nenhuma remoção manual como estratégia.
9. Consumer standalone e consumidores reais antes do fechamento de frota.

## Material não incorporado

- Claims de “tudo implementado” sem make/runtime.
- Per-file ignores para encobrir owner incorreto.
- Backend alternativo de Beads sem autorização do operador.
- Refactors baseados em `model_rebuild()`.
- Merge integral da lane aeolian ou de qualquer branch atrás da integração.
- Testes unitários de funções privadas ou de estrutura de implementação.

## Próximos adendos

Adicionar somente quando houver nova evidência integrada: baseline escolhido, resultado
do primeiro ciclo canônico, decisão final do backend envrc e censo de lanes/PRs
encerrado.
