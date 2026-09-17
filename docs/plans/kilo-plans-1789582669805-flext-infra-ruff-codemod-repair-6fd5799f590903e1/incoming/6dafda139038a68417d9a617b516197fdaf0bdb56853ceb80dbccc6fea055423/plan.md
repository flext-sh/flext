# Plano fleet-wide: estabilização, modernização e prova runtime FLEXT

## Resultado obrigatório

Entregar a frota FLEXT completa sobre os tips `origin/0.12.0-dev`, com `flext-infra` como único proprietário de setup, geração, conformidade, codemods e gates. O trabalho só termina quando:

- `make setup`, `make gen`, `make mod`, `make fix`, `make fmt`, `make check`, `make test`, `make build` e os verbos aplicáveis de docs/audit passam sem erro, warning, skip oculto, timeout ou resíduo;
- `gen`, `mod`, `fix` e `fmt` atingem no-op na segunda execução;
- um projeto standalone recém-gerado completa o mesmo ciclo e executa sua facade/CLI pública;
- cada slice é integrado por merge commit no tip atual, propagado ao superprojeto e revalidado no SHA integrado;
- Gas City Beads contém o estado, dependências e evidências reais; este arquivo é roteiro, não tracker paralelo.

## Auto-crítica e substituição dos planos anteriores

Os planos anteriores não são executáveis como escritos porque:

1. declararam correções prontas sem prova runtime;
2. usaram snapshots CRG e relatórios antigos como estado atual;
3. trataram Ruff isoladamente, embora o primeiro bloqueio esteja em Gas City/direnv/setup;
4. não reconciliaram tips, WIP concorrente, PRs, branches e beads duplicados;
5. propuseram suppressions, shims e testes de métodos privados onde a lei exige owner único e comportamento público;
6. misturaram edições manuais de projeções geradas com mudanças em seus owners;
7. não ordenaram produtores antes de consumidores;
8. não cobriram a frota completa escolhida pelo operador.

Este plano absorve apenas decisões ainda válidas dos planos `1789564109553`, `1789565900000`, `1789582482542` e da continuação em `~/flext/.kilo/plans/2026-09-16-flext-infra-continuation-plan.md`. O refactor de `wip-hier` permanece um produto separado e não pode bloquear a estabilização FLEXT.

## Adendo de repasse e posição atual

O repasse das sessões Claude paradas, com janela operacional, contribuição
adjudicada, conflitos e matriz fase-a-fase, está no source local
`.kilo/plans/addenda/1789582669805-claude-repass-2026-09-16.md`.
Esse adendo é evidência datada deste plano; Gas City Beads continua sendo o
único tracker executável.

### Avanço confirmado do Claude

- reorganizou parcialmente Beads/docs/ADRs na store Gas City correta;
- publicou a fatia documental `049cc4c00c`;
- iniciou o censo de lanes/PRs/membros e publicou três commits infra pendentes,
  cuja ancestry e validação ainda precisam de releitura live;
- executou `make setup` com exit 0 e 286 packages no checkout principal;
- reproduziu `make gen` vermelho em forward refs de
  `MiseTomlRenderSpec`/`FlextInfraModelsMiseToolchain`;
- provou parcialmente a causa de namespace Pydantic e iniciou reparo em
  `_models/mise_toolchain.py`;
- parou durante essa edição, sem novo `make gen`, commit, push, PR ou gates.

### Efeito na ordem de retomada

O setup verde é histórico e não transfere green para outro SHA. A retomada não
reinicia pela antiga microfatia Ruff: primeiro relê Git/Beads, adota o WIP
íntegro, repete `make setup` no tree escolhido e termina o primeiro produtor
vermelho (`make gen`). Nenhum downstream é aceito antes de `gen ×2`.

## Estado observado que inicia a execução

- Âncoras do snapshot cooperativo de 2026-09-16: super
  `89fc3096335b53d81cdc52afe7cc8c785514bdb2` e `flext-infra`
  `469b26b4e0b336e78548fef1fdcfca347f9c5d53`. Em 2026-09-17, o super
  continua nesse SHA, mas registra o gitlink infra `96c52f1d6`, enquanto o
  checkout infra está em `d83ccc616` com WIP. Este plano é histórico e não
  autoriza reaplicar o snapshot antigo.
