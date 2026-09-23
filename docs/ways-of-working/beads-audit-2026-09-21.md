# Beads Audit & Reorganization — 0.12 Conformance Campaign

<!-- TOC START -->

- [Estado de execução (2026-09-21)](#estado-de-execucao-2026-09-21)
- [Inventário por família (bd list 2026-09-21, open beads)](#inventario-por-familia-bd-list-2026-09-21-open-beads)
- [Protocolo por item (execução)](#protocolo-por-item-execucao)
- [Fila de execução da auditoria (ordem)](#fila-de-execucao-da-auditoria-ordem)

<!-- TOC END -->

> **Contrato (operador, 2026-09-21):** auditoria item a item de TODAS as beads abertas —
> obsoleta, redundante, reassinar, atualizar estruturalmente ou concluir. Claims
> obsoletos removidos; PRs/branches ligados às beads; tarefas e bugs alinhados aos epics
> corretos; bugfixes/hotfixes fora da hierarquia de epics onde exigido; pods 100%
> superseded podados. Runtime é o critério.

## Estado de execução (2026-09-21)

- Gen fixed point GREEN na frota (32/32, múltiplas provas).
- 31 manifestos de identidade pousados.
- Ondas conformance landed: markdown (root 209→0), silent-failure (~66), census
  ENFORCE-079/042 (~40+21 Config FlextSettings), pyrefly (~40), peer-alias 046 (62
  arquivos), u.Cli ignored_types (flext-cli), exports d/e/h/r/x restaurados, symbol
  recoveries (11).

## Inventário por família (bd list 2026-09-21, open beads)

| Família        | Qtd   | IDs principais                                                                        | Disposição inicial                                                                                                    |
| -------------- | ----- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| facade/lazy    | 17+12 | flext-5fxu6.4.29/30, gy6mx, m4ls9, 3jjja, 4305f, vjj1s, 0in0k.23, tmpm4, m1abc, ssnc7 | Validar contra o estado pós-merge: SymbolRecovery do merge projection-roots pode ter resolvido várias; probe por bead |
| namespace      | 10    | 0in0k.4/.5, z4ydq, 5fxu6.2, 1tcsp, uno8m                                              | Campaña ativa (uno8m é o mapa); as outras convergem nela                                                              |
| hook           | 10    | mvaxv, z7u1g, 1c3mu, cxxha, 64c4s, 5hzi                                               | ai-hub lane (hooks.json render + CRG sweep já feito); coordenar com o dedicado                                        |
| mypy           | 6     | 051n4, 5fxu6.4.16, vaw, o352o, rxg, 0ftd.3                                            | Contidos: minoria; validar pós-042 (Settings MRO pode ter resolvido)                                                  |
| codemod        | 5     | t9q8h, dgd97, pwmej, mu6mp, vjj1s.2                                                   | Validar contra codemod/rules/ atual (35 findings no infra eram do merge)                                              |
| pyrefly        | 5     | osqra, 1x66z, p68a.46.7.x                                                             | 1x66z (\_conform ~64) pode ter caído pós-recuperação de símbolos                                                      |
| journal        | 4     | fkfmu, 3c03u, xldlq, iy2zt                                                            | iy2zt (harvest verb) ABERTO e válido; validar os outros contra o #780                                                 |
| pyright        | 3     | 94d4y, a0edu, 57i4w                                                                   | Contidos                                                                                                              |
| gen fixed      | 2     | t9fay, 6ddeh                                                                          | 6ddeh família .1-.4 já absorvida; validar                                                                             |
| runtime-census | 1     | 0in0k.26                                                                              | Onda executada (21 Config FlextSettings); validar e fechar                                                            |
| silent-failure | 1     | 9eczi                                                                                 | Onda executada (~66 fixes); validar                                                                                   |

## Protocolo por item (execução)

1. `bd show <id>` — ler descrição/notas.
2. Probe de realidade: o sintoma ainda reproduz? (gate/grep/runtime).
3. Decisão: CLOSE-DONE (evidência) | CLOSE-SUPERSEDED (ref da que resolveu) |
   UPDATE+CLAIM | REASSIGN (dono correto) | KEEP (campanha ativa).
4. Registrar a decisão na própria bead; duplicatas → fechar referenciando a canônica.
5. PR/branch traceability: linkar PRs abertos e branches órfãs à bead dona; triagem
   PORT-NOW/LATER/REGENERATE/ABANDON pertence ao dono do flext-infra (pergunta feita no
   canal).
6. Bugfix/Hotfix: type=bug fora de epic hierarchy — hierarchy só para tasks/epics.

## Fila de execução da auditoria (ordem)

1. runtime-census (0in0k.26) + silent-failure (9eczi): fechar com a evidência das ondas.
2. journal family: iy2zt open-válido; fkfmu/3c03u/xldlq → harvest procedure executado
   múltiplas vezes — fechar como superseded se o sintoma não reproduz.
3. facade/lazy family: probe de import por bead (629 módulos importando pós-recovery —
   muitas fecham).
4. mypy/pyrefly/pyright/codemod: contidos — validar pós-próximo check.
5. namespace family: convergir em flext-uno8m (campanha ativa).
6. hook family: ai-hub lane.
