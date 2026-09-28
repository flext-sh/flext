# Baseline reconciliado e contrato de aceite

<!-- TOC START -->

- [Verdade atual](#verdade-atual)
- [Primeiro pacote de delegação](#primeiro-pacote-de-delegacao)
- [Matriz de aceite de resultado de worker](#matriz-de-aceite-de-resultado-de-worker)

<!-- TOC END -->

## Verdade atual

- Não há baseline global verde aceito.
- O checkout raiz ainda contém o defeito `_lazy_analysis` em
  `flext-infra/src/flext_infra/codegen/_conform/execute.py`.
- A lane envrc provou um recorte funcional, não o produto inteiro.
- Resultados vermelhos recentes vieram de revisões diferentes: 914 findings de check;
  129→6 falhas no conform da lane envrc; 58F+13E em seleção pós-merge; 79 Pyrefly errors
  reportados. O próximo baseline substitui esses números com uma execução única no mesmo
  SHA.
- `config.py` (~3342 LOC) e `conform.py` (~2996 LOC) permanecem god modules no root.

## Primeiro pacote de delegação

1. **Baseline worker:** escolher tip/checkpoint, atualizar CRG e inventariar WIP/PRs.
2. **Conform worker:** eleger um único `CodegenPhaseAnalysis` filtrado e usá-lo em
   append, commit e receipt validation; provar APPLY/CHECK/abort/fixed point.
3. **Setup/gen QA:** `make setup`; `make gen` ×2 serializado; segunda passagem no-op.
4. **Gate worker:** fix/fmt/check/test/build no mesmo SHA; devolver clusters, não
   corrigir fora do Bead.
5. **Coordinator review:** aceitar a fatia somente com runtime, logs, SHA e Gas City.

## Matriz de aceite de resultado de worker

- [ ] Branch/worktree parte da tip declarada e não carrega WIP estranho.
- [ ] CRG atualizado no SHA (`head_matches_build=true`).
- [ ] Bead Gas City claimado e atualizado; nenhum banco local alternativo.
- [ ] Mudança no owner canônico; projeções regeneradas, não editadas.
- [ ] Runtime público exercitado antes dos testes.
- [ ] `make gen/fix/fmt` duas vezes; segunda passagem sem mutação.
- [ ] Ruff, Pyrefly, Pyright, Mypy, testes e build aplicáveis verdes.
- [ ] Sem mocks/fakes/privados/hardcodes novos; testes por interface pública.
- [ ] Diff reduz LOC/duplicação ou justifica aumento por contrato novo.
- [ ] Commit escopado, PR/merge autorizado, gates repetidos no SHA integrado.
- [ ] Bead atualizado com cwd, comando, exit, saída decisiva, SHA e runtime.

Resultado que não cumpre todos os itens volta ao worker; não é “quase pronto”.
