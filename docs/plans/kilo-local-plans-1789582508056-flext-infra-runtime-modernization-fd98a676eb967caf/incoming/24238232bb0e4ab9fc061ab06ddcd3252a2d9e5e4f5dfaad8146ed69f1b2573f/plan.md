# Plano de recuperação e modernização runtime-first do `flext-infra`

## Objetivo

Restabelecer o `flext-infra` como ferramenta utilizável a partir da tip da branch de
integração: `make setup`, `make gen`, `make fix`, `make fmt`, `make check` e `make test`
devem funcionar pelo contrato real, convergir de forma idempotente e produzir a única
verdade gerada. Depois da estabilização funcional, reduzir drasticamente LOC e
duplicação centralizando primeiro `config/settings/c/t/p/m/u` e somente então decompondo
god modules em facades MRO estritas.

## Atualização de posição — 2026-09-16 23:30Z

Esta atualização reconcilia sessões Kilo/Claude paradas, worktrees do Agent Manager,
auditorias independentes e os planos paralelos. O contexto detalhado e sua proveniência
ficam em `.kilo/plans/addenda/1789582508056/`. Este arquivo é o mapa de execução da
sessão, não uma autoridade publicada: Gas City Bead `flext-itpd1.2` mantém o cursor
durável e os runbooks/ADRs versionados mantêm os contratos estáveis.

### Progresso aceito

- A lane `surf-hornet` implementou o ciclo de `.envrc`/direnv nos SHAs reportados
  `dce9192a0` (`flext-infra`) e `1e49d70841` (superprojeto), com 36 testes direcionados
  verdes, smoke de `direnv`, projeção de 64 arquivos e uma passagem subsequente sem
  publicações. A parte reutilizável é: owner tipado, `direnv allow` pós-apply,
  `source_env_if_exists`, normalização de `.envrc.local` e geração idempotente.
  Auditoria posterior mostrou que esses SHAs não são ancestrais da tip observada; são
  contribuição candidata, não landing atual.
- A mesma lane reduziu a suíte isolada de conform de 129 para 6 falhas por fix-forward e
  identificou o conflito lazy-init/conform, mas não fechou a suíte nem o ciclo global.
  Seu último trabalho útil ficou na determinação dos 6 casos.
- A lane `feature/rope-modernize` reportou pouso do one-writer lazy-init (`flext-infra`
  `4ee618f59`), absorções de membros e supercommit `a3793f9010`. Esses SHAs entram como
  candidatos de adoção, sujeitos à comparação contra a tip e aos Beads antes de serem
  tratados como integrados.
- A lane `aeolian-sodalite` levantou e alterou testes presos a `__name__`, `__module__`,
  `__qualname__`, hardcodes e chamadas manuais de lifecycle. A metodologia é válida, mas
  a branch está 158 commits atrás, o PR #235 está fechado e houve resets/reverts e
  tentativas proibidas de `model_rebuild()`. Nada dessa lane é aceito em bloco; apenas
  contribuições reais ainda ausentes podem ser reimplementadas/adotadas sobre a tip.
- O Gas City/Dolt é o único tracker autoritativo. Consultas read-only confirmaram o
  banco `flext`; nenhum tracker local alternativo é autorizado.

### Estado atual não verde

- Em `~/flext/flext-infra`, `codegen/_conform/execute.py` ainda cria `_lazy_analysis`
  sem propagá-lo e usa o nome fora de escopo na validação. A correção presente em outra
  lane não prova este checkout; o primeiro worker deve reconciliar os dois estados e
  eleger um único objeto filtrado para append, commit e receipt validation.
- `make check` e `make test` não têm prova verde atual. Evidências recentes incluem 914
  findings no check, 129 falhas de teste reduzidas para 6 na lane envrc, 79 erros
  Pyrefly reportados em `_conform`, e uma seleção pós-merge com 58 falhas + 13 erros.
  Esses números vêm de revisões distintas e devem ser substituídos por uma execução
  única na tip atual, nunca somados como se fossem o mesmo baseline.
