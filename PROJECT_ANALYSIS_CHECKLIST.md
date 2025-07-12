# PROJECT ANALYSIS CHECKLIST - FLEXT WORKSPACE

**CRITICAL**: This checklist MUST be completed for EACH project before ANY modification

## PROJETOS IDENTIFICADOS (22 total)

1. algar-oud-mig
2. flext-api
3. flext-auth
4. flext-cli
5. flext-core
6. flext-db-oracle
7. flext-grpc
8. flext-ldap
9. flext-meltano
10. flext-observability
11. flext-oracle-oic-ext
12. flext-plugin
13. flext-quality
14. flext-tap-ldap
15. flext-tap-oracle-oic
16. flext-tap-oracle-wms
17. flext-target-ldap
18. flext-target-oracle
19. flext-target-oracle-oic
20. flext-target-oracle-wms
21. flext-web
22. gruponos-meltano-native

## CHECKLIST POR PROJETO

### ✅ VERIFICAÇÕES OBRIGATÓRIAS PARA CADA PROJETO

- [ ] **pyproject.toml exists?** - DOCUMENT CURRENT STATE
- [ ] **Makefile exists?** - DOCUMENT ALL TARGETS
- [ ] **.gitignore exists?** - NEVER MODIFY
- [ ] **requirements.txt exists?** - CHECK IF USED WITH pyproject.toml
- [ ] **setup.py/setup.cfg exists?** - LEGACY CONFIG
- [ ] **.env/.env.example exists?** - DOCUMENT VARIABLES
- [ ] **package.JSON exists?** - FOR JS/TS PROJECTS
- [ ] **go.mod/go.sum exists?** - FOR GO PROJECTS
- [ ] __docker-compose_.yml exists?_* - INFRASTRUCTURE
- [ ] **CI/CD files exist?** - .github/, .gitlab-ci.yml
- [ ] **README.md exists?** - PROJECT DOCUMENTATION
- [ ] **CLAUDE.md exists?** - PROJECT SPECIFIC RULES

### 🔍 PADRÕES A DOCUMENTAR

- [ ] **Language/Framework** - Python/Go/JS/Other
- [ ] **Build system** - make/poetry/npm/go build
- [ ] **Test framework** - pytest/go test/jest
- [ ] **Lint tools** - ruff/black/golangci-lint/eslint
- [ ] **Debug flags** - --debug/--trace/--verbose
- [ ] **Entry points** - main modules/scripts
- [ ] **Dependencies** - key libraries used

### ❌ SCRIPTS PROIBIDOS A PROCURAR

- [ ] fix_*.py files
- [ ] temp_*.py files
- [ ] migrate_*.py files
- [ ] test_*.py OUTSIDE tests/
- [ ] Scripts in parent directories
- [ ] Duplicate functionality scripts

### 📊 QUALITY GATES A VERIFICAR

- [ ] Lint command exists in Makefile?
- [ ] Test command exists in Makefile?
- [ ] Type check command exists?
- [ ] Build command exists?
- [ ] All commands work without errors?

## ANÁLISE INDIVIDUAL DOS PROJETOS