- O estado antigo `d1b29223b4`/`96c52f1d6` e suas contagens de ahead/behind foram
  superseded; servem apenas para arqueologia de contribuição.
- Tracker único: Gas City via `direnv exec <rig> gc bd ...`/rota publicada pelo
  rig. `flext-5fxu6.4` permanece candidato ao owner principal; `flext-crd1y` e
  itens journal/testes precisam ser reconciliados, não tratados como nova engine.
- `make setup` ficou verde durante a sessão Claude no checkout principal, mas
  `make gen` permaneceu vermelho; portanto a posição atual é **baseline parcial,
  produtor gen bloqueado**.
- O WIP interrompido em `_models/mise_toolchain.py` não possui prova de sintaxe,
  Pydantic strict resolution ou fixed point. Releitura e repair-forward são
  obrigatórios antes de qualquer absorção.
- O checkout principal também possui uma implementação `_lazy_analysis`
  inconsistente em `_conform/execute.py`; essa implementação não deve ser
  copiada. Preservar somente a intenção one-writer com um único analysis object.
- PRs/lanes históricos (`#247`, `#743`, `#235`, `#681`) e SHAs antigos exigem
  releitura de forge/Git; nenhum status histórico autoriza retirement.
- Relatórios antigos de check/test/runtime census/duplicação continuam úteis
  para investigação, mas não comprovam os SHAs atuais.

## Registro de progresso por fase

| Fase | Estado após repasse Claude | Critério para avançar |
|---|---|---|
| 0 — Gas City e owners | parcial | releitura live e owner único sem beads duplicados |
| 1 — tips/WIP/lanes | parcial | ancestry, PRs e contribuição real confirmados |
| 2 — baseline | setup histórico verde; gen vermelho | setup no tree atual + gen ×2 no-op |
| 3 — produtores | em andamento apenas em geração | forward refs/fixed point verdes, depois journal/mod |
| 4 — modernização infra | não iniciada como slices integrados | primeiro gate atual define owner |
| 5 — check | sem baseline atual | check completo zero findings/warnings |
| 6 — testes | sem suite atual verde | comportamento público, sem timeout/skip |
| 7 — ondas fleet | absorção histórica parcial | cada repo no tip, PR integrado e rerun |
| 8 — runtime | pendente | standalone, workspace e consumidores reais |
| 9 — closeout | pendente | evidência no SHA integrado e trees limpos |

### Retomada imediata, sem repetir trabalho

1. Reler Gas City, Git e forge e anexar ao Bead owner os SHAs/tips atuais.
2. Verificar `049cc4c00c`, os três commits infra e o WIP de `mise_toolchain.py` por ancestry/diff; não repetir contribuição já integrada.
3. Completar ou rejeitar o WIP Pydantic interrompido por source owner e runtime, mantendo zero `model_rebuild` e zero compat shim.
4. Repetir `make setup` no candidate SHA. Se verde, executar `make gen` duas vezes; se vermelho, somente essa primeira falha define o próximo slice.
5. Não iniciar Ruff/test cleanup/LOC waves antes de geração fixa e idempotente.
6. Após cada landing, atualizar o adendo deste plano e Gas City; os demais planos Kilo são cooperação, não substituição desta sequência.

## Decisões de arquitetura e execução

- Fix-forward adopt somente: nunca reset, restore, stash, rebase, force-push ou descarte de WIP.
- Base de todo slice: tip remoto atual da integração; divergência é absorvida por `merge --no-ff`.
- Um bead, um owner, uma branch/worktree, um PR pequeno e independentemente verde.
- Config/settings/templates/generator são SSOT; projeções geradas nunca são editadas manualmente.
- Centralizar `c/t/p/m/u`, config e settings antes de dividir módulos.
- Modelos Pydantic permanecem sem comportamento. Parsing e transformação ficam em `u`, services ou mixins.
- Nenhum shim, dual path, compatibility alias, suppression ou teste privado preserva código antigo.
- O gate operacional de LOC permanece temporariamente em 1000 para não bloquear a recuperação. Todo módulo tocado deve convergir para ≤200 LOC lógicos. Cada módulo existente acima de 200 ganha slice/bead; quando a frota zerar a dívida, o SSOT `loc_cap.max_lines` baixa para 200 e todas as projeções são regeneradas.
- Warning, cosmético, violação preexistente e detection-only finding dentro da frota first-party permanecem vermelhos.
- Third-party forks e content-only repos estão fora da modernização arquitetural FLEXT.