- O CRG válido existe na worktree `rope-modernize`; a raiz não tem graph próprio. Antes
  de qualquer decisão estrutural, o worker deve atualizar o graph no checkout escolhido
  e provar `head_matches_build=true`.
- `config.py` e `conform.py` continuam god modules no checkout raiz. O split parcial em
  `_config/` e `_conform/` existe, mas o god ainda vence partes do MRO e mantém owners
  duplicados.
- A implementação `gascity/local/none` da lane envrc conflita com a instrução mais nova
  de usar exclusivamente os Beads do Gas City. Preservar a ativação/allow e a limpeza de
  resíduos, mas remover ou desautorizar rotas de ledger local/alternativo no próximo
  corte do owner.
- A governança publicada declara `agentsctl` como facade única de projeção, mas o
  executável não existe em `~/agents` nem no workspace; o programa owner registra esse
  pacote como não iniciado. Projeções provider ficam congeladas até o owner existir e
  passar seus gates. `make gen` não é fallback para `agentsctl`.
- `.kilo/command/*.md` é configuração nativa project-local do Kilo. Não há mapping dela
  em `agentsctl`/`config/codegen.yaml`; portanto não será criada nem projetada sem um
  comando real, consumidor e decisão de ownership.

### Status das fases

| Fase                         | Estado reconciliado           | Critério para avançar                                                                                                    |
| ---------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| 0. Autoridade/docs/projeções | Em execução (`flext-itpd1.2`) | owners mantidos convergentes; `agentsctl` implementado ou projeções explicitamente bloqueadas; Beads/memória atualizados |
| 1. Preflight/Beads/lanes     | Parcial                       | tip, PRs, lanes e Beads revalidados na mesma janela temporal                                                             |
| 2. Setup/gen/conform         | Parcial e vermelho            | objeto lazy único; `setup` verde; `gen` ×2 no-op na tip                                                                  |
| 3. Ciclo canônico            | Não aceito                    | `fix/fmt/check/test/build` verdes no mesmo SHA                                                                           |
| 4. SSOT `c/t/p/m/u`          | Parcial                       | cortar owners duplicados antes dos moves estruturais                                                                     |
| 5. Facades MRO               | Parcial                       | god deixa de vencer a família extraída; facade pública fina                                                              |
| 6. Testes reais              | Parcial, não pousado          | auditoria por interface pública + suíte verde integrada                                                                  |
| 7. Frota                     | Parcial                       | consumidor-piloto e cada cluster verdes/pousados                                                                         |
| 8. Fechamento                | Não iniciado                  | CI/runtime/Beads/PRs/worktrees encerrados com evidência                                                                  |

## Modelo de orquestração e aceite

O coordenador não implementa fatias: mantém plano e Beads, resolve conflitos de
owner/intenção, distribui workers por escopo disjunto, revisa evidência e aceita ou
rejeita entregas. Cada worker recebe exatamente um Bead/repo/stop condition e não fecha,
publica ou integra por conta própria.

Os workers executam em ondas, nunca com owner e projeção concorrentes:

1. **Auditoria read-only:** classifica artefatos e comprova owner/consumer/generator.
2. **Adjudicação do coordenador:** resolve conflito de autoridade e rejeita claims sem
   diff vivo.
3. **Edição de owners mantidos:** workers disjuntos; nenhuma projeção é tocada.
4. **Barreira de projeção:** somente após todos os owners estabilizarem, executar
   `agentsctl`/`make gen`/`make docs` no owner canônico.
5. **QA independente:** reler o tree, comparar diff real com o ledger do worker e provar
   fixed point. Um relatório de subagente não é evidência de arquivo vivo.

6. **Worker de baseline/runtime:** tip + CRG, reconcilia o WIP lazy/conform e entrega
   `setup`/`gen ×2` com logs.
7. **Worker de gates:** somente após baseline aceito, executa fix/fmt/check/test/build e
   devolve clusters de falha reproduzíveis.
8. **Workers de arquitetura:** um owner por vez (`config`, `conform`, transaction,
   Rope), depois da centralização `c/t/p/m/u`; sem alterações cruzadas.
