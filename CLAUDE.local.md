# CLAUDE.local.md - PYAUTO WORKSPACE TEMPORARY ISSUES

**Hierarquia**: **WORKSPACE TEMPORÁRIO** - Issues específicos do workspace PyAuto
**Referência Global**: `/home/marlonsc/CLAUDE.md`
**Referência Workspace**: `./CLAUDE.md`
**Última Atualização**: 2025-06-25
**Versão**: 1.0 - Initial Workspace Temporary Issues

---

## 🚨 CURRENT PYAUTO WORKSPACE ISSUES

### **🚨 CRITICAL PRIORITY - CLAUDE AGENTS MULTI-PROJECT CONFUSION**

#### **PROBLEMA CRÍTICO IDENTIFICADO (2025-06-25):**

Agentes Claude se confundem entre projetos PyAuto e aplicam soluções de um projeto em outro.

**IMPACTO REAL:**

- ❌ **Cross-Project Contamination**: Soluções específicas do algar-oud-mig aplicadas no gruponos-poc-oic-wms
- ❌ **Configuration Mixing**: Environment variables de um projeto interferindo em outro
- ❌ **Pattern Misapplication**: Padrões Oracle aplicados em projetos Meltano incorretamente
- ❌ **Context Loss**: Agentes perdem contexto de qual projeto está ativo

**SOLUTION: .token SYSTEM IMPLEMENTATION:**

```bash
# MANDATORY: Each PyAuto project MUST have .token file
echo "PROJECT_CONTEXT=projeto_especifico" > projeto/.token
echo "WORKSPACE=pyauto" >> projeto/.token
echo "PYTHON_VENV=/home/marlonsc/pyauto/.venv" >> projeto/.token
echo "DOCS_REFERENCE=./CLAUDE.md" >> projeto/.token
echo "TEMP_ISSUES=./CLAUDE.local.md" >> projeto/.token
```

**STATUS**: **IMPLEMENTING** - Creating .token files for all PyAuto projects

---

### **⚠️ ONGOING PYAUTO WORKSPACE ISSUES**

#### **1. Virtual Environment Activation Failures**

**Status**: **RECORRENTE** - Agentes esquecem de ativar pyauto/.venv
**Affected Projects**: Todos os projetos PyAuto

**Current Issues**:

- Agentes usam Python system em vez de pyauto/.venv
- Import errors para dependências específicas do PyAuto
- Version conflicts entre global e workspace Python

**Temporary Solution**:

```bash
# MANDATORY before any Python command in PyAuto:
source /home/marlonsc/pyauto/.venv/bin/activate
which python  # Verify: /home/marlonsc/pyauto/.venv/bin/python
```

**Resolution Target**: Implementar validação automática em .token files

---

#### **2. Cross-Project Configuration Leakage**

**Status**: **CRITICAL** - Environment variables between projects conflicting
**Affected Projects**: algar-oud-mig, gruponos-poc-oic-wms

**Current Issues**:

- Oracle configs from gruponos affecting algar LDAP configs
- Entity filtering settings shared between incompatible projects
- Batch size settings optimized for one project breaking another

**Temporary Solutions**:

- Namespace environment variables by project: `ALGAR_*`, `GRUPONOS_*`
- Clear documentation in each project's CLAUDE.local.md
- Project-specific .env files with clear naming

**Resolution Target**: Implement project-specific environment isolation

---

#### **3. Documentation Hierarchy Confusion**

**Status**: **IMPLEMENTING** - New CLAUDE.md system rollout incomplete
**Affected**: Documentation maintenance across PyAuto projects

**Progress**:

- ✅ Global `/home/marlonsc/CLAUDE.md` established
- ✅ Workspace `/home/marlonsc/pyauto/CLAUDE.md` restructured
- ⏳ Project-specific CLAUDE.md creation in progress
- ⏳ .token system implementation ongoing

**Next Actions**:

- [ ] Create CLAUDE.md for each active project
- [ ] Implement .token files with proper references
- [ ] Establish maintenance schedule for hierarchy

**Resolution Target**: End of 2025-06-25

---

## 🔧 PYAUTO-SPECIFIC TECHNICAL DEBT

### **📊 Oracle vs Meltano vs LDAP Pattern Conflicts**

**Issue**: Different projects use conflicting patterns for similar operations
**Impact**: Agents apply wrong patterns, causing architecture inconsistencies

**Current Patterns Conflicting**:

- **Oracle Projects**: Batch processing, transaction management, composite keys
- **Meltano Projects**: Singer protocol, state management, streaming
- **LDAP Projects**: Entry processing, DN handling, schema migration

**Temporary Solution**: Clear project type identification in .token files
**Permanent Solution Needed**: Framework-specific pattern documentation

---

### **🔐 Environment Variable Namespace Collision**

**Issue**: Similar env var names across projects causing configuration conflicts
**Impact**: Wrong configurations applied, breaking integrations

**Collision Examples**:

```bash
# CONFLICTING:
BATCH_SIZE=1000     # Could be Oracle batch or LDAP processing batch
ENTITIES=allocation # Oracle entities vs LDAP entry types
DEBUG=true          # Global debug vs project-specific debug

# FIXED:
GRUPONOS_ORACLE_BATCH_SIZE=1000
GRUPONOS_WMS_ENTITIES=allocation
ALGAR_LDAP_DEBUG=true
```

**Standardization Needed**: Universal env var naming conventions

---

### **📦 Dependency Version Conflicts**

**Issue**: Different projects requiring different versions of same libraries
**Impact**: Virtual environment conflicts, import failures

**Current Status**:

- All projects share single pyauto/.venv
- Some projects need different Oracle library versions
- Meltano vs direct database integration conflicts

**Migration Strategy**: Document per-project dependency requirements

---

## 🎯 TEMPORARY WORKFLOW IMPROVEMENTS

### **🧪 Project-Specific Testing Standards**

**Current Issue**: Different testing approaches across PyAuto projects

- Oracle projects need database integration tests
- Meltano projects need Singer protocol validation
- LDAP projects need directory service mocking

**Temporary Approach**: Document testing requirements in each project's CLAUDE.md

---

### **📈 Performance Monitoring per Project Type**

**Current Issue**: No consistent performance monitoring across different project types

- Oracle projects: Batch throughput, transaction times
- Meltano projects: Extract/load performance, state management
- LDAP projects: Entry processing rates, migration completion

**Investigation Needed**: Evaluate project-type-specific performance metrics

---

## 🔄 RESOLUTION TRACKING

### **Recently Resolved (Archive After 30 Days)**

#### **✅ Multi-Agent File Modification Conflicts (Resolved 2025-06-25)**

**Issue**: Multiple agents modifying same files simultaneously
**Solution**: Implemented mandatory Read() before Edit() protocol
**Status**: **RESOLVED** - Protocol enforced in global CLAUDE.md

---

## 📝 PYAUTO MAINTENANCE NOTES

### **Update Schedule**

- **Daily**: Add new PyAuto-specific issues discovered
- **Weekly**: Update progress on cross-project issues
- **Monthly**: Archive resolved issues, promote patterns to permanent documentation

### **Escalation Criteria**

Issues graduate from here to `/home/marlonsc/CLAUDE.md` when:

- Pattern affects multiple workspaces beyond PyAuto
- Solution becomes universal development methodology
- Issue affects fundamental development practices

### **Cleanup Criteria**

Issues are archived/removed when:

- Fully resolved across all PyAuto projects
- No longer relevant due to project completion
- Superseded by better PyAuto-specific solutions

---

## 📋 PYAUTO PROJECT STATUS SUMMARY

### **ACTIVE PROJECTS STATUS:**

#### **algar-oud-mig**

- **Status**: Dependency issues resolved, LDIF processing functional
- **Blockers**: None currently
- **Next**: Complete migration validation testing

#### **gruponos-poc-oic-wms**

- **Status**: Production-ready Oracle integration complete
- **Performance**: 7,433+ records synchronized successfully
- **Next**: Incremental sync validation

#### **flx-meltano-enterprise**

- **Status**: Architecture excellent, implementation gaps identified
- **Blockers**: NotImplementedError epidemic in core modules
- **Next**: Authentication system implementation

#### **tap-oracle-wms / target-oracle-wms**

- **Status**: Core functionality working
- **Performance**: Optimized for Oracle Autonomous Database
- **Next**: Advanced streaming features

---

**Reference**: For PyAuto workspace patterns → `./CLAUDE.md`
**Reference**: For universal principles → `/home/marlonsc/CLAUDE.md`
**Reference**: For global temporary issues → `/home/marlonsc/CLAUDE.local.md`
**Reference**: For project-specific issues → `<project>/CLAUDE.local.md`

---

_Última Atualização: 2025-06-25_
_Próxima Revisão: Diária durante implementação da hierarquia_
_Status: ATIVO - Issues PyAuto workspace em resolução_