## Sequência de implementação

### 0. Restaurar Gas City e eleger o grafo autoritativo de trabalho

1. Provar conectividade real com `rtk direnv exec <rig> gc bd show flext-5fxu6.4 --json`; a sessão Claude demonstrou a rota Gas City, mas a execução deve reler estado atual.
2. Somente se a leitura real falhar, corrigir o runtime city-owned que publica endpoint/estado Dolt; não criar banco embedded nem pinar host/porta.
3. Atualizar o owner eleito (`flext-5fxu6.4` ou sucessor após reconciliação) com tip, primeiro gate vermelho, stop condition e dependências.
4. Reconciliar, sem criar duplicatas:
   - journal/lock: `flext-dcge0` vs `flext-fkfmu`;
   - testes inválidos: `flext-9m4gc`, `flext-wjozx`, `flext-c4k44`, mantendo `flext-4v4tf` apenas se sua aceitação for distinta;
   - setup/toolchain `flext-5k9r7`;
   - geração `flext-3d8bv`;
   - conform model `flext-bdmdg`;
   - budgets `flext-z4ydq`/`flext-t9q8h`;
   - rules/mod `flext-oquk7`;
   - envrc Gas City `flext-gniuj`.
5. Reconciliar também `flext-crd1y`, criado pela sessão Claude na store correta, contra o épico/owner existente; superseder duplicatas somente após preservar dependências, evidências e contribuição única.

**Saída:** Gas City saudável, um owner por intenção e tracker sem duplicidade material.

### 1. Rebase zero: adotar tips, WIP, lanes e PRs

1. Rodar discovery somente leitura pelo `wip-hier` real e registrar super + 31 membros.
2. Confirmar ancestry das contribuições históricas de `aeolian-sodalite`, `promoted-framework-lift`, PRs `#247/#743/#235/#681` e dos três commits infra publicados pelo Claude; absorver somente contribuição única/correta por merge `--no-ff`.
3. Classificar o WIP live, especialmente `_models/mise_toolchain.py` e `_conform/execute.py`, por owner/intenção. Preservar hunks íntegros, reparar forward e rejeitar implementações fora de escopo; não restaurar snapshots antigos por contagem de arquivos.
4. Mesclar os tips `origin/0.12.0-dev` no super e em cada lane tocada; resolver conflitos por owner, nunca ours/theirs cego.
5. Abrir/atualizar PRs vivos da lane antes da primeira mudança adicional.
6. Atualizar CRG no SHA adotado e registrar build SHA, changed functions, flows, gaps, hubs, bridges, large modules e duplicação.

**Saída:** nenhuma contribuição órfã, nenhuma lane behind e CRG atual no tree executado.

### 2. Capturar baseline real e parar no primeiro produtor vermelho

No root ativo, sempre através de `direnv` e `rtk`, executar e registrar cwd/SHA/exit/saída decisiva:

1. `make setup`;
2. `make gen` duas vezes;
3. `make mod` duas vezes;
4. se `mod` alterar owners/projeções, `make gen` novamente duas vezes;
5. `make fix` duas vezes;
6. `make fmt` duas vezes;
7. `make check`;
8. `make test` e nova execução para provar testmon/no-selection com integridade;
9. `make build`;
10. `make docs` e `make audit` quando declarados.

Falhou um produtor: parar downstream, atualizar o bead owner, corrigir e repetir o mesmo verbo. Não executar ferramenta subjacente diretamente.

### 3. Reparar os produtores antes das violações consumidoras

#### 3.1 Setup/toolchain

- Corrigir identidade provisionada versus invocada de uv/mise/direnv no owner `flext-infra`.
- Exterminar geração/leitura de `uv.lock`, `mise.lock`, `exclude-newer` e banco Beads local.
- Provar `make setup` no root e em standalone real antes de continuar.

#### 3.2 Journal e concorrência de geração

- Eleger um bead journal/lock.
- Journal keyado pelo PIN SHA de cada repo e locks por repositório, nunca lock global host.
- Timeout não remove lock; identificar owner, completar/compensar transação e provar zero resíduo.
- Cobrir begin, publish, recovery e cleanup pela API pública de geração.

#### 3.3 Geração e projeções

