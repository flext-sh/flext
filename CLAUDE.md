# CLAUDE.md - FLEXT WORKSPACE STANDARDS

**Hierarchy**: WORKSPACE-SPECIFIC
**Reference**: `/home/marlonsc/CLAUDE.md` → Universal methodology
**Reference**: `/home/marlonsc/CLAUDE.local.md` → Cross-workspace issues
**Reference**: `./CLAUDE.local.md` → Temporary FLEXT issues
**Last Updated**: 2025-06-30

---

## 📊 FLEXT PROJECT STRUCTURE (COMPREHENSIVE INVENTORY)

### 🏗️ FLEXT FRAMEWORK MODULES - ✅ FULLY OPERATIONAL

**Location**: Root workspace `/home/marlonsc/flext/`

- `flext-core/` - Foundation & Domain ✅ **OPERATIONAL** (Complete DDD implementation)
- `flext-auth/` - Authentication ✅ **OPERATIONAL** (JWT, sessions, token storage)
- `flext-api/` - REST Gateway ✅ **OPERATIONAL** (Go API server with validation)
- `flext-grpc/` - gRPC Services ✅ **OPERATIONAL** (50+ RPC methods)
- `flext-web/` - Django Dashboard ✅ **OPERATIONAL** (Web interface)
- `flext-cli/` - CLI Interface ✅ **OPERATIONAL** (Command line tools)
- `flext-plugin/` - Plugin System ✅ **OPERATIONAL** (Dynamic loading)
- `flext-observability/` - Monitoring ✅ **OPERATIONAL** (Metrics, tracing, health)
- `flext-meltano/` - ETL Integration ✅ **OPERATIONAL** (Singer protocol)

### 🔄 ADDITIONAL PROJECTS

**Location**: Root workspace `/home/marlonsc/flext/`

- `flext-ldap/` - LDAP Operations (STATUS NEEDS VERIFICATION)
- `flext-quality/` - Code Quality Analysis (STATUS NEEDS VERIFICATION)
- `flext-db-oracle/` - Oracle Database Integration (STATUS NEEDS VERIFICATION)

### 🎵 SINGER/MELTANO PROTOCOL PROJECTS - STATUS VERIFICATION REQUIRED

**Location**: Root workspace `/home/marlonsc/flext/`

- `flext-tap-ldap/` - LDAP data extraction (STATUS UNKNOWN)
- `flext-tap-oracle-oic/` - OIC data extraction (STATUS UNKNOWN)
- `flext-tap-oracle-wms/` - WMS data extraction (STATUS UNKNOWN)
- `flext-target-ldap/` - LDAP data loading (STATUS UNKNOWN)
- `flext-target-oracle-oic/` - OIC data loading (STATUS UNKNOWN)
- `flext-target-oracle-wms/` - WMS data loading (STATUS UNKNOWN)
- `flext-dbt-ldap/` - dbt LDAP models (STATUS UNKNOWN)
- `flext-oracle-oic-ext/` - OIC extensions (STATUS UNKNOWN)

### 🏢 ENTERPRISE INTEGRATIONS - STATUS VERIFICATION REQUIRED

**Location**: Root workspace `/home/marlonsc/flext/`

- `algar-oud-mig/` - ALGAR Oracle migration (STATUS NEEDS ASSESSMENT)
- `gruponos-poc-oic-wms/` - GrupoNOS POC (STATUS NEEDS ASSESSMENT)

### 📦 BACKUP & LEGACY REFERENCES

**Modularization Sources**:

- `backups/flext-meltano-enterprise_source_20250629_121126/` - Original modularization source
- `backups/flext_original_20250629_121011/` - Empty flext/ directory removed

**Superseded FLEXT Projects** (moved to backups):

- `backups/flext-oracle-wms_20250629_122800/` - Superseded by modular structure
- `backups/flext-oracle-oic_*/` - Superseded by enterprise integration
- `backups/flext-adapter-example_*/` - Superseded by plugin system

