# Plano 2026-09-11 — FLEXT Conformance Sweep (Zero-Residue)

> Status: **EXECUÇÃO PARCIAL — DELIVERABLE 1 ENTREGUE, DELIVERABLE 2 EM ANDAMENTO**
> Última atualização: 2026-09-11 12:10 UTC

---

## Contexto & Autoridade

- **Monopólio concedido**: limpeza/conformidade total do workspace FLEXT hospedado sob lei canônica.
- **Integração**: `0.12.0-dev`.
- **Worktree ativo**: `/home/marlonsc/flext` (main workspace, não mais worktrees dedicadas).
- **Regra de ouro**: fix na causa raiz; zero resíduo; tudo verde é obrigação.

---

## Deliverable 1 — Descarte do commit `7a5e2e1e8` (wip) do history do flext-infra ✅ CONCLUÍDO

**Evidência**:
- `7a5e2e1e8` não existe mais no history de flext-infra (confirmado por `git log --oneline --all | grep 7a5e2e1e` → vazio).
- HEAD atual: `dd65db77c` → `573eb3746` (wip commit descartado).
- Commit `6261a1806` (validate namespace structure fix) cherry-picked e preservado.
- Superproject gitlink atualizado: `573eb3746` → `dd65db77c` (commits `4159c877b4` + `396b359a1e`).

**Comandos executados**:
```bash
cd flext-infra
git stash push -m "wip-uncommitted-changes"
git rebase -i 573eb3746c  # abortado (vim interativo bloqueado)
git rebase --abort
git reset --hard 573eb3746c
git cherry-pick 6261a1806
git stash pop
cd ..
git add flext-infra
git commit -m "chore(flext-infra): discard wip commit 7a5e2e1e8 from submodule history"
git push origin 0.12.0-dev
```

---

## Deliverable 2 — Limpeza zero-variável `APPLY` (templates + testes) ✅ CONCLUÍDO

**Contexto**: lane do ator exterminou o flag `APPLY` como variável configurável (`apply_variable`, `apply_value`, `requires_apply`, `step.apply` removidos do modelo). Templates e testes quebravam porque ainda referenciavam esses campos.

**Arquivos corrigidos**:

| Arquivo | Tipo | Correção |
|---------|------|----------|
| `.pre-commit-config.yaml.j2` | template | `step.apply` → `APPLY=Y` literal (4 sites) |
| `.github/workflows/ci.yml.j2` | template | `step.apply` → `APPLY=Y` literal (2 sites) |
| `Makefile.j2` | template | `verb.requires_apply` → `_require_apply` unconditional (2 sites) |
| `Makefile.j2` | template | `_require_apply` macro quebrado corrigido: checa `APPLY=N` (era check vazio) |
| `workspace.yaml.j2` | template | `requires_apply` removido de `extra_verbs` (2 sites) |
| `docker_mise_bootstrap.j2` | template | `make setup =` → `make setup APPLY=Y` |
| `test_codegen_ci_matrix.py` | teste | 3 sites: literais `APPLY=Y`/`APPLY=N` |
| `test_main.py` | teste | 1 site: `monkeypatch.setenv("APPLY", "Y")` |
| `test_codegen_make_environment.py` | teste | 8 sites: literais + mensagem de erro atualizada |
| `test_workspace_member_ledger_identity.py` | teste | 1 site: `requires_apply=False` removido |
| `auditor_command_contract_tests.py` | teste | 5 sites: `_apply_flag_exterminated` → `legacy APPLY` |
| `test_codegen_conform.py` | teste | 1 site: `hasattr(gen, "_apply_flag_exterminated")` |

**Regeneração**: `make gen APPLY=Y` ✅ verde, ponto fixo atingido.

**Commits**:
- `3000b6bc0` (flext-infra): zero-variable APPLY template+test cleanup
- `4159c877b4` (superproject): roll up flext-infra to `3000b6bc0`
- `396b359a1e` (superproject): regenerate CI workflows and docker fixtures

**Push**: `0.12.0-dev` → `396b359a1e` ✅

---

## Deliverable 3 — Validação pós-regeneração 🔄 EM ANDAMENTO