- Resolver primeiro a forward ref de `MiseTomlRenderSpec` pela declaração/import graph canônico: classes declaradas em ordem resolvível, sem `model_rebuild`, import circular, comportamento em model ou alias compat.
- Adjudicar o WIP `_lazy_analysis`: um único `CodegenPhaseAnalysis` filtrado deve alimentar append, journal e fixed-point; variável fora de escopo ou dados diferentes entre fases são rejeitados.
- Corrigir o writer canônico que causou drift de `flext-target-oracle-wms/Makefile`.
- `make gen` segunda rodada precisa ser byte-identical em todos os membros.
- ProjectNew → conform → lazy-init deve alcançar o fixed point na primeira geração completa.

#### 3.4 Codemod

- Migrar rules para `config/rules/mod`, `config/rules/ast` e owner Rope conforme SSOT vigente.
- `make mod` deve aplicar cortes mecânicos, rewire semântico, remover owners antigos e terminar com zero actionable e zero detection-only residual.
- Cada regra possui fixture/snapshot e nunca é invocada por ast-grep ad hoc.

### 4. Modernizar `flext-infra` em slices arquiteturais verdes

Cada item abaixo é bead/PR separado e roda o ciclo completo antes do próximo.

1. **Adotar reparos de validação**: preservar bindings restaurados em `modernizer.py`, release metadata e Mise state; provar pelos fluxos públicos, não pela presença das linhas.
2. **Gitignore owner único**:
   - promover `u.Infra.gitignore_sections` como API pública do utility owner;
   - remover o mixin delegador `_conform_gitignore.py` e a suppression SLF001;
   - compor `render_project_gitignore` na classe de render/conform sem shim;
   - alterar apenas sources; `make gen` atualiza `__init__.py` e lazy maps.
3. **Modernizer tooling**:
   - extrair `resolve_tooling_context` para uma classe/mixin coesa em `_modernizer_tooling.py`;
   - separar seed, leitura obrigatória de tabelas e derivação de analyzer paths;
   - manter modelos sem métodos e a facade `FlextInfraPyprojectModernizer` apenas como composição MRO.
4. **Mise state**:
   - transformar `FlextInfraMiseArtifactsState` em facade MRO canônica;
   - módulos internos separados para planning puro, transaction/journal e cleanup/recovery;
   - preservar uma única API, sem facade compat paralela.
5. **Release requirements**:
   - centralizar parse/traversal de grupos em `u.Infra`/dependencies com protocolo tipado;
   - manter política de specifier de release no owner release e política git/conform no owner conform;
   - eliminar loops duplicados sem misturar políticas distintas.
6. **Runtime census**:
   - remover somente a duplicação real de `project_filter` se o contrato público permanecer idêntico;
   - manter a semântica autorizada de agregar falhas de import como violações, usando a exceção/alias canônico para Ruff zero, não suppression;
   - provar CLI `validate runtime-census` e gate público.
7. **Routes**: manter lazy route tables existentes; mudar wiring somente se um gate ou runtime provar hardcode indevido. Não introduzir modelo com callable/comportamento.

### 5. Zerar `make check` pela causa raiz

1. Corrigir MD013 no owner documental.
2. Agrupar runtime-census por rule/project/module; para cada família ENFORCE, corrigir primeiro o owner `c/t/p/m/u`/facade/config e propagar por `make mod`.
3. Exterminar clones apontados pelo gate de duplicação, começando por `_rope/source.py` versus `_rope_analysis/*` e rules duplicadas `ban-model-rebuild`/`pydantic-boundary`.
4. Não elevar budgets, excluir paths, adicionar `noqa/type:ignore` ou aceitar warnings.
5. Repetir `make check` até zero e atualizar CRG após cada corte estrutural.

### 6. Revalidar testes por comportamento público

1. Inventariar por AST/CRG: mock/patch/fake, chamada privada, assertions de ordem/linha, literal config-owned, fixture copiada e false-green.
2. Preservar fixtures negativas legítimas e construção de modelos públicos; não confundir strings contendo `unittest.mock` com mocks executados.
3. Refatorar assertions por line number em `test_rope_structure.py` para semântica observável.
4. Complementar testes de fases Ruff/coverage com pipeline público do modernizer.
5. Adicionar prova pública P0 para:
   - runtime census via CLI/gate;
   - Ruff lint/format gates;
   - batch apply e snapshot reconciler via CLI `mod`/`ast`;
   - release metadata através do Release Orchestrator, nunca métodos privados.
