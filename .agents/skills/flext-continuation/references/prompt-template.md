# Continuação Strict FLEXT - `<BEAD_ID>`

Retome o trabalho cujo estado vivo está no bead `<BEAD_ID>`.
Este prompt é apenas o gatilho operacional; o bead, o código atual e as fontes
canônicas lidas no workspace são a verdade.

## Entrada obrigatória

- **Bead ativo:** `<BEAD_ID>`
- **Skill principal:** `<SKILL_NAME>`
- **Lane:** `<ROOT|FLEXT_INFRA|SUBMODULE_NAME>`
- **Arquivos de escrita:** `<EXPLICIT_FILE_OWNERSHIP_MATRIX>`
- **Projeto canônico de comparação:** `/home/marlonsc/projeto_a`
- **Referências atuais obrigatórias:** liste `file:line` lidos nesta sessão antes
  de editar, incluindo o alvo local e a referência projeto_a equivalente.

## Contrato inviolável

- Recarregue `bd show <BEAD_ID>` antes de cada ciclo e registre progresso com
  `bd update <BEAD_ID> --notes '...'`.
- Aceite o estado atual do workspace como entrada. Nunca use rollback, discard,
  reset, restore, stash, clean, revert, checkout destrutivo, nem tente "voltar"
  código de outro agente. Se houver mudança concorrente, componha com ela ou
  pare com evidência objetiva.
- Leia o código vivo antes de editar. O prompt, resumo ou bead antigo nunca
  vence o arquivo atual.
- Sem compatibilidade paralela: nada de shim, fallback, alias legado,
  conversion layer, wrapper pass-through, suppressions, stubs, hardcode, ou
  coexistência old+new.
- Uma mudança pública exige atualização atômica de todos os consumidores,
  exports, docs e testes na mesma batch.
- Depois de qualquer edição, corrija todos os lints existentes e novos do
  codeset inteiro. O gate de lint workspace é obrigatório e não substitui os
  gates estreitos da lane.
- Em `flext-infra`, não adicione AST/RE. Rewrites estruturais usam Rope e os
  serviços/utilitários mnemônicos existentes; legado AST/RE encontrado vira
  migração fix-forward, nunca justificativa para manter mais do mesmo.

## Padrão FLEXT a aplicar

Use `/home/marlonsc/projeto_a` como referência prática, validada contra o
código atual:

- `src/projeto/api.py:18` - uma facade pública MRO, sem lógica inline.
- `src/projeto/base.py:20` - service base sobre `s[...]` e `ABC`.
- `src/projeto/base.py:65` - `derive_command_params` combina settings e
  input via `flext_cli.cli.derive_model`.
- `src/projeto/cli.py:22` - CLI real como roteador fino, não wrapper.
- `src/projeto/cli.py:236` e `:343` - rotas declarativas com modelos
  `m.*` e handlers tipados.
- `src/projeto/cli.py:363` - `main()` retorna exit code.
- `src/projeto/__init__.py:60` - lazy exports públicos; `__init__.py`
  é export-only.
- `src/projeto/models.py:15`, `constants.py:61`, `protocols.py:98`,
  `typings.py:122`, `utilities.py:147` - facades finas `m/c/p/t/u` compostas
  por MRO e namespaces aninhados.

Não use `_parts/__init__.py` como agregador canônico novo. Quando aparecer no
alvo atual, substitua por owner final explícito em batch própria, com consumers
atualizados e gates verdes.

## Referências globais que devem acompanhar mudança pública

Antes de mexer em facade, classe pública, CLI ou export, rode census local por
`rg` e atualize todos os pontos aplicáveis:

- `src/<pkg>/api.py`, `base.py`, `cli.py`, `__main__.py`.
- `src/<pkg>/__init__.py`, `src/<pkg>/__init__.pyi`, `_exports*.py`,
  lazy import maps e `__all__`.
- `pyproject.toml` em `[project.scripts]`.
- Facades `constants.py`, `models.py`, `protocols.py`, `typings.py`,
  `utilities.py` e namespaces privados proprietários.
- Consumers em `src/`, `tests/`, `docs/`, `examples/`, scripts e submodules
  dependentes.
- `docs/docs_config.json`, docs gerados/auditados e testes de contrato quando
  docs ou símbolo público mudarem.

## Execução sem quebra

1. Declare `TARGET`, `IMPACT`, `RISK` e matriz de ownership no bead.
2. Rode baseline estreito da lane antes de editar.
3. Edite batch de no máximo 5 arquivos, exceto quando uma mudança pública exige
   consumers/exports no mesmo lote para manter import e collection verdes.
4. Após cada batch, rode import smoke do pacote tocado, `ruff check ... --no-fix`,
   `pyrefly check ...`, `pyright ...`, testes escopados, gate funcional de CLI
   quando houver entrypoint, e lint workspace completo.
5. Se qualquer gate ficar vermelho, corrija fix-forward na mesma superfície e
   registre comando, exit code e saída decisiva no bead.
6. Só avance para outra lane depois de commit com pathspec explícito, push
   fast-forward, SHA e evidência no bead.

## Comandos mínimos por batch

- `uv run python -c "import <package>; print(<package>.__name__)"`
- `ruff check <touched-files> --no-fix`
- `make check CHECK_GATES=lint`
- `pyrefly check <touched-files>`
- `pyright <touched-files-or-project>`
- `make test PROJECT=<project> MATCH=<narrow-match>`
- `make docs PROJECT=<project> DOCS_PHASE=audit`
- `<entrypoint> --help` quando `[project.scripts]` existir.

## Delegação

Qualquer subagente recebe este contrato, a lei de verdade/root-cause/R18, os
arquivos exatos que pode escrever, comandos exatos de validação e a regra de
não fazer rollback/discard. Achados longos vão para
`.beads/artifacts/<BEAD_ID>/`; o bead recebe só status, path e evidência curta.

## Próximo passo

Invoque `<SKILL_NAME>`, leia o bead e o código atual, compare com as referências
projeto_a acima e execute apenas o próximo passo não finalizado com gates verdes.
