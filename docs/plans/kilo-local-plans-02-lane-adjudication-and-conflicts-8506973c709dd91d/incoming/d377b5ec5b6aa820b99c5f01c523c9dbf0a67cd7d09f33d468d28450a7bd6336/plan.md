# Adjudicação de lanes e conflitos

## Decisões

| Lane/artefato                              | Decisão                      | Motivo                                                                         |
| ------------------------------------------ | ---------------------------- | ------------------------------------------------------------------------------ |
| `surf-hornet` envrc                        | Adotar seletivamente         | Recorte pousado e runtime comprovado; backend local conflita com Gas City-only |
| `feature/rope-modernize`                   | Comparar e absorver por SHA  | Tem commits reportados e graph atualizado; integração/PR não está comprovada   |
| `aeolian-sodalite`, PR #235                | Não mergear em bloco         | PR fechado, 158 atrás, resets/reverts e gates incompletos                      |
| `_config/` split                           | Preservar WIP compatível     | Estrutura parcial útil; cortar duplicata god somente com paridade/runtime      |
| `_conform/` split                          | Preservar e concluir cutover | Família existe, mas god ainda vence MRO e duplica comportamento                |
| per-file ignore de `_conform_gitignore.py` | Reavaliar/remover            | Suppressão não corrige owner e contradiz causa-raiz/zero warnings              |
| CRG dead-code 243 símbolos                 | Não aplicar automaticamente  | Pydantic/config dinâmica produz falsos positivos                               |

## Conflitos que o coordenador resolve antes de delegar

1. **Gas City-only vs backend local/none:** tracker de execução é exclusivamente Gas
   City. O próximo owner decide se `none` é apenas ausência explícita de capability;
   nenhum fallback para outro ledger é permitido.
2. **LOC 200 vs gate 1000:** 1000 é o limite operacional existente; 200 é a lei de
   forma para módulos tocados. Não enfraquecer a lei nem mudar config apenas para
   esconder dívida.
3. **Checkout raiz vs rope-modernize:** escolher um único checkout de integração para
   baseline; comparar SHAs e diffs antes de qualquer edição.
4. **God vs família extraída:** não manter dois owners. Enquanto o god vence MRO, toda
   correção deve concluir o cutover ou alinhar ambos apenas como etapa atômica curta.
5. **Teste vs runtime:** template/CLI real decide; teste obsoleto é corrigido/removido.

## Política de adoção

- Adoção é contribuição real ainda ausente na tip, não merge automático de branch.
- Worker produz mapa commit→paths→Bead→consumer→gate.
- Coordenador rejeita commits mistos, gerados à mão, suppressões ou WIP sem runtime.
- PR/worktree só é encerrado após contribuição integrada ou comprovadamente
  superseded e registrada no Gas City Bead.
