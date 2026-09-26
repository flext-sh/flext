# Runbook de estabilização — checkpoint 0.12.0

<!-- TOC START -->

- [(a) Ciclo canônico](#a-ciclo-canonico)
- [(b) Contrato beads central](#b-contrato-beads-central)
- [(c) Integração](#c-integracao)
- [(d) Extermínios vigentes](#d-exterminios-vigentes)
- [(e) Checkpoint 2026-09-20 — motor, cli floor e frota (flext-v4fmn)](#e-checkpoint-2026-09-20-motor-cli-floor-e-frota-flext-v4fmn)
- [(f) Checkpoint 2026-09-21 — extermínio do budget SSOT, auditoria do tracker e campanha de integração](#f-checkpoint-2026-09-21-exterminio-do-budget-ssot-auditoria-do-tracker-e-campanha-de-integracao)

<!-- TOC END -->

> **Status (2026-09-20):** `make gen` atinge ponto fixo verde na frota (32/32; fixes
> pousados: 31 manifestos de identidade `config/workspace.yaml`, render bare-deps no
> root workspace, journal recovery #780, exports lazy `d/e/h/r/x` restaurados na raiz do
> flext-infra). A estabilidade global ainda não está comprovada: restam a campanha
> namespace (~2600 achados NS-STRUCT/NS-IMPORT — rota decidida: regras ast-grep para as
> classes mecânicas em `flext-infra/codemod/rules/` + ondas manuais por repo para as
> estruturais), runtime-census 1/repo (ENFORCE-079 + `extra="forbid"`), e os findings do
> código novo no flext-infra. `flext-uno8m` detém o mapa por repo; `flext-itpd1.3`
> coordena a recuperação sob `flext-itpd1`; os workstreams irmãos `flext-itpd1.2`
> (documentação) e `flext-itpd1.4` (maquinaria Make) mantêm seus escopos. Beads detém o
> estado vivo; este documento mantém o contrato versionado. Planos locais são contexto
> de sessão: sua utilização aprovada não autoriza cópia ou publicação, nem seleção
> automática pelo nome mais recente.

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

**Prioridade máxima: a branch de trabalho acompanha a integração atual.** Cada
incremento precisa entregar comportamento funcional e manter verdes a raiz, os 31
membros e o ambiente compartilhado. Preservar WIP significa adotar e corrigir seus
defeitos; nenhuma falha é aceita como preexistente ou escondida por exclusões.

Antes de iniciar um incremento e antes de publicá-lo, atualizar as referências remotas e
absorver `origin/0.12.0-dev` por merge `--no-ff`, resolvendo cada conflito com revisão
das funcionalidades de ambos os lados. Mudança na base invalida os recibos afetados. Não
acumular funcionalidades em uma branch distante da integração.

O coordenador executa obrigatoriamente a integração de cada incremento: implementação
completa, gates locais da frota, runtime real, CI do candidato exato, merge e prova
pós-merge. Só começa o incremento seguinte depois dessa composição estar verde. Uma
autorização administrativa substitui apenas a aprovação independente; mantém todos os
gates. Enquanto o runtime do tracker estiver suspenso, não criar outro tracker nem
declarar encerramento de fase.

Para mudanças entre repositórios, ordenar os commits pelo contrato entre produtores e
consumidores e validar cada composição intermediária antes de pousá-la. Não contar com
merges simultâneos. Publicar os commits dos membros antes dos gitlinks da raiz;
comprovar a composição final também no SHA integrado publicado.

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

- **Motor codegen**: conform execute compõe `FlextInfraCodegenConformPlan` + roles
  mixin; `misc.py` adia o import de `execute` para `TYPE_CHECKING` (quebra do ciclo
  execute→plan→misc→execute); cleanup do estado `.state` tolera residentes persistentes
  (lock do lease + receipts do lazy-init); import direto de `FlextInfraConfigModels` em
  `workspace.py`.
- **cli**: floor `click>=8.3.3,<8.4` restaurado (cap do meltano; fontes: codegen SSOT +
  projeção + `constraint-dependencies` da raiz quando aplicável).
- **Frota**: 27 membros com renders convergidos e pousados; `setup`/`gen`
  fixpoint/`fix`/`fmt` verdes em toda a frota; payload do flext-tests aceita
  `GenericAlias`/`UnionType`/`TypeAliasType` como átomos textuais.
- **Pendente (rastreado)**: onda estrutural namespace/census (regras ast-grep via
  `make mod`, pós-integração — bead `flext-1tcsp`); daemon fantasma do ai-hub
  (`aihub-yr5ft`); split do services package do ai-hub (`aihub-30jaq`).

## (f) Checkpoint 2026-09-21 — budget SSOT, auditoria do tracker, integração

Estado verificado na sessão de 2026-09-21 (evidência: epic `flext-49quw`, artefatos
`.beads/artifacts/reval260921/`, ledger CSV):

- **Zumbi do budget SSOT exterminado**: o merge `2d2a5b8ba` havia ressuscitado o bloco
  `budget:` do `config/codegen.yaml` que o cutover `265346e77` havia morto
  (modelo+YAML+template). Remoção pousada via `5bb83e45c`; modelo segue sem
  `CodegenGateBudgetSpec` no tip `34765a1ee` — NÃO ressuscitar sem ordem explícita do
  operador (lei universal; a mensagem de `5bb83e45c` declara intenção contrária e
  permanece rejeitada).
- **Shim `_models/codegen.py` restaurado**: a migração para o pacote `_codegen/` estava
  completa (shim de 7 linhas reexportando `FlextInfraCodegen`); o monolito pré-migração
  (`FlextInfraModelsCodegen`, 36 classes duplicadas) voltou pela mesma merge e foi
  devolvido ao estado-fim da migração.
- **Guardas de stems não-importáveis**: `02_api_usage.py` (tem `__all__`) provou falsa a
  suposição "numbered script publishes nothing"; `isidentifier()` nos dois pontos de
  injeção do lazy-init planner (`_lazy_init_planner_aliases.py`,
  `_lazy_init_planner_exports.py`), pousado em `34765a1ee`. Gen do flext-web verde.
- **Auditoria do tracker (`reval260921`)**: baseline 3.470 entidades / 473 ativas; gates
  de abertura: graph limpo, 0 duplicatas (scan unbounded), 6 órfãos de branch, 3 deps
  cross-tracker. Lote 1: 4 claims estagnados → open, `flext-co1th` SUPERSEDED por
  `flext-cu85s`. Lote 2 (F3): `flext-czzns` e `flext-v1xzd` DONE com ancestralidade
  provada; relinks yirgp/cyplp/pwmej; `flext-38p39` em hold (prova de arms pendente).
  Órfãos 6→4. Ondas de análise read-only: C1 completa; A/B1/B2 refazer (rate limit);
  C2/D em curso.
- **Higiene Dolt**: branch `list` (criada acidentalmente por agente) dropada com prova
  de hash idêntico ao `main`. Topologia documentada pelo operador: branch de integração
  `0.12.0-dev` é a linha real; `main` do DB é propagação futura de produção.
- **Campanha de integração**: 15 PRs abertos mapeados via compare API — apenas root
  `#257` é pure-ahead com conteúdo vivo (21 patches únicos, prova de cherry 0 na base);
  CI falha no "gen fixed point" por árvore pós-gen suja → requer commit de convergência
  antes do merge no-ff. Demais 14 divergidos (atrás 5–180 commits); residue-PRs de hoje
  (#786/#787/#182) são de lanes ativas. Ladder protegido (fix→fmt→gen→check→test) com
  `SELECTED_PROJECTS` e guarda anti-colisão na flext-infra em execução.