### 📦 LEGACY PROJECTS (Successfully Moved)

**Location**: `legacy/` directory

- `flext-adapter-example/` - Template superseded by plugin system
- `flext-database-oracle/` - Git submodule (commit: e8fe4da6b74bc69a)
- `flext-http-oracle-oic/` - Superseded by enterprise integration
- `flext-http-oracle-wms/` - Superseded by enterprise integration
- `flext-oracle-oic/` - Superseded by modular structure
- `flext-oracle-wms/` - Superseded by modular structure

**Note**: `flext-database-oracle` still referenced by `gruponos-poc-oic-wms` (9 files)

### 📊 FINAL PROJECT ORGANIZATION

```
ACTIVE IN ROOT (22 projects):
├── FLEXT Framework (9): flext-core, flext-auth, flext-api, flext-grpc, flext-web, flext-cli, flext-plugin, flext-observability, flext-meltano
├── FLEXT Extensions (3): flext-ldap, flext-quality, flext-db-oracle
├── Singer/Meltano (8): flext-tap-ldap, flext-tap-oracle-oic, flext-tap-oracle-wms, flext-target-ldap, flext-target-oracle-oic, flext-target-oracle-wms, flext-dbt-ldap, flext-oracle-oic-ext
└── Enterprise (2): algar-oud-mig, gruponos-poc-oic-wms

STORED IN LEGACY (6 projects):
└── Superseded FLEXT projects: flext-adapter-example, flext-database-oracle, flext-http-oracle-*, flext-oracle-*

STORED IN BACKUPS (8+ items):
├── Sources: flext-meltano-enterprise_source_*, flext-meltano-enterprise_current_*
├── Removed: flext_original_*, ldap-core-shared_backup_*
└── Superseded: flext-oracle-wms_*, flext-oracle-oic_*, flext-adapter-example_*
```

---

## ⚡ WORKSPACE STANDARDS

### Environment Management

**Single workspace venv**: `/home/marlonsc/flext/.venv`
**Rule**: NO project-specific venvs allowed

### Project Documentation

**Required**: Every project MUST have its own `CLAUDE.md` or `CLAUDE.local.md`
**Content**: ONLY project-specific information
**Forbidden**: Duplication of workspace/global patterns

### Multi-Agent Coordination

**Primary coordination**: `/home/marlonsc/flext/.token`
**Rule**: Read .token before ANY file modification in workspace

---

## 🔒 SECURITY PROTOCOLS

### .ENV File Authority

**Rule**: Each project's .env = SINGLE SOURCE OF TRUTH for that project
**Modification**: Requires explicit user authorization
**CLI**: MUST use debug mode for transparency

### Environment Variables

**Namespacing**: Project-specific prefixes to avoid conflicts
**Standard variables**: WORKSPACE_ROOT, Python_VENV, DEBUG_MODE

---

## 🏗️ TECHNOLOGY PATTERNS

### Oracle Integration

- Connection pooling with configurable size
- Batch processing with environment control
- Transaction management across projects

### Meltano/Singer

- State management per Singer spec
- Schema discovery with catalog generation
- Stream processing with concurrency control

### LDAP Operations

- Connection timeout configuration
- Entry processing in batches
- Schema migration with validation

---

## 📁 WORKSPACE ORGANIZATION

### Reference Folder

**Purpose**: Local cache and generated content for workspace
**Rule**: ALWAYS in .gitignore, NEVER committed
**Structure**: documentation/, schemas/, examples/, cache/

### Project Standards

**Required per project**: CLAUDE.md/CLAUDE.local.md, .env, pyproject.toml
**Prohibited**: Individual .venv directories, redundant configs

---

## 🎯 QUALITY GATES

### Production Projects

- Zero lint violations across workspace
- Complete type annotations where applicable
- High test coverage standards

### Development Projects

- Progressive quality implementation
- Documented technical debt
- Clear migration path to production standards

---

## 🔄 PATTERN ESCALATION

### To Cross-Workspace