9. **Worker de testes:** revalida contribuições da lane aeolian sobre a tip, elimina
   apenas testes não aderentes e prova comportamento por interfaces públicas.
10. **Workers de frota:** um cluster de repos por Bead, sem tocar o superprojeto; o
    coordenador aprova os SHAs e só então atualiza gitlinks.
11. **QA independente:** revisa CRG impact, runtime, gates, diff, idempotência e
    proveniência. Resultado sem comando, cwd, exit, saída decisiva e SHA é rejeitado.

## Autocrítica e correção de rumo

1. Os planos anteriores cresceram mais rápido que a entrega. Misturaram estabilização,
   release, frota, arquitetura e limpeza histórica, sem um primeiro corte runtime verde
   e pousado.
2. O CRG foi construído e consultado, mas não governou cada mudança. Houve conclusões
   por busca textual e por testes sem provar o caminho runtime correspondente.
3. O estado atual contém trabalho parcial em `codegen/_conform/execute.py`: filtra
   planos lazy sobrepostos, mas cria `_lazy_analysis` e não o propaga corretamente;
   `_validate_managed_fixed_point()` referencia `_lazy_analysis` fora de escopo. Isso é
   um defeito funcional concreto e impede tratar o recorte como concluído.
4. O relatório `dead_code` do CRG não pode ser aplicado mecanicamente: modelos Pydantic
   carregados dinamicamente por YAML aparecem falsamente mortos. Toda remoção exige
   prova por owner, consumidores, config/schema e runtime.
5. Quebrar `conform.py` ou `_models/config.py` antes de obter baseline funcional
   aumentaria a área de falha. A ordem correta é: recuperar runtime, centralizar owners,
   provar equivalência, depois mover responsabilidades.
6. Testes existentes foram usados como autoridade em alguns diagnósticos. A autoridade
   deve ser o runtime público; testes incompatíveis, privados, mockados ou presos a
   valores de config atuais devem ser removidos ou reescritos.
7. O plano anterior aceitava recortes como “se orçamento permitir”. Isso não satisfaz o
   contrato. Cada fatia agora termina apenas com runtime, gates, idempotência, landing e
   evidência no Bead autoritativo do gascity.
8. Esta sessão de planejamento não executará shell nem alterará código. A implementação
   deve ocorrer em sessão/agente habilitado, por comandos canônicos, sem bash ad hoc e
   sem substitutos para `make`, `bd`, `ast-grep` ou `make mod`.
9. A onda documental demonstrou que subagentes podem reportar edições já sobrescritas
   por sync concorrente. Todo aceite passa a exigir `git diff`/conteúdo vivo após o
   término do worker.
10. Um worker editou `docs/knowledge-index.md`, embora o arquivo declare
    `AUTO-GENERATED`. Projeção incorreta não é revertida nem corrigida à mão: o source
    owner é corrigido e o gerador restaura o destino.
11. ADRs e skills receberam caminhos `.kilo/plans/**`, mas `.kilo/plans` é ignorado pelo
    Git. Artefatos publicados não podem depender de contexto local; devem apontar a
    Beads e documentos versionados.

## Autoridades e invariantes

- Beads autoritativos: somente Gas City, acessados pela rota canônica
  `direnv exec <repo> gc bd ...`; não criar tracker paralelo.
- Autoridade documental: ADRs guardam decisões estáveis; runbooks guardam contratos
  operacionais versionados; roadmaps guardam direção; Beads guardam estado e cursor;
  `.kilo/plans`/addenda guardam contexto local da sessão. Nunca inverter essas funções.
- Classes de artefato obrigatórias antes de editar:
  1. `maintained-source` — editável no owner;
  2. `generated-projection` — somente pelo generator;
  3. `historical-evidence` — preservar, acrescentar correção datada;
  4. `runtime-report` — regenerar pelo gate, nunca manter manualmente;
  5. `session-local` — não usar como link/autoridade publicada; somente uma associação
     explícita em `config/plan-collection.yaml` pode publicar snapshot imutável com
     proveniência sob `docs/plans`.
