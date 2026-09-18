# Beads, lanes e PRs — reconciliação datada de 2026-09-16

<!-- TOC START -->

- [Regra](#regra)
- [Beads observados](#beads-observados)
- [Lanes/PRs observados por Claude](#lanesprs-observados-por-claude)
- [Contribuições históricas com SHAs](#contribuicoes-historicas-com-shas)
- [Checklist de releitura no início da execução](#checklist-de-releitura-no-inicio-da-execucao)

<!-- TOC END -->

## Regra

Somente a leitura atual via `direnv exec <rig> bd ...` e forge/Git decide o estado. A
tabela abaixo impede duplicação de trabalho, mas não autoriza mutação com base em
transcript histórico.

## Beads observados

| Bead                                          | Estado histórico                                                        | Disposição de planejamento                                          |
| --------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `flext-5fxu6.4`                               | IN_PROGRESS no audit read-only de 17:08; owner de generator/enforcement | reler primeiro; candidato ao Bead principal                         |
| `flext-j64nz`                                 | fechado por Claude após push do one-writer lazy-init                    | não reabrir sem regressão atual comprovada                          |
| `flext-oquk7`                                 | aberto; fechamento dependia de `make mod` x2                            | continua pendente até prova atual                                   |
| `flext-1x66z`                                 | recebeu mapa Pyrefly 79                                                 | dados históricos; recontar via gate atual                           |
| `flext-dcge0` / `flext-fkfmu`                 | intents sobrepostos de journal/lock                                     | eleger um owner e superseder duplicata após preservar dependências  |
| `flext-9m4gc` / `flext-wjozx` / `flext-c4k44` | intents sobrepostos de testes inválidos                                 | reconciliar; não criar quarto owner                                 |
| `flext-5k9r7`                                 | setup/toolchain                                                         | vincular se `make setup` atual falhar nesse owner                   |
| `flext-3d8bv`                                 | determinismo de geração                                                 | vincular se gen x2 atual divergir                                   |
| `flext-gniuj`                                 | envrc/Gas City                                                          | usuário confirmou Gas City operacional; só reativar por falha atual |

## Lanes/PRs observados por Claude

| Artefato                                    | Estado histórico reportado                   | Releitura necessária                                   |
| ------------------------------------------- | -------------------------------------------- | ------------------------------------------------------ |
| super PR `#247`                             | criado/atualizado com evidência R0           | verificar open/merged/closed e head SHA                |
| infra PR `#743`                             | criado/atualizado com evidência R0           | verificar open/merged/closed e head SHA                |
| super PR `#235` / `aeolian-sodalite`        | contribuição absorvida, PR superseded/closed | provar ancestry no tip atual antes de retirement final |
| infra PR `#681` / `promoted-framework-lift` | contribuição absorvida, PR superseded/closed | provar ancestry no tip atual                           |
| PRs `#94/#95`                               | aposentados no passe parcial de retirement   | nenhuma ação sem resíduo atual                         |

## Contribuições históricas com SHAs

- one-writer lazy-init lane: `f08e6b7c9`.
- merge infra de promoted-framework-lift/tip: `20893e38e` reportado.
- super absorções/pointers: `0554632a06`, `68942bbf05`, `e096f020e9` reportados na
  sessão.
- âncoras do snapshot de 2026-09-16 eram super `89fc309633`, infra `469b26b4e0`. Em
  2026-09-17, o super continua em `89fc309633`, registra o gitlink infra `96c52f1d6` e
  tem o checkout infra em `d83ccc616` com WIP.

Esses SHAs antigos servem para `merge-base`/contribution archaeology, não como base de
implementação.

## Checklist de releitura no início da execução

1. `bd show` dos Beads acima via direnv; registrar status/deps atuais.
2. listar PRs da lane e seus head/base/merge SHAs.
3. provar ancestry de contribuições históricas no tip atual.
4. comparar branches/worktrees abandonados por hunks e Beads, não por nome.
5. atualizar o Bead principal com super/infra SHAs atuais e primeiro gate reproduzido.
6. somente então fechar/superseder/retirar qualquer artefato.
