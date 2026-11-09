# Handoff: `make mod`/`make gen` estritos e frota verde (2026-11-08)

Para começar uma sessão nova. Bead guarda-chuva: `flext-w8qmv`. Plano aprovado
original: `~/.claude/plans/melhore-corrrija-automatize-ainda-melodic-quill.md`.

## Ordens do operador vigentes

- **Corrigir, nunca contornar.** Todo problema é corrigido no dono, pelas regras
  mais estritas, sem gambiarra nem workaround. Vale também para os projetos externos.
- **Ordem de preferência das correções:**
  1. Regra do catálogo via `make mod RULES=`.
  2. Regra generalizada nova, com fixture e snapshot.
  3. Correção no gerador ou fixer.
  4. Edição manual só para caso único, com o motivo no commit.
- **Merge só com CI verde**, nunca `--admin`.
- **Branches:** `upload-20261007` é a branch de trabalho compartilhada em todos os
  repositórios FLEXT. Ela entra na `0.12.0-dev` por PR verde. O rig `~/flext` fica
  em `upload-20261007`.
- **Commits:** gravar sempre, pequenos e frequentes. Uma edição sem commit num
  worktree compartilhado já se perdeu uma vez.
- **Gates pesados** (mypy, pyright, codemod, smells, duplication): continuam só no
  `make check` local (decisão de 2026-11-08: "Manter como está").
- **Inventário de bases avaliadas em runtime:** foi removido por ser código morto.
  O Ruff TC está desligado pelo axioma de 2026-11-02, e quem decide o posicionamento
  em `TYPE_CHECKING` é a lei de imports.

## Onde o trabalho vive

- **Lane:** a minha é `~/worktrees/flext-infra/base-ci-green-20261108`, branch
  `fix/base-ci-green-20261108`, sempre sincronizada com
  `origin/upload-20261007`. Ela é publicada por fast-forward
  (`git push origin HEAD:upload-20261007`).
- **Tip:** o flext-infra `upload-20261007` está em `8e9b4dddcc`. A raiz
  `upload-20261007` está em `5cc89f5f2e` (já contém a `0.12.0-dev`).
- **Snapshots preservados:** o WIP de todas as worktrees está em
  `preserve/*-wip-20261108`. O log está em
  `~/tmp/flext-campaign/preserve-20261108.log`.

## O que já foi feito (em `upload-20261007`)

- **Projetor model→protocolo:** preserva leitura e escrita (ADR-018). Só vira
  property só-leitura e `Sequence`/`Mapping` quando um modelo é de fato substituído
  (`1d2c180ec6`, regenerado em `07b9d43be1`).
- **Regras de protocolo:**
  - `model-field-names-protocol`, `model-signature-names-protocol` e
    `consumer-annotation-names-protocol`.
  - O consumidor não toca mais campos de classe (`79da7d5c94`).
  - `rewire-model-protocol-field-to-port` não envolve mais `schema_for_model`
    (`10c876578e`). Era a origem de "202 rules keep rewriting".
- **`make gen` de ponta a ponta:** ponto fixo verificado, ou seja, a segunda
  execução escreve 0 arquivos.
  - O scaffold de repositório existente agora só cria fachadas que faltam
    (`07b9d43be1`).
  - Corrigido o `PydanticSchemaGenerationError` em `CodegenConformState`.
- **Regressões corrigidas:**
  - `detector.py`: os `inputs` de `RepositoryRef` eram serializados para dict; a
    validação de `kind` foi restaurada.
  - Removidos os `getattr` de probing, com tipos `get_ast` precisos no Rope.
- **Pyrefly do flext-infra: 203 → 83.**
  - Uniões de protocolo estreitadas pela variante usada.
  - Contrato das portas de conform alinhado.
  - Construção de `SourceRewrite` passa pelo modelo.
  - Globs entram como lista JSON na fronteira dos documentos de regra.
  - Inventário morto removido (`8e9b4dddcc`).
- **Desempenho:** memo de `resolve` de caminhos (`dbce4f2cd3`). O perfil do gen
  está em `~/tmp/flext-campaign/gen-infra.prof`, e o diagnóstico em `flext-obayy.1`.
- **flext-ldif:** gate-set fix aplicado (`01f24ab4`).

## Em andamento ao fechar a sessão

- **`make tests` do flext-infra recusou rodar** (`tests-1.log`): os testes só rodam
  com o primary check verde, e o primary está com pyrefly 83. Os testes das minhas
  mudanças, portanto, **ainda não foram executados**. A revalidação por testes fica
  depois do passo 2.