- Base: tip atual da branch de integração de cada repositório. Criar worktree/branch
  dedicada a partir dela.
- Concorrência: fix-forward adopt. Reexaminar e incorporar trabalho paralelo compatível;
  proibidos reset, restore, stash, rebase, rollback compartilhado e force-push.
- Geração: saída de `make gen` vence edições manuais em projeções. Corrigir
  owner/config/template e regenerar.
- Runtime: comportamento real via CLI/API pública vence teste. Falha deve escapar com
  causa; sem shim, fallback, suppressão ou dupla rota.
- Facades: pasta `_<modulo>/`, classes parciais por responsabilidade, `base.py`
  reunindo-as por MRO, módulo público com uma classe facade sem conteúdo. Não usar
  `_parts/`.
- Declarações: config/settings/constants/typings/protocols/models são dados;
  comportamento fica em utilities/services/API/CLI. Modelos owned usam Pydantic v2.
- Qualidade: Ruff e Pyrefly permanecem verdes em cada fatia; Mypy, Pyright, testes,
  duplicação e LOC são gates adicionais, não substitutos.
- Evidência: comando canônico, diretório, exit code, saída decisiva, SHA e runtime
  observado em cada Bead.

## Estado técnico confirmado para iniciar

- CRG do `flext-infra`: 9.242 nós, 82.389 arestas, 988 arquivos; build e HEAD em
  `469b26b4e0b336e78548fef1fdcfca347f9c5d53` no momento da análise.
- Mudanças detectadas: 14 arquivos, 18 símbolos, risco 0,55 e 15 lacunas de teste;
  prioridades: `_execute_managed_locked_prepared`, `_validate_managed_fixed_point` e
  `FlextInfraCodegenConformExecute`.
- God modules confirmados pelo CRG:
  - `_models/config.py`: 3.343 LOC; `FlextInfraConfigModels`: 3.300 LOC.
  - `codegen/conform.py`: 2.996 LOC; `FlextInfraCodegenConform`: 2.959 LOC.
  - `_utilities/_rope/source.py`: 1.123 LOC.
  - `codegen/codegen_transaction.py`: 1.022 LOC.
  - `_utilities/pyproject_conform.py`: 1.012 LOC.
  - `_utilities/census.py`: 959 LOC.
- Defeito concreto no WIP de conform:
  - `execute.py:371-378` remove sobreposição entre `plan.files` e lazy-init.
  - `execute.py:376` cria `_lazy_analysis`, mas `commit_locked()` recebe
    `lazy_analysis.value`.
  - `_validate_managed_fixed_point()` usa `_lazy_analysis` sem recebê-lo. O recorte
    precisa de um único objeto filtrado, passado ao journal e à validação.

## Sequência de execução

### 0. Convergir autoridade, documentação, skills, comandos e projeções

1. Claimar `flext-itpd1.2` no Gas City e registrar a tip/dirty set antes de cada onda.
   Não usar markdown como fila paralela.
2. Inventariar cada artefato com: classe, owner, generator, consumers, destino,
   validação e status de versionamento. Marcador `AUTO-GENERATED`, `managed-by` ou seção
   `[MANAGED]` torna edição direta bloqueante.
3. Atualizar owners mantidos em escopos disjuntos:
   - root docs/ADRs/runbooks;
   - hand-maintained `flext-infra/docs`;
   - skills/commands locais FLEXT;
   - owners globais em `~/agents` mantendo conteúdo project-neutral;
   - Beads e `bd remember` sem criar outro store.
4. Regras de conteúdo:
   - ADR = decisão/contexto/consequência, nunca snapshot de gate ou SHA transitório;
   - estado vivo = Gas City Bead;
   - retomada versionada = runbook/handoff no repositório;
   - plano Kilo = contexto local não versionado;
   - skill = procedimento condicional; rule = invariável; command = gramática;
     agent/config = discovery/projection metadata.
5. Rejeitar edições globais que movam fatos FLEXT/Gas City para `~/agents`; o global
   guarda apenas invariantes genéricas e aponta ao law local.
