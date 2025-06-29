# CLAUDE.md - PYAUTO WORKSPACE STANDARDS

**Hierarquia**: WORKSPACE-SPECIFIC
**Referência**: `/home/marlonsc/CLAUDE.md` → Metodologia universal
**Referência**: `/home/marlonsc/CLAUDE.local.md` → Issues cross-workspace
**Referência**: `./CLAUDE.local.md` → Issues temporários PyAuto
**Última Atualização**: 2025-06-29

---

## 📊 PYAUTO PROJECT STRUCTURE (COMPREHENSIVE INVENTORY)

### 🏗️ FLX FRAMEWORK MODULES - STATUS REQUIRES VERIFICATION ⚠️

**Location**: Root workspace `/home/marlonsc/pyauto/`

- `flext-core/` - Foundation & Domain (STATUS UNKNOWN - NEEDS VERIFICATION)
- `flext-auth/` - Authentication (STATUS UNKNOWN - NEEDS VERIFICATION)
- `flext-api/` - REST Gateway (STATUS UNKNOWN - NEEDS VERIFICATION)
- `flext-grpc/` - gRPC Services (STATUS UNKNOWN - NEEDS VERIFICATION)
- `flext-web/` - Django Dashboard (STATUS UNKNOWN - NEEDS VERIFICATION)
- `flext-cli/` - CLI Interface (STATUS UNKNOWN - NEEDS VERIFICATION)
- `flext-plugin/` - Plugin System (STATUS UNKNOWN - NEEDS VERIFICATION)
- `flext-observability/` - Monitoring (STATUS UNKNOWN - NEEDS VERIFICATION)
- `flext-meltano/` - ETL Integration (STATUS UNKNOWN - NEEDS VERIFICATION)

### 🔄 ADDITIONAL PROJECTS

**Location**: Root workspace `/home/marlonsc/pyauto/`

- `flext-ldap/` - LDAP Operations (STATUS NEEDS VERIFICATION)

### 🎵 SINGER/MELTANO PROTOCOL PROJECTS - STATUS VERIFICATION REQUIRED

**Location**: Root workspace `/home/marlonsc/pyauto/`

- `tap-ldap/` - LDAP data extraction (STATUS UNKNOWN)
- `tap-oracle-oic/` - OIC data extraction (STATUS UNKNOWN)  
- `tap-oracle-wms/` - WMS data extraction (STATUS UNKNOWN)
- `target-ldap/` - LDAP data loading (STATUS UNKNOWN)
- `target-oracle-oic/` - OIC data loading (STATUS UNKNOWN)
- `target-oracle-wms/` - WMS data loading (STATUS UNKNOWN)
- `dbt-ldap/` - dbt LDAP models (STATUS UNKNOWN)
- `oracle-oic-ext/` - OIC extensions (STATUS UNKNOWN)

### 🏢 ENTERPRISE INTEGRATIONS - STATUS VERIFICATION REQUIRED

**Location**: Root workspace `/home/marlonsc/pyauto/`

- `algar-oud-mig/` - ALGAR Oracle migration (STATUS NEEDS ASSESSMENT)
- `gruponos-poc-oic-wms/` - GrupoNOS POC (STATUS NEEDS ASSESSMENT)

### 📦 BACKUP & LEGACY REFERENCES

**Modularization Sources**:

- `backups/flext-meltano-enterprise_source_20250629_121126/` - Original modularization source
- `backups/flext_original_20250629_121011/` - Empty flext/ directory removed

**Superseded FLX Projects** (moved to backups):

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
ACTIVE IN ROOT (20 projects):
├── FLX Framework (9): flext-core, flext-auth, flext-api, flext-grpc, flext-web, flext-cli, flext-plugin, flext-observability, flext-meltano
├── FLX Extensions (2): flext-ldap, flext-quality (renamed from dc-code-analyzer)
├── Singer/Meltano (8): tap-ldap, tap-oracle-oic, tap-oracle-wms, target-ldap, target-oracle-oic, target-oracle-wms, dbt-ldap, oracle-oic-ext
└── Enterprise (2): algar-oud-mig, gruponos-poc-oic-wms

STORED IN LEGACY (6 projects):
└── Superseded FLX projects: flext-adapter-example, flext-database-oracle, flext-http-oracle-*, flext-oracle-*

STORED IN BACKUPS (8+ items):
├── Sources: flext-meltano-enterprise_source_*, flext-meltano-enterprise_current_*
├── Removed: flext_original_*, ldap-core-shared_backup_*
└── Superseded: flext-oracle-wms_*, flext-oracle-oic_*, flext-adapter-example_*
```

---

## ⚡ WORKSPACE STANDARDS

### Environment Management

**Single workspace venv**: `/home/marlonsc/pyauto/.venv`
**Rule**: NO project-specific venvs allowed

### Project Documentation

**Required**: Every project MUST have its own `CLAUDE.md` or `CLAUDE.local.md`
**Content**: ONLY project-specific information
**Forbidden**: Duplication of workspace/global patterns

### Multi-Agent Coordination

**Primary coordination**: `/home/marlonsc/pyauto/.token`
**Rule**: Read .token before ANY file modification in workspace

---

## 🔒 SECURITY PROTOCOLS

### .ENV File Authority

**Rule**: Each project's .env = SINGLE SOURCE OF TRUTH for that project
**Modification**: Requires explicit user authorization
**CLI**: MUST use debug mode for transparency

### Environment Variables

**Namespacing**: Project-specific prefixes to avoid conflicts
**Standard variables**: WORKSPACE_ROOT, PYTHON_VENV, DEBUG_MODE

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

**Trigger**: Pattern used in 2+ PyAuto projects + applicable to other workspaces

### To Global  

**Trigger**: Pattern proven universal across multiple workspaces

---

**Authority**: CLAIMS REQUIRE VERIFICATION - Project standards need validation
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
