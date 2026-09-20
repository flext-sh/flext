# Runbook de estabilização — checkpoint 0.12.0

<!-- TOC START -->

- [(a) Ciclo canônico](#a-ciclo-canonico)
- [(b) Contrato beads central](#b-contrato-beads-central)
- [(c) Integração](#c-integracao)
- [(d) Extermínios vigentes](#d-exterminios-vigentes)

<!-- TOC END -->

> **Status (2026-09-20):** `make gen` atinge ponto fixo verde na frota (32/32;
> fixes pousados: 31 manifestos de identidade `config/workspace.yaml`, render
> bare-deps no root workspace, journal recovery #780, exports lazy `d/e/h/r/x`
> restaurados na raiz do flext-infra). A estabilidade global ainda não está
> comprovada: restam a campanha namespace (~2600 achados NS-STRUCT/NS-IMPORT —
> rota decidida: regras ast-grep para as classes mecânicas em
> `flext-infra/codemod/rules/` + ondas manuais por repo para as estruturais),
> runtime-census 1/repo (ENFORCE-079 + `extra="forbid"`), e os findings do
> código novo no flext-infra. `flext-uno8m` detém o mapa por repo;
> `flext-itpd1.3` coordena a recuperação sob `flext-itpd1`; os workstreams
> irmãos `flext-itpd1.2` (documentação) e `flext-itpd1.4` (maquinaria Make)
> mantêm seus escopos. Beads detém o estado vivo; este documento mantém o
> contrato versionado. Planos locais são contexto de sessão: sua utilização
> aprovada não autoriza cópia ou publicação, nem seleção automática pelo nome
> mais recente.

## (a) Ciclo canônico

```bash
make setup
make gen
make mod
make gen
make gen
make fix
make fmt
make check
make test
make build
```

Uma falha → corrigir o dono do verbo; sem inflar timeout; sem remover testmon. Executar
os verbos sem seletores na raiz ativa do workspace. Completar com o runtime público
aplicável e a validação nativa de documentação e links. Comprovar que repetições de
`make gen`, `make fix` e `make fmt` não alteram o candidato e terminam com exit zero;
alterações posteriores invalidam os recibos afetados. Warnings e findings residuais
impedem o fechamento. Não iniciar outro ciclo até comprovar a frota inteira verde nos
SHAs integrados e publicados.

## (b) Contrato beads central

- `bd` roda via `direnv exec <repo> gc bd ...`
- A ativação vem do `.envrc`/`.envrc.local` gerado (AGENTS_GAS_CITY_ROOT + porta da
  publicação da cidade + banco da metadata do rig)
- Reparo de identidade: `gc rig set-endpoint flext --inherit`
- Nunca inicializar banco embedded/porta manual (fonte:
  `flext-infra/docs/guides/execution-context.md`)

## (c) Integração

1. Workers entregam reparos delimitados e evidências; não fazem merge nem fecham Beads.
   O coordenador mantém dependências, decisões de integração e a janela serializada de
   geração, ambiente e gates.
2. Preservar o WIP e revisar commits escopados (paths explícitos, nunca `git add -A`);
   integrar por `merge --no-ff` na branch de integração verificada, esperada
   `0.12.0-dev`, com revisão e CI aplicáveis.
3. Publicar membros antes de atualizar os gitlinks da raiz. Push fast-forward;
   divergência exige absorção por merge e revalidação, nunca rebase ou force-push.
4. Revalidar gates, convergência de geração e runtime no SHA integrado publicado; um
   checkpoint ou teste local não comprova a estabilidade da frota.
5. O coordenador registra no Bead comando, cwd, exit, saída decisiva, SHAs e recibos de
   revisão/CI/runtime; fecha apenas obrigações comprovadamente entregues.

## (d) Extermínios vigentes

`APPLY`, `uv.lock`, `mise.lock`, banco local de beads — leitura/geração também, não só
gitignore.

## (e) Checkpoint 2026-09-20 — motor, cli floor e frota (flext-v4fmn)

Estado verificado pós-ciclo do agente dedicado (evidência: bead `flext-v4fmn`,
`flext-1tcsp`):

- **Motor codegen**: conform execute compõe `FlextInfraCodegenConformPlan` +
  roles mixin; `misc.py` adia o import de `execute` para `TYPE_CHECKING`
  (quebra do ciclo execute→plan→misc→execute); cleanup do estado `.state`
  tolera residentes persistentes (lock do lease + receipts do lazy-init);
  import direto de `FlextInfraConfigModels` em `workspace.py`.
- **cli**: floor `click>=8.3.3,<8.4` restaurado (cap do meltano; fontes:
  codegen SSOT + projeção + `constraint-dependencies` da raiz quando
  aplicável).
- **Frota**: 27 membros com renders convergidos e pousados; `setup`/`gen`
  fixpoint/`fix`/`fmt` verdes em toda a frota; payload do flext-tests aceita
  `GenericAlias`/`UnionType`/`TypeAliasType` como átomos textuais.
- **Pendente (rastreado)**: onda estrutural namespace/census (regras ast-grep
  via `make mod`, pós-integração — bead `flext-1tcsp`); daemon fantasma do
  ai-hub (`aihub-yr5ft`); split do services package do ai-hub
  (`aihub-30jaq`).