6. Após a barreira de owners, executar o DAG canônico de projeção identificado pelo
   `agentsctl`: validar source, sync, avaliar/runtime, repetir sync e exigir zero diff.
   Antes disso, resolver o bloqueio do owner:
   - confirmar/claimar o Bead `ag-7hz` no tracker do repositório `~/agents`;
   - implementar o pacote/entrypoint independente `agentsctl` com os verbos optionless
     declarados (`help`, `doctor`, `check`, `sync`, `evaluate`, `secure`, `clean`,
     `live`), ou corrigir a governança publicada se essa decisão foi formalmente
     substituída;
   - provar `make audit`, `make check`, `make test`, `make test-full` e runtime do
     bundle antes do primeiro `sync`;
   - nunca usar `make gen`, scripts privados ou cópia manual como fallback.
7. Executar `make gen` e o owner de docs no workspace somente depois do sync global;
   segunda rodada precisa ser no-op. Nunca restaurar projeção manualmente.
8. Relê todos os destinations e procura: `.kilo/plans` publicado, rota `bd` sem `gc`,
   `scope-nav`, verbos inexistentes, status “green” sem evidência, conflito de markers e
   referências a SHAs sem timestamp/proveniência.
9. Atualizar Beads/memórias com comandos, cwd, exit, saída decisiva e destinations;
   fechar apenas o que possui fixed point e runtime/documentation gate verde.
10. Tratar `.kilo/command/` separadamente: inventariar comandos realmente carregados
    pelas raízes Kilo, preservar arquivos manuais com consumidor e não criar uma
    projeção até existir mapping explícito source→generator→destination.

**Aceite:** nenhum arquivo generated foi editado diretamente; `agentsctl` existe e prova
sync em fixed point, ou a onda termina honestamente bloqueada antes de tocar
destinations; docs publicados não dependem de `.kilo`; `~/agents` permanece
project-neutral; Gas City e runbooks formam a rota durável; ledgers de subagentes
correspondem ao diff vivo.

### 1. Preflight, adoção e Beads

1. Abrir/atualizar o Bead gascity da estabilização; registrar goal, tip base, arquivos
   modificados, lanes/PRs/worktrees relacionados, primeiro gate vermelho e stop
   condition.
2. Criar worktree dedicada da tip da integração. Fazer inventário das diferenças com CRG
   `detect_changes`, `get_review_context`, `get_impact_radius` e `get_affected_flows`;
   reler os arquivos reais antes de qualquer edição.
3. Auditar lanes e PRs do mesmo tema contra a tip atual e seus Beads. Adotar somente
   contribuição real ainda ausente; fechar/subsumir duplicatas após landing. Notificar
   agentes ativos para cooperação fix-forward.
4. Atualizar incrementalmente o CRG e exigir `head_matches_build=true` antes de decisões
   estruturais.

**Aceite:** Bead autoritativo atualizado; worktree baseada na tip; todas as mudanças
atuais classificadas como adotar, integrar ou fora de escopo com evidência.

### 2. Recuperar a funcionalidade do ciclo de geração

1. Corrigir o objeto de análise lazy filtrado em `FlextInfraCodegenConformExecute`:
   criar uma única análise filtrada, passá-la a `append_phase_locked()` e a
   `_validate_managed_fixed_point()`, e validar exatamente o mesmo recibo. Remover
   variável morta e referência fora de escopo.
2. Verificar por CRG callers/callees/tests e fonte se conform e lazy-init têm owners
   sobrepostos. A deduplicação de paths deve ocorrer uma vez, na fronteira de composição
   do transaction plan, não em planners independentes.
3. Executar primeiro o runtime público que reproduz geração/conform. Só depois alinhar
   testes. Provar APPLY e CHECK, abort transaction, fixed point e ausência de resíduo.
4. Executar `make setup`. Corrigir cada primeira falha no owner:
   - instalação/provisionamento em config/templates do setup;
   - journal/lock em transaction owner, com identidade por repo/PIN e recuperação
     determinística;
   - import ausente no produtor/consumidor correto;
   - projeção divergente no SSOT/template, nunca no arquivo gerado.
