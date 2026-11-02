# Scripts de manutenção do repositório

## Private module filenames

From the provisioned workspace root, run
`bash scripts/workspace/rename-private-modules.sh` to preview single-underscore
Python module filenames, or add `--apply` to publish the candidate. The script
preserves facade directories and all `__*` filenames, excludes hidden tool and
environment directories. An occupied file or package destination selects
`<name>_definitions.py` instead, preserving the existing owner; an occupied or
competing alternative still fails before publication.
It uses the canonical source inventory and processes declared repositories in
order through the existing semantic rename planner and initializer generator,
not the complete `make mod` cascade. Each repository is published separately;
the preview publishes no source renames but may create control-plane lease
metadata. Arbitrary strings, configuration and documentation are not a
semantic-reference contract and are not globally replaced.

## Canonical docs maintenance

O fluxo de documentação do workspace e dos subprojetos FLEXT é o alvo canônico
`make build WHAT=docs`, implementado pelo orquestrador de `flext-infra`.

### Objetivo

- Rodar o pipeline docs (`generate`, `fix`, `build`, `audit`, `validate`) por escopo
  usando a superfície `make` já gerada.
- Manter a lógica em `flext-infra`, sem scripts paralelos de manutenção.
- Usar `workspace-docs-audit` apenas como alvo customizado estreito para lint Markdown
  dos documentos do workspace.

### Contrato

- Use `PROJECT=<name>` ou `PROJECTS="a b"` para selecionar escopos.
- Use `DOCS_PHASE=<generate|fix|audit|build|validate|all>` para escolher a fase.
- Use `FIX=1` somente quando a fase suportar correção automática.

### Uso rápido

```bash
# Validar documentação de um subprojeto
make build WHAT=docs DOCS_PHASE=validate PROJECT=flext-core

# Auditar documentação do workspace
make build WHAT=docs DOCS_PHASE=audit

# Corrigir docs quando a fase suportar auto-fix
make build WHAT=docs DOCS_PHASE=fix PROJECT=flext-core FIX=1
```

### Notas de compliance

- Arquivos gerenciados automaticamente por `flext_infra` são preservados.
- Não recrie scripts shell para fases já cobertas pelo orquestrador.
- Para validação Markdown isolada do workspace, use `make workspace-docs-audit`.