**Trigger**: Pattern used in 2+ FLEXT projects + applicable to other workspaces

### To Global

**Trigger**: Pattern proven universal across multiple workspaces

---

## 🚀 DEVELOPMENT ENVIRONMENT ENHANCEMENTS

### **New Development Tools Added**

#### **🔧 Build and Development**

- **Makefile**: Complete development automation
  - `make build` - Build Go API server
  - `make dev` - Start development environment
  - `make test` - Run all tests (Go + Python)
  - `make lint` - Run code quality checks
  - `make validate-api` - Validate API endpoints

#### **🐳 Docker Infrastructure**

- **docker-compose.yml**: Complete development stack
  - PostgreSQL database
  - Redis cache/sessions
  - Prometheus metrics
  - Grafana dashboards
  - Jaeger tracing
  - LDAP server for testing
  - Optional Oracle XE database

#### **📋 API Validation**

- **validate_api.sh**: Comprehensive API testing
  - 10 automated endpoint tests
  - Pipeline and plugin operations
  - Health checks and monitoring

#### **📚 Enhanced Documentation**

- **API_VALIDATION_GUIDE.md**: Complete API testing guide
- **GO_ARCHITECTURE_GUIDE.md**: Go implementation architecture
- **.env.example**: All environment variables documented

### **Go API Server Architecture**

#### **Clean Architecture Implementation**

```
cmd/flext/           # Main application entry
internal/
├── bounded_contexts/    # Domain boundaries (DDD)
│   ├── pipeline/       # Pipeline domain
│   └── plugin/         # Plugin domain
├── infrastructure/     # Infrastructure layer
└── shared_kernel/     # Shared domain concepts
```

#### **API Endpoints Available**

- `GET /health` - Health check
- `GET /` - API information
- **Pipelines**: POST, GET, LIST, ADD STEPS
- **Plugins**: REGISTER, GET, LIST

### **Development Workflow**

#### **Quick Start**

```bash
# Setup environment
make setup

# Start development
make dev

# Validate API
make validate-api

# Run tests
make test
```

#### **Docker Development**

```bash
# Start infrastructure
docker-compose up postgres redis prometheus

# Start full stack (with profiles)
docker-compose --profile api --profile web up
```

---

**Authority**: VERIFIED - All enhancements tested and operational
**Scope**: Multi-project workspace coordination and standardization
**Enforcement**: Truth-based verification before claims

---

## 🚨 CRITICAL WARNING FOR MULTI-AGENT COORDINATION

### **ANTI-HALLUCINATION PROTOCOL FOR THIS WORKSPACE**

**MANDATORY BEFORE ANY CLAIMS**:

1. **Use Read tool** to verify file existence and content
2. **Use LS tool** to confirm directory structure
3. **Use Bash tool** to test functionality claims
4. **Use Grep tool** to count actual issues/implementations
5. **Check .token file** for ongoing agent coordination

### **FORBIDDEN CLAIMS WITHOUT VERIFICATION**

- ❌ "100% complete" without comprehensive testing
- ❌ "PRODUCTION ready" without deployment validation
- ❌ Specific percentages without measurement
- ❌ "VALIDATED" without actual validation execution
- ❌ Technology claims without code inspection

### **REQUIRED STATUS PREFIXES**

- ✅ **VERIFIED**: Confirmed through tool usage
- ❓ **UNKNOWN**: Status requires investigation
- ⚠️ **NEEDS VERIFICATION**: Claims need validation
- 🔧 **IN PROGRESS**: Currently being worked on

### **MULTI-AGENT COORDINATION RULES**

1. **Read .token** before starting work on any project
2. **Write .token** with your planned actions
3. **Update status** only after actual verification
4. **Admit uncertainty** rather than making false claims
5. **Reference tool results** in all claims

**ENFORCEMENT**: Any agent violating these rules undermines workspace coordination

---

## 🛑 ANTI-CHAOS PROTOCOL - MANDATORY RULES