5. Repetir `make setup` até sucesso; em seguida `make gen` duas vezes e exigir segunda
   execução no-op exit 0.

**Aceite:** setup e gen funcionam no `flext-infra`; conform APPLY/CHECK converge; falha
transacional não deixa resíduo; segunda geração é no-op.

### 3. Fechar o ciclo canônico antes de refatorar arquitetura

1. Rodar em ordem `make fix`, `make fmt`, `make check`, `make test` e `make build`,
   sempre pelo comando canônico e com saída via RTK quando o runner suportar.
2. Corrigir todos os warnings, cosméticos e falhas pré-existentes encontrados no escopo
   tocado. Um gate vermelho vira trabalho no mesmo Bead ou filho dependente, não
   allowlist/suppressão.
3. Atualizar CRG depois de cada mudança; usar `detect_changes` e `get_affected_flows`
   antes do próximo gate.
4. Landar esta fatia funcional isoladamente na integração, reexecutar o ciclo no SHA
   integrado e registrar evidência no Bead.

**Aceite:** baseline integrado com ciclo canônico verde e runtime real provado. Nenhuma
refatoração estrutural grande começa antes disso.

### 4. Centralizar SSOT e `c/t/p/m/u` antes dos splits

Para cada god module, mapear com CRG communities, callers/callees/importers,
config/schema e testes públicos. Aplicar nesta ordem:

1. Mover literais e vocabulários estáveis para `c.Infra` quando forem constantes reais.
2. Mover regras configuráveis para `config/*.yaml` e seus modelos Pydantic; mover knobs
   de ambiente/CLI para settings.
3. Consolidar aliases em `t.Infra`, contratos comportamentais em `p.Infra`, payloads em
   `m.Infra` e operações reutilizáveis em `u.Infra`.
4. Remover helpers locais, tipos duplicados, regras repetidas e wrappers sem consumidor.
   Não mover métodos para models/config/constants.
5. Executar `jscpd` pelo gate canônico; para cada clone, eleger um owner e remover todas
   as cópias no mesmo corte.
6. Reexecutar runtime e ciclo canônico; medir LOC/duplicação antes e depois e registrar
   no Bead.

**Ordem dos alvos:**

1. `_models/config.py` — separar famílias Pydantic por domínio sob `_models/_config/`,
   mantendo `FlextInfraConfigModels` como facade MRO de declarações, sem comportamento.
2. `codegen/conform.py` — remover duplicações já extraídas para `_conform/` depois que
   os contratos compartilhados estiverem em `c/t/p/m/u`.
3. `codegen_transaction.py` — separar sessão/journal/publish/validate por
   responsabilidade.
4. `_utilities/_rope/source.py`, `_utilities/pyproject_conform.py` e
   `_utilities/census.py` — somente após seus consumers e contratos estarem
   centralizados.

**Aceite por alvo:** redução líquida relevante de LOC e clones, um owner por regra, zero
mudança comportamental não planejada, runtime e gates verdes.

### 5. Aplicar facade MRO estrita

1. Criar/ajustar `_<modulo>/` com um módulo por responsabilidade e uma classe
   nested-flext por módulo.
2. Criar `base.py` importando as classes internas e compondo a base MRO completa.
3. Reduzir o módulo público a imports e uma classe facade sem conteúdo.
4. Não criar `_parts/`, aliases compatíveis, facade paralela ou dupla implementação.
5. Usar `make mod` e ast-grep para transformações repetíveis; regras recorrentes entram
   em `config/rules/mod` ou `config/rules/ast`, não em scripts avulsos.
6. Rodar `make gen` para gerar `__init__.py`; nunca editar a projeção manualmente.
7. Validar ordem MRO, imports públicos, construção Pydantic, CLI e consumers reais.

**Aceite:** facade fina, MRO completa, módulos de responsabilidade pequenos, imports
públicos preservados e geração idempotente.

### 6. Revalidar e limpar testes pela realidade