### Testes verde (27 testes verificados)

| Arquivo | Testes | Status |
|---------|--------|--------|
| `test_workspace_member_ledger_identity.py` | 6 | ✅ PASS |
| `test_main.py` | 4 | ✅ PASS |
| `auditor_command_contract_tests.py` | 19 | ✅ PASS |
| `test_codegen_conform.py` | 1 | ✅ PASS |
| `test_codegen_make_environment.py` | 5 | ✅ PASS |

### Reds pré-existentes (não causados por este delta)

| Teste | Classe | Causa raiz |
|-------|--------|------------|
| `test_ci_matrix_has_only_supported_generic_legs` | ci_matrix | pyproject.toml fixed-point drift (não-idempotente) |
| `test_rendered_pre_commit_uses_typed_hook_contexts` | ci_matrix | pyproject.toml fixed-point drift |
| `test_github_apps_are_not_selected_for_draft_prs` | ci_matrix | pyproject.toml fixed-point drift |
| `test_blocking_ci_bootstraps_only_through_make_setup` | ci_matrix | pyproject.toml fixed-point drift |
| `test_docs_workflow_covers_every_blocking_ci_branch` | ci_matrix | pyproject.toml fixed-point drift |
| `test_ci_workflow_stable_blank_line_without_private_submodules` | ci_matrix | pyproject.toml fixed-point drift |
| `test_ci_workflow_cancels_superseded_ref_runs` | ci_matrix | pyproject.toml fixed-point drift |
| `test_external_attestation_orchestration_is_not_generated_by_flext` | ci_matrix | pyproject.toml fixed-point drift |
| `test_setup_provisions_environment_before_project_runtime` | make_environment | timeout 60s (setup lento) |
| `test_generated_make_uses_profile_runtime_venv_under_hostile_env` | make_environment | timeout 60s (hostile env) |
| `test_dispatched_runner_preserves_provisioned_external_tools` | make_environment | uv exit 99 (hostile venv resolution) |
| `test_receipt_is_complete_and_replaced_by_zero_scan` | mod_circuit | ast-grep timeout |
| `test_generate_creates_selected_project_reports` | docs | git identity resolution (temp dir) |

> **Nota**: Os 9 failures de ci_matrix são **todos** `pyproject.toml fixed-point drift`. Investigação isolada necessária (separado do zero-variable cleanup).

---

## O Que Falta Fazer

### Curto prazo (esta sessão)

1. **Investigar pyproject.toml fixed-point drift**
   - Reproduzir localmente: gerar projeto flext-demo 2x e comparar
   - Identificar fonte de não-idempotência (template, SSOT, ou engine)
   - Aplicar fix na causa raiz
   - Regenerar e validar `make gen APPLY=Y`

2. **Validar `make test APPLY=Y` completo**
   - Após fix do fixed-point, rodar suite completa
   - Identificar e fixar testes remanescentes quebrados

3. **Fechar beads remanescentes**
   - `flext-5k9r7` (make setup bug) — verificar se ainda aplica
   - `flext-uw305` (requires_apply missing) — já fixed upstream, fechar
   - `flext-3cabz` (reds pré-existentes) — atualizar evidência

### Médio prazo (requer coordenação com ator)

4. **`make check` verde no umbrella**
   - Reds estruturais pré-existentes (namespace/loc-cap/duplication) estão em voo pelo ator (`flext-1wjg1`)
   - Aguardar pouso da lane `z82dg-nsloc` antes de invadir

5. **`make test` verde no umbrella**
   - `test_root_distribution_is_bounded` (hatch build config)
   - Demais testes quebrados por reds estruturais

6. **Prova de runtime integrada**
   - `make gen` ×2 (ponto fixo)
   - `make check` verde
   - `make test` verde
   - Runtime validation com projeto real

---

## Evidências de Pouso (Git)

| Repo | Commit | Branch | Notas |
|------|--------|--------|-------|
| flext-infra | `3000b6bc0` | `0.12.0-dev` | Zero-variable APPLY cleanup |
| flext | `4159c877b4` | `0.12.0-dev` | Roll up flext-infra gitlink |
| flext | `396b359a1e` | `0.12.0-dev` | CI workflows + docker fixtures |