## Próximos passos, em ordem

1. **Revalidar.** Ler `tests-1.log`. Rodar `CI=Y make check CHECK_PHASE=primary` na
   lane e, quando o CI permitir, o check completo.
2. **Zerar o pyrefly de `src/` do flext-infra (~40 restantes).** Os `tests/` são da
   sessão Rope (PR #2217, que deve ser mergeado em `upload`). Famílias:
    - uniões discriminadas por `isinstance` de modelo: estreitar pela variante usada;
    - fluxos de `ast`/Rope (`RopeAstNode` contra `AST`, escopo opcional);
    - `JsonValue`;
    - `missing-override`;
    - `source_bases_runtime.py:196` (`SourceClassReference.rpartition`);
    - `nesting_references.py:394` (`RopeImportedName` ausente no `p.Infra`).
3. **flext-ldif.**
    - Lint: E501, C901/PLR0914 em `acl_pipeline`, PLR0904 em `acl_region`.
    - Pyrefly 21: 10 `missing-override`, `AclBindRule.require` (protocolo
      desatualizado, sai pelo gen) e o teste gold de ACL.
4. **flext-db-oracle:** lint DOC201 em `tests/conftest.py`.
5. **Abrir o PR** `upload-20261007` → `0.12.0-dev` no flext-infra, e depois nos
   membros, quando o CI estiver verde. Avisar o SHA às sessões que esperam (Kilo2,
   "Projeto continuação e integração", Rope, cosmos-main).
6. **Defeitos do DcBackup, em beads filhos de `flext-w8qmv`** (`.5` a `.11`):
    - (a) o mod aceitar os ids curtos que o check reporta;
    - (b) seed do namespace do projeto nas fachadas geradas;
    - (c) F821 do import-header;
    - (d) property-docstring sem progresso;
    - (e) crash do ban-loose-module-object;
    - (f) storage/cache no filesystem do checkout, com fail-loud;
    - (g) `.gitignore` de `.flext/*.lock` e `.envrc.local` (#2215 da sessão Rope).
7. **Desempenho do gen (`flext-obayy.1`):** usar o cache nativo de arquivos do Rope
   em `native_project.get_python_files` (30 redescobertas, 34 s). Depois, memo da
   resolução de anotações por (escopo, expressão).
8. **Corte semântico `model_fields._port_protocol_annotation`:** também envolve
   protocolos em `t.Port`. Verificar se colide com a forma `schema_for_model`.
9. **Gitlinks e externos.** Gitlinks da raiz num PR verde. Externos (ai-hub,
   algar-oud-mig, mcb, invest, cosmos-main) adotam pela `0.12.0-dev`, com `merge
   --no-ff` e `make upg`.

## Divisão com as outras sessões (sem dois escritores no mesmo arquivo)

| Sessão                               | Escopo                                                                                                                                                                                                  |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fork handling Rope                   | `tests/` do pyrefly do infra (#2217); `ban-runtime-environment-skip` (#2211); pin do rope dc.6 (#2216); `.gitignore` do `.flext` (#2215)                                                                |
| Estabilização cluster (d1110f)       | 4 defeitos do mod/fix: IndentationError de imports, PEP 723, krr what≠filename, verbos promovidos sem target (com admin-merge autorizado para ela)                                                      |
| cosmos-main                          | split por orçamento de membros no `_source_render_module` (`fix/projector-member-budget-20261108`)                                                                                                      |
| Algar                                | `fix:` das regras W3: `ban-test-import-outside-test-namespace`, depois `ban-loose-module-object`, depois `ban-reverse-runtime-import`; também o hook `__contract_model__` do projetor (flext-core #766) |
| Projeto continuação e integração     | perfil do censo no DataOP, para eu corrigir no dono                                                                                                                                                     |
| Projeto flext integração e conclusão | não recebe mensagem direta (outro modo de permissão); o canal com ela é o bead `flext-w8qmv`                                                                                                            |

O handoff da sessão Rope está em `~/flext/.reports/handoff-rope-session-20261108.md`.
Ele cobre as lanes #2211, #2215, #2216 e #2217, o pyrefly de `tests/` e a propagação
do dc.6. Em `upload` + #2217, o pyrefly está em 84.

Os arquivos do projetor que são meus: `_source_structural_projection` e
`source_fields`.
