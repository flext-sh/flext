# Scripts de manutenção do repositório

## `docs-reorg.sh`

Script de reorganização de documentação para o workspace e subprojetos FLEXT.

### Objetivo
- Mover documentação atual para quarentena (`.legacy-docs/<run-id>/<scope>`) com sufixo `.bak`.
- Rodar pipeline docs (`generate`, `build`, `audit`, `validate`) por escopo, um por execução.
- Reidratar documentos úteis não-gerenciados automaticamente.
- Produzir relatório de execução em `.reports/docs/doc-reorg/<run-id>/`.

### Contrato
- **Um escopo por execução**: obrigatório passar exatamente `--project <name>` ou `--project workspace`.
- Não há execução em lote nem `--continue-on-error`.
- Para workspace, as fases `audit`/`validate` usam `make check WHAT=markdown`; as demais fases são no-ops de restauração/preservação.

### Uso rápido

```bash
# Recuperar docs de uma quarentena anterior
scripts/maintenance/docs-reorg.sh --project workspace --recover-run 20260624144000

# Reorganizar docs do workspace
scripts/maintenance/docs-reorg.sh --project workspace --run-id $(date +%Y%m%d%H%M%S)

# Reorganizar docs de um subprojeto
scripts/maintenance/docs-reorg.sh --project flext-core --run-id $(date +%Y%m%d%H%M%S)

# Simular sem alterar arquivos
scripts/maintenance/docs-reorg.sh --project workspace --dry-run
```

### Notas de compliance
- Arquivos gerenciados automaticamente por `flext_infra` são preservados.
- Documentos fora desses arquivos geridos podem voltar da quarentena.
- Use `--dry-run` para simular alterações.