6. Remover testes sem contrato público útil; não expor internals para salvá-los.
7. A suite completa deve terminar dentro do budget; timeout é defeito de produto/test architecture, não motivo para aumentar limite.

### 7. Ondas fleet-wide em ordem de dependência

Processar um repo/bead/PR por vez, sempre no tip `0.12.0-dev`:

1. foundation: `flext-core`;
2. control plane: `flext-tests`, `flext-cli`, `flext-infra`;
3. platform: api/auth/web/grpc/observability/plugin/meltano;
4. domain: ldap/ldif/db-oracle/oracle-wms/oracle-oic/quality;
5. Singer/dbt: taps, targets e dbt packages.

Em cada membro:

- centralizar config/settings e `c/t/p/m/u` antes de mover classes;
- uma família/classes coesa por módulo;
- facade pública fina, private package `_<modulo>/`, `base.py` como composição MRO, sem `_part*`;
- módulo tocado converge para ≤200 LOC lógicos; dívida adjacente vira bead dependente e é zerada nesta campanha;
- remover old/new coexistence no mesmo slice;
- rodar ciclo completo e integrar antes do próximo consumidor.

Quando todos os módulos first-party estiverem ≤200, baixar `config/codegen.yaml::loc_cap.max_lines` de 1000 para 200, regenerar a frota e provar novamente.

### 8. Prova runtime standalone e workspace

1. Gerar um projeto standalone internal FLEXT pela superfície pública.
2. Provar árvore/config identity e ausência de writes fora dos roots autorizados.
3. Executar nele o ciclo completo, incluindo segundas rodadas.
4. Buildar e executar facade/CLI pública do artefato staged.
5. Atualizar gitlinks do super pelo fluxo canônico.
6. Executar ciclo completo no workspace e consumidores afetados; incluir `flext`, `ai-hub` e `cosmos-main` quando associados ao rollout.

### 9. Landing incremental e encerramento

Para cada slice:

1. atualizar CRG e revisar risco/flows/gaps;
2. merge `origin/0.12.0-dev --no-ff` na lane;
3. ciclo completo verde e fixed points limpos;
4. commit por paths explícitos, atualização Bead e push;
5. CI/review no SHA exato;
6. merge commit no integration branch;
7. fetch do SHA integrado e nova prova runtime crítica;
8. fechar bead somente com comando, cwd, exit e saída decisiva;
9. aposentar branch/worktree/PR apenas após contribuição e história estarem integradas.

## Falhas e recuperação

- Gas City indisponível: reparar city/runtime owner; nunca banco alternativo.
- Setup vermelho: nenhum downstream roda.
- Geração divergente: preservar as duas saídas, corrigir writer e repetir ×2.
- Mod residual: corrigir rule/discovery/semantic apply; não classificar como aceitável.
- Teste versus runtime: estabelecer contrato runtime e corrigir o lado errado.
- Conflito concorrente: reler tree, comunicar pelo bead, adotar e mergear forward.
- Push rejeitado: fetch + merge `--no-ff` da integração + revalidação.
- Warning/timeout/skip: gate vermelho com bead owner.

## Critérios finais de aceite

- Gas City saudável e beads duplicados reconciliados;
- todas as lanes descendem dos tips atuais e nenhuma contribuição única ficou órfã;
- CRG atual nos SHAs revisado e integrado;
- setup e todos os gates verdes, sem warnings/resíduo;
- gen/mod/fix/fmt idempotentes;
- ProjectNew/conform/lazy-init byte-stable;
- owners arquiteturais únicos, sem shims/suppressions/old+new;
- módulos first-party ≤200 LOC e gate SSOT em 200;
- testes exercitam somente comportamento público e config derivada;
- standalone, workspace e consumidores executam runtime real;
- PRs, merge commits, gitlinks, docs e Beads contêm evidência do SHA integrado;
- trees finais limpos e alinhados com `origin/0.12.0-dev`.

## Fora de escopo

- arquitetura FLEXT em third-party forks;
- refactor interno de `wip-hier`;
- Dependabot não relacionado;
- redesign de produto sem consumidor atual;
- qualquer bypass temporário, compatibilidade ou redução de cobertura para obter green.