1. Inventariar com CRG e busca estrutural:
   - testes de métodos/funções privadas;
   - `mock`, `patch`, `MagicMock`, fake/stub;
   - assertions de estrutura interna;
   - valores hardcoded pertencentes a config/settings;
   - fixtures que fabricam ambiente diferente do runtime.
2. Para cada caso, identificar o comportamento público real. Remover teste sem contrato
   útil; reescrever o necessário através de API/CLI/facade pública e filesystem/processo
   real controlado.
3. Expected values configuráveis devem vir do mesmo SSOT tipado usado em produção ou de
   round-trip generator/consumer.
4. Manter literais somente para protocolos externos imutáveis.
5. Não alterar produção para satisfazer teste obsoleto. Primeiro provar runtime; depois
   atualizar/remover o teste.
6. Cobrir os gaps CRG reais dos símbolos modificados, sem perseguir falsos positivos
   dinâmicos como remoção automática de modelos Pydantic.

**Aceite:** zero teste do escopo tocado dependente de private internals, mocks/fakes ou
valores config-owned congelados; testes comprovam comportamento público observado.

### 7. Propagar pela frota em fatias pequenas

1. Depois do `flext-infra` integrado e verde, regenerar um consumidor-piloto real a
   partir da tip da integração.
2. Provar setup/gen/fix/fmt/check/test/runtime no consumidor; corrigir producer quando o
   contrato gerado estiver errado e consumer quando receber contrato válido
   incorretamente.
3. Propagar por clusters independentes, com subagentes bounded por Bead/repo e
   instruções explícitas de fix-forward adopt, sem merge/close pelos workers.
4. Coordenador revisa via CRG, integra, executa gates no SHA integrado, atualiza gitlink
   somente após repo membro pousado e verde.
5. Só ampliar para o próximo cluster quando o anterior estiver integrado, reproduzível e
   registrado.

**Aceite:** cada membro tocado está na tip, pousado, runtime-green e refletido no
superprojeto sem WIP órfão.

### 8. Fechamento

1. Reconciliar PRs, branches e worktrees do tema pela contribuição real versus tip e
   Beads; integrar ou encerrar resíduos comprovadamente superseded.
2. Executar o ciclo completo duas vezes na workspace; segunda rodada de gen/fix/fmt deve
   ser no-op.
3. Executar CRG final: graph atualizado, detect_changes, affected flows, test gaps e
   large functions. Abrir Beads separados somente para resíduos fora do escopo aprovado.
4. Atualizar docs/ADRs/skills/commands afetados no mesmo landing.
5. Fechar Beads apenas com SHA integrado, comandos/exit codes, runtime, CI e ausência de
   resíduo.

## Uso obrigatório de ferramentas

- CRG: entrada de cada fatia (`minimal_context`), impacto, flows, communities, large
  functions, review e atualização pós-mudança.
- RTK: compactar toda saída de comandos no runner, sem substituir comandos canônicos.
- gascity `bd` via `direnv`: claim, dependências, evidências e closure.
- `agentsctl`: owner declarado da projeção de governança/provider. Enquanto o entrypoint
  estiver ausente, isso é bloqueio P0 e nenhuma projeção é atualizada. Depois de
  implementado/validado, executar verbos optionless e provar segunda sync sem diff.
- ast-grep/`make mod`: transformações estruturais rules-as-data; não usar substituição
  textual manual em massa.
- Subagentes: fan-out apenas para análises ou repos independentes com retorno
  verificável; coordenador mantém integração, Beads e gates.
- Hooks CRG: observar/update; hook nunca substitui confirmação explícita de graph/head
  nem os gates.

## Stop conditions

- Parar e perguntar somente se duas intenções atuais comprovadas forem incompatíveis ou
  uma ação necessária for destrutiva/irreversível.
- Não parar por gate vermelho, concorrência ordinária, WIP paralelo ou warnings: adotar
  estado atual, corrigir no owner e continuar.
- Não declarar concluído sem runtime na tip integrada, ciclo canônico verde,
  idempotência, Beads atualizados e resíduos reconciliados.
- Não aceitar documentação que cite path ignorado/local como autoridade publicada, nem
  resultado de subagente que não esteja presente no tree vivo.
