# Plano de convergência documental e de governança

<!-- TOC START -->

- [Resultado esperado](#resultado-esperado)
- [Estado de partida verificado](#estado-de-partida-verificado)
- [Lições que passam a ser regras de execução](#licoes-que-passam-a-ser-regras-de-execucao)
- [Adjudicação da auditoria global tardia](#adjudicacao-da-auditoria-global-tardia)
- [Classificação obrigatória do corpus](#classificacao-obrigatoria-do-corpus)
- [Sequência de implementação](#sequencia-de-implementacao)
  - [1. Reancorar e estabilizar ownership](#1-reancorar-e-estabilizar-ownership)
  - [2. Fechar autoridade global e projeção de providers](#2-fechar-autoridade-global-e-projecao-de-providers)
  - [3. Convergir documentos hand-written](#3-convergir-documentos-hand-written)
  - [4. Corrigir owners de projeção](#4-corrigir-owners-de-projecao)
  - [5. Regenerar e provar fixed point](#5-regenerar-e-provar-fixed-point)
  - [6. Landing multi-repo](#6-landing-multi-repo)
  - [7. Encerrar Beads e memórias](#7-encerrar-beads-e-memorias)
- [Falhas esperadas e resposta](#falhas-esperadas-e-resposta)
- [Critérios finais](#criterios-finais)

<!-- TOC END -->

> Historical evidence only. This plan records an earlier execution context and
> its command examples are not current workspace guidance. Use the root
> `AGENTS.md` and `make help` for the active contract.

## Resultado esperado

Convergir documentação, ADRs, skills, commands, projeções, Beads e memórias para um único estado verificável, sem transformar planos ou targets aceitos em alegações de runtime. O trabalho termina somente quando os owners canônicos estão corrigidos, as projeções atingem fixed point, os gates passam nos SHAs integrados e o Bead registra a evidência.

## Estado de partida verificado

- Bead coordenador: `flext-3rld2`, ativo no Gas City; `bd lint --json` chegou a `total: 0`.
- Autoridade global `~/agents`: `dev@1c7e99a4`, pushed e limpa. `make check`, `make docs` e `make test-full` passaram; bundle: 132 skills, 19 commands, 66 agents e 90 rules. Isso aprova o source bundle, não prova ainda os runtimes projetados de GitHub/Claude/Kilo/Codex/Gemini.
- `scope-nav` e sua suíte foram exterminados; CRG é o mapper oficial.
- Superprojeto: checkpoint cooperativo `4e4e30c274`, com ADRs/skills e gitlinks avançados. Há documentação e submódulos ainda dirty; não assumir que o checkpoint está validado.
- ADR-005 e ADR-017 já distinguem implementação corrente, target aceito e proposta. `make mod` existe; `ast` separado e `config/rules/ast/` continuam target do Bead `flext-oquk7`.
- O corpus `docs/projects/` foi retirado da gramática histórica `PROJECT=`, `make val`, `make boot` e instalações diretas, mas docs internas dos membros ainda precisam de sweep owner-aware.
- A coleta de planos começou a produzir `config/plan-collection.yaml`, manifesto, índice e anexos sob `docs/plans/`; tratar tudo como candidato não validado até fixed point.
- Drift gerado confirmado: `pyproject.toml` precisa do banner final do owner; headers heterogêneos precisam de validação pelo schema/template, não substituição estética. `base.mk` é superfície legada rastreada separadamente.

## Lições que passam a ser regras de execução

1. Relatório de subagente não é evidência. Reabrir source, diff e owner antes de aceitar cada conclusão.
2. Subagentes recebem paths disjuntos e modo explícito: `research-only`, `edit-only` ou `owner-and-test`. Não podem commitar, avançar gitlinks ou editar projeções sem autorização específica da fatia.
3. Depois de duas falhas de provider/context, não repetir. Reduzir a fatia ou o coordenador assume.
4. Nunca trocar um comando morto por outro comando direto. Em FLEXT, exemplos executáveis usam apenas verbos do Makefile raiz.
5. Histórico permanece histórico. Planos, releases, audits e handoffs recebem rótulo de evidência datada; não são reescritos como guidance atual.
6. Arquivo com aparência gerada não prova owner. Resolver config, template, política de merge, consumidor e verbo de regeneração antes de editar.
7. Gerar somente depois que todos os writers da fatia terminaram. Rodar geração durante edits concorrentes invalida a projeção.
8. Um commit de membro precede o gitlink do superprojeto. Nenhum checkpoint de docs pode avançar 31 gitlinks sem ancestry, gates e publicação dos membros.

## Adjudicação da auditoria global tardia

A auditoria read-only foi coletada antes do landing `~/agents@1c7e99a4`; cada
finding deve ser reproduzido no SHA integrado antes de virar trabalho.

| Finding                                                                 | Disposição no plano                                                                                                                                                                                                                                   |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Refs `command:*` e `skill:*` em `config/governance.json` seriam phantom | Rejeitado no snapshot atual: `make check` executou `GovernanceBundle.load`, resolveu 132/19/66/90 e passou. Adicionar teste live-config apenas se uma reprodução no SHA atual falhar.                                                                 |
| Eval órfão de `scope-nav`                                               | Resolvido em `1c7e99a4`; skill, suite, tasks e fixture foram removidos e `mod-check` passou 7/7.                                                                                                                                                      |
| `flext-context-routing` ausente no repo global                          | O repo global é provider-neutral; a referência é a um delta local de projetos `internal_flext`. Exigir que o projector materialize esse delta em todo projeto elegível e falhe se faltar; não copiar o skill para o catálogo global por conveniência. |
| `.agents/provider.toml` ausente em `~/agents`                           | Fora de escopo: `~/agents` não é um projeto `internal_flext`. Validar o manifest nos consumidores. No rope-modernize, corrigir `codemod_provider.sgconfig` se ele aponta para um path inexistente.                                                    |
| 40 symlinks `.github/skills` quebrados                                  | Finding runtime potencialmente real. Reproduzir após AI Hub sync; o projector deve recriar destinos válidos ou eliminar a superfície, nunca manter symlinks cacheados.                                                                                |
| `flext-gates-as-products` 66 versus 92 linhas                           | Não decidir por tamanho. Rodar `make waza` e cenários do suite contra a versão canônica; completar o menor skill que satisfaz outcomes, sem restaurar texto por diff.                                                                                 |
| `triage-runtime-skew` sem extensão `.md`                                | Finding real até prova contrária: o loader usa `*.md`. Renomear atomicamente ou retirar o comando se não há consumidor; atualizar catalog/evals e provar bundle.                                                                                      |
| `CLAUDE.md` cita `config/workspaces.yaml` inexistente                   | Finding real: corrigir no owner AI Hub/projector, não no output. O marker deve nomear source e verbo que realmente existem.                                                                                                                           |
| `flext-law` excede budget por bytes                                     | Rejeitado como métrica inválida; o gate `test_delivery_budget_holds_with_measured_composition` passou. Usar tokens medidos pelo owner, não bytes/estimativa.                                                                                          |
| `uv.lock` global seria banido                                           | Não transportar uma correção FLEXT para repo provider-neutral sem owner. Aplicar apenas se config/law global declarar o ban; em FLEXT permanece proibido.                                                                                             |
| `VALIDATE_ON_CHANGE.md` sem owner                                       | Finding real de composição: preservar a diretiva mais nova, intaká-la como regra/ADR canônica e depois substituir o root file por pointer ou removê-lo na mesma projeção.                                                                             |

## Classificação obrigatória do corpus

| Classe            | Owner gravável                               | Tratamento                                                                           |
| ----------------- | -------------------------------------------- | ------------------------------------------------------------------------------------ |
| Guidance corrente | README/docs/standards/guides hand-written    | Atualizar contra source/config/runtime e validar links/exemplos                      |
| ADR               | `docs/architecture/adr/`                     | Manter rationale; declarar `CURRENT IMPLEMENTATION`, `ACCEPTED TARGET` ou `PROPOSED` |
| Projeção          | template/config/generator declarado          | Editar owner; regenerar; nunca editar output                                         |
| Histórico         | releases/audits/handoffs/plans datados       | Preservar conteúdo e rotular como histórico; não usar como comando atual             |
| Evidência runtime | reports/receipts/gates                       | Regenerar pelo comando canônico; nunca fabricar ou copiar totals                     |
| Estado executivo  | Gas City Beads                               | Atualizar status, dependências, critérios e receipts; docs só apontam                |
| Memória durável   | `bd remember`; Kilo como contexto secundário | Guardar apenas decisões/constraints estáveis; corrigir memória obsoleta              |

## Sequência de implementação

### 1. Reancorar e estabilizar ownership

1. Parar novos writers e aguardar/cancelar apenas as fatias ainda ativas pelo mecanismo normal; não matar processos ou reverter trabalho.
2. Executar preflight em `~/agents`, superprojeto e cada submódulo dirty: branch, HEAD, upstream, status e diff por path.
3. Comparar o checkpoint `4e4e30c274` com seu parent. Classificar cada hunk e gitlink como contribuição aceita, projeção prematura ou mudança sem evidência.
4. Atualizar `flext-3rld2` com a matriz `owner -> paths -> SHA -> writer -> gate -> estado`; não criar tracker paralelo.
5. Rebuild incremental do CRG depois que o tree parar de mudar; source vence divergências do grafo.

**Stop:** ownership de todo path dirty conhecido; nenhum writer sobreposto.

### 2. Fechar autoridade global e projeção de providers

1. Tratar `~/agents@1c7e99a4` como global SSOT aprovado.
2. No `~/agents`, executar também `make waza`, `make build`,
   `make validate-artifacts` e `make runtime`; gates já verdes não provam a
   projeção externa.
3. Resolver no source global o comando `commands/flext/triage-runtime-skew`
   invisível ao glob `*.md` e fazer intake de `VALIDATE_ON_CHANGE.md` sem perder
   a precedência da diretiva.
4. No AI Hub, atualizar o pin/bundle e executar o projector oficial para Claude,
   Kilo, Codex, Gemini e GitHub. Não editar `~/.agents`, `.github/skills` ou
   capsules manualmente.
5. Corrigir no projector o marker de `CLAUDE.md` para source/verbo existentes.
   Validar todos os symlinks/destinos do provider depois do sync.
6. Validar que projetos recebem somente bundles globais aplicáveis e que
   `.agents/provider.toml` mantém os deltas branch-matched. Todo projeto
   `internal_flext` deve materializar `flext-context-routing` e `flext-law`; repo
   provider-neutral não precisa dessas superfícies.
7. No rope-modernize, provar que `codemod_provider.sgconfig` resolve ao arquivo
   real; corrigir o manifest owner se o path atual não existe.
8. Provar ausência de `scope-nav`, precedência duplicada, indexes copiados e
   skills Gas City cacheadas no Git.
9. Executar gates nativos do AI Hub e smoke real de ao menos Claude, Kilo e
   GitHub antes de propagar à frota.

**Stop:** runtime dos providers identifica o SHA global integrado e o projeto carrega apenas seu delta.

### 3. Convergir documentos hand-written

Dividir em commits pequenos e independentes:

1. Portal raiz e standards: comandos, ciclo, versões, links, ownership e linguagem CURRENT/TARGET/PROPOSED.
2. ADRs: revisar o diff do checkpoint; em ADR-005 manter tanto rules-as-data quanto rope-only como targets enquanto houver detector Python/AST. Em ADR-017 manter `ast` separado e `config/rules/ast/` como target.
3. Páginas `docs/projects/`: provar zero comandos aposentados sem alterar releases/audits.
4. Docs internas dos membros por domínio: plataforma, LDAP/Oracle, taps, targets e DBT. Alterar somente guidance corrente; rotular planos históricos.
5. Docstrings e exemplos executáveis somente quando o gate apontar drift; não ampliar para refactor de source nesta fatia.

**Validação por commit:** links locais, `git diff --check`, busca de contratos aposentados limitada à classe corrente e gate docs do owner.

### 4. Corrigir owners de projeção

1. Header provenance: alterar templates/testes do `flext-infra`, não outputs. O schema deve exigir quatro fatos sem impor tokens idênticos quando a sintaxe do formato difere: modo gerado, owner exato, ponto de ajuste e `make gen`.
2. Provar que o `FlextInfraInjectCommentsPhase` injeta o banner final no `pyproject.toml`; depois regenerar todos os membros.
3. Resolver `base.mk` pelo Bead owner: se não houver consumidor atual, remover template/config/callers e arquivos na mesma fatia; não apenas ignorar.
4. Corrigir help/Make/CI projections pelos Beads existentes (`flext-5fxu6.4.*`), mantendo uma única registry tipada.
5. Completar plan collection no owner transacional: manifest com provenance/revision/hash, anexos ligados, publicação atômica, remoção de projections órfãs e segundo run sem writes.
6. Nunca executar `make gen` se `flext-ff28g` reproduzir falha transacional. Corrigir journal/phase analysis no owner, provar abort sem resíduo e rerodar o mesmo verbo.

**Stop:** owners e testes estreitos verdes; nenhum output editado à mão.

### 5. Regenerar e provar fixed point

No workspace raiz, registrar cwd, exit e output decisivo:

```bash
make setup
make gen
make mod
make gen
make gen
make fix
make fmt
make docs
make check
make test
make build
```

Regras:

- Segundo `make gen` pós-`mod` deve ser byte-identical.
- `make mod` com findings detection-only permanece vermelho; somente a fase apply evita falso stall.
- Qualquer edit posterior invalida os gates sobrepostos.
- Não usar `PROJECT`, `WHAT`, `APPLY`, comandos de ferramenta ou loops ad hoc.
- Lock/pin proibido (`uv.lock`, `mise.lock`, `exclude-newer`) não pode reaparecer.

### 6. Landing multi-repo

1. Em cada membro alterado: revisar diff, gates afetados, commit explícito, push fast-forward para lane/PR e merge `--no-ff` na integração.
2. Rerodar runtime/gates no SHA integrado do membro.
3. Somente então atualizar o gitlink no superprojeto.
4. No super: absorver integração por merge cooperativo, resolver conflitos fix-forward, repetir ciclo aplicável, commit explícito e push.
5. Revalidar provider runtime, docs publicadas e uma amostra real de consumo após o merge do super.

**Proibido:** commit guarda-chuva que avance membros não publicados, rebase/force-push, ou fechar Bead com gates locais apenas.

### 7. Encerrar Beads e memórias

1. `bd lint --json` deve continuar em zero.
2. Atualizar Beads de owner com comandos, SHAs, PRs, merge commits e runtime; fechar somente os realmente aceitos.
3. `bd remember` mantém: autoridade `~/agents`, ciclo selector-free, estado `mod` versus `ast`, generated-owner law e warning/finding red.
4. Kilo memory recebe apenas correções equivalentes; remover/corrigir records que ainda aleguem CLI Rope separada, `make tests`, tolerância atual a warnings ou `config/rules/ast/` implementado.
5. Fechar `flext-3rld2` somente após projeção, integração e runtime; caso contrário manter `in_progress` com o primeiro gate vermelho e próxima ação exata.

## Falhas esperadas e resposta

| Falha                                              | Resposta owner-correct                                                                                    |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Subagente commita/avança gitlink prematuramente    | Adotar o commit como input, revisar por hunk/ancestry, corrigir forward e validar; nunca resetar          |
| Provider falha/estoura contexto                    | Reduzir fatia uma vez; na segunda falha o coordenador assume                                              |
| `make gen` falha em journal/fixed point            | Parar a invocação, corrigir `flext-ff28g`, provar abort e rerodar `make gen`                              |
| Docs gate encontra comando aposentado em histórico | Rotular histórico/excluir pelo owner tipado; não reescrever evidência datada                              |
| Projeção difere em muitos membros                  | Corrigir template/config uma vez, regenerar e provar amostra + sweep; não investigar ou editar por membro |
| Gate encontra findings “preexistentes”             | Adotar como red no blast radius e corrigir por classe; sem baseline/supressão                             |
| AI Hub projeta bundle global inteiro no projeto    | Corrigir perfil/provider no AI Hub; manter projeto com delta mínimo                                       |

## Critérios finais

- `~/agents` e AI Hub integrados, runtime de projeção provado.
- Corpus corrente sem comandos aposentados; históricos identificáveis.
- ADR index, status e texto sem contradições implementation/target/proposal.
- `make gen` e plan collection em fixed point.
- Nenhum generated output ou gitlink sem owner/commit publicado.
- Gates e runtime verdes nos SHAs integrados, sem warnings/findings.
- `bd lint` zero; Beads/memórias atuais; `flext-3rld2` fechado com receipts completos.