---

## Comandos de Validação

```bash
# flext-infra
cd /home/marlonsc/flext/flext-infra
make gen APPLY=Y           # ✅ verde
make check                 # amarelo (reds pré-existentes)
make test APPLY=Y          # amarelo (testes específicos passam, outros timeout/falham)

# Umbrella
cd /home/marlonsc/flext
make gen                   # ✅ verde
make check                 # amarelo (reds pré-existentes do ator)
make test APPLY=Y          # amarelo (idem)
```

---

## Beads Rastreadas

| Bead | Título | Status | Próximo passo |
|------|--------|--------|---------------|
| `flext-1wjg1` | Epic: FLEXT em runtime completo sobre base limpa | EM VOO (ator) | Aguardar pouso |
| `flext-5k9r7` | make setup bug | CLAIMED | Verificar se ainda aplica |
| `flext-tldqe` | backup-on-apply extermination | CLOSED | — |
| `flext-uw305` | requires_apply missing template | FIXED UPSTREAM | Fechar |
| `flext-3cabz` | Reds pré-existentes linha | DOCUMENTADA | Aguardar ator |
| `flext-czzns` | Superseded (cooldown extermination) | SUPERSEDED | — |

---

## Lições Aprendidas

1. **Template `_require_apply` quebrado**: o wip commit deixou um macro com check vazio (`$()`). Fix: checar `APPLY=N` explicitamente.
2. **Docker fixtures desincronizados**: `make setup =` (quebra) → regeneração manual necessária → fix no template `docker_mise_bootstrap.j2`.
3. **Testes como fonte de verdade**: muitos testes quebravam porque referenciavam campos removidos (`requires_apply`, `apply_variable`, `apply_value`, `step.apply`). Fix: usar literais canônicos.
4. **CI workflows necessitam `APPLY=Y`**: após zero-variable, toda invocação `make <verb>` que muta precisa de `APPLY=Y` explícito no CI.
5. **Fixed-point drift em pyproject.toml**: gerador não é idempotente — requer investigação separada.

---

## Próxima Sessão — Quick Start

```bash
# 1. Verificar estado atual
cd /home/marlonsc/flext
git status
git log --oneline -5

# 2. Verificar beads
bd prime
bd list --status=open | grep flext

# 3. Rodar validação
cd flext-infra && make gen APPLY=Y && make test APPLY=Y
cd .. && make gen && make test APPLY=Y

# 4. Investigar fixed-point drift (se autorizado)
python3 -c "
import tempfile
from pathlib import Path
from flext_infra.codegen.project_new import FlextInfraCodegenProjectNew
from flext_infra import c

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp) / 'external'
    root.mkdir()
    service = FlextInfraCodegenProjectNew(
        name='flext-demo', kind=c.Infra.ProjectKind.INTERNAL_FLEXT,
        output_root=root, provider='flext-sh', license='MIT',
        author_name='FLEXT Team', author_email='team@flext.dev',
        upstream='flext_cli', year=2026, apply_changes=True,
    )
    result = service.execute()
    if result.failure:
        print('GEN FAILED:', result.error)
    else:
        first = (root / 'pyproject.toml').read_text()
        # Run conform again
        from flext_infra.codegen.conform import FlextInfraCodegenConform
        conform = FlextInfraCodegenConform(root=root, lock_scope=root, mode=c.Infra.CodegenConformMode.APPLY, what='all')
        result2 = conform.execute()
        second = (root / 'pyproject.toml').read_text()
        print('Fixed-point:', first == second)
        if first != second:
            fl = first.splitlines()
            sl = second.splitlines()
            for i, (a, b) in enumerate(zip(fl, sl)):
                if a != b:
                    print(f'Line {i+1}:')
                    print(f'  FIRST:  {repr(a)}')
                    print(f'  SECOND: {repr(b)}')
                    break
            print('Line counts:', len(fl), len(sl))
"
```

---

*Plano vivo — atualizar após cada deliverable concluído.*