### **ABSOLUTELY FORBIDDEN ACTIONS**

#### **1. FILE MODIFICATIONS - NEVER MODIFY WITHOUT PERMISSION**

- ❌ **NEVER modify pyproject.toml** - These define project dependencies and structure
- ❌ **NEVER modify .gitignore** - Repository-wide file tracking rules
- ❌ **NEVER modify Makefile** - Build and deployment automation
- ❌ **NEVER modify docker-compose.yml** - Infrastructure definitions
- ❌ **NEVER modify .env files** - Contains secrets and configurations
- ❌ **NEVER modify CI/CD files** (.github/workflows, .gitlab-ci.yml, etc)

**EXCEPTION**: Only with EXPLICIT user permission: "Please update the pyproject.toml"

#### **2. SCRIPT CREATION - FORBIDDEN PATTERNS**

- ❌ **NEVER create loose scripts** outside project structure
- ❌ **NEVER create "fix_*.py" scripts** - Use proper project tools
- ❌ **NEVER create "migrate_*.py" scripts** - Use project migration system
- ❌ **NEVER create "temp_*.py" scripts** - Temporary code belongs in tests
- ❌ **NEVER create scripts in parent directories** - Stay within project boundaries
- ❌ **NEVER create duplicate functionality** - Check existing code first

**CORRECT APPROACH**: Use existing project structure and tools

#### **3. DIAGNOSIS - MANDATORY DEBUG PRACTICES**

- ✅ **ALWAYS use --debug flag** when available
- ✅ **ALWAYS use --trace flag** for detailed execution paths  
- ✅ **ALWAYS check logs** before claiming errors
- ✅ **ALWAYS verify with actual commands** not assumptions
- ✅ **ALWAYS read error messages completely** before acting

**FORBIDDEN**: Making changes without understanding root cause

#### **4. CODE PATTERNS - ANTI-DUPLICATION RULES**

- ❌ **NEVER copy-paste code** without understanding purpose
- ❌ **NEVER duplicate existing functionality**
- ❌ **NEVER create parallel implementations**
- ❌ **NEVER add fallback code** without explicit need
- ❌ **NEVER add "just in case" code**

**MANDATORY**: Search for existing implementations first

#### **5. DOCUMENTATION - TRUTH-BASED ONLY**

- ❌ **NEVER create reports with unverified claims**
- ❌ **NEVER use percentages without measurement**
- ❌ **NEVER claim "VALIDATED" without running validation**
- ❌ **NEVER document future plans as completed**
- ❌ **NEVER create inflated success reports**

**REQUIRED**: All documentation must reference tool output

### **MANDATORY WORKFLOW**

#### **Before ANY Modification:**

1. **INVESTIGATE** - Use Read/Grep/LS to understand current state
2. **VERIFY** - Check if functionality already exists
3. **TEST** - Use debug/trace to understand behavior
4. **ASK** - Request permission for infrastructure changes
5. **IMPLEMENT** - Make minimal required changes only

#### **Quality Gateway Checklist (MANDATORY AT END OF EACH CYCLE):**

```bash
# 1. Check for syntax errors
make lint || echo "Fix linting errors"

# 2. Run type checking  
make typecheck || echo "Fix type errors"

# 3. Run tests
make test || echo "Fix failing tests"

# 4. Verify no loose scripts created
find . -name "fix_*.py" -o -name "temp_*.py" -o -name "migrate_*.py" | grep -v tests

# 5. Check for code duplication
# Use appropriate duplication detection tool

# 6. Verify documentation accuracy
# All claims must have supporting evidence
```

### **STANDARD COMMANDS TO USE**

#### **For Python Projects:**

```bash
# Debug execution
python -m <module> --debug --trace

# Check dependencies  
pip list | grep <package>

# Run with full logging
PYTHONPATH=. LOG_LEVEL=DEBUG python <script>
```

#### **For Go Projects:**

```bash
# Debug build
go build -v -x

# Run with debug
GODEBUG=gctrace=1 ./binary

# Check dependencies
go mod graph | grep <package>
```

### **CONSEQUENCES OF VIOLATIONS**

1. **Project instability** from modified configurations
2. **Dependency conflicts** from changed pyproject.toml
3. **Build failures** from altered Makefiles
4. **Security breaches** from exposed .env files
5. **Code chaos** from duplicate implementations
6. **Trust erosion** from false documentation

### **EMERGENCY RECOVERY**

If chaos has already occurred:

1. **STOP all modifications immediately**
2. **Run git status** to see all changes
3. **Revert infrastructure files** to last known good state
4. **Remove all loose scripts** created outside project structure
5. **Run quality gateway** to verify system health
6. **Document what went wrong** in CLAUDE.local.md

**REMEMBER**: The goal is STABILITY, not activity. Better to do nothing than create chaos.

---

## 📊 VERIFIED PROJECT CONFIGURATIONS - FLEXT WORKSPACE

### 🔴 DESCOBERTAS CRÍTICAS DA ANÁLISE

#### PROBLEMAS ENCONTRADOS

1. **19 scripts fix_*.py** em scripts/ e scripts/legacy/
2. **flext-plugin** tem fix_syntax_errors.py
3. **flext-web** e **flext-grpc** têm erro no Makefile linha 121
4. **3 projetos Go** no workspace (root, flexcore, pkg/meltano)

#### PROJETOS Python (Poetry-based)

- **TODOS** usam pyproject.toml + Poetry (PEP 517/518)
- **TODOS** têm Makefile padronizado
- **TODOS** usam Ruff para linting
- **PADRÃO MODERNO**: Sem requirements.txt, setup.py ou setup.cfg

#### COMANDOS PADRÕES VERIFICADOS

```bash
# SEMPRE USAR:
make check      # Roda tudo: lint, type, test
make test       # Roda pytest
make lint       # Roda ruff
make format     # Formata código

# PARA SERVIDORES:
make api-serve      # flext-api
make dev            # flext-web, flext-grpc
make cli-test       # flext-auth, flext-cli

# DEBUG CORRETO:
PYTHONPATH=. python -m module --debug --trace
LOG_LEVEL=DEBUG python script.py
```

### 🛑 REGRAS ESPECÍFICAS DO WORKSPACE FLEXT

1. **VIRTUAL ENV ÚNICO**: `/home/marlonsc/flext/.venv`
   - NUNCA criar venv em subprojetos
   - SEMPRE ativar o venv do workspace

2. **POETRY COMMANDS**:

   ```bash
   # SEMPRE no diretório do subprojeto:
   poetry install      # Instala dependências
   poetry add package  # NUNCA! Use usuário aprovar
   poetry update      # NUNCA! Pode quebrar versões
   ```

3. **ESTRUTURA OBRIGATÓRIA**:

   ```
   projeto/
   ├── src/           # Código fonte
   ├── tests/         # ÚNICO lugar para testes
   ├── Makefile       # NUNCA modificar
   ├── pyproject.toml # NUNCA modificar
   └── .gitignore     # NUNCA modificar
   ```

4. **IMPORTS CORRETOS**:

   ```python
   # SEMPRE absolute imports:
   from flext.core import Domain
   # NUNCA relative imports em src:
   from ..core import Domain  # ERRADO!
   ```

5. **QUALITY GATES FLEXT**:

   ```bash
   # EXECUTAR EM CADA PROJETO APÓS MUDANÇAS:
   cd projeto && make check
   # Se falhar QUALQUER etapa = CORRIGIR
   ```

### 📁 ARQUIVOS PARA REMOVER (URGENTE)

```bash
# ESTES ARQUIVOS VIOLAM AS REGRAS:
./flext-plugin/fix_syntax_errors.py
./scripts/fix_*.py (todos os 3)
./scripts/legacy/fix_*.py (todos os 16)
```

**AÇÃO NECESSÁRIA**: Solicitar ao usuário permissão para remover estes arquivos.
