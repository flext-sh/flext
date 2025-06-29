# CLAUDE.local.md - FLX-LDAP PROJECT SPECIFICS

**Hierarquia**: **PROJECT-SPECIFIC**  
**Projeto**: FLX LDAP - Enterprise Directory Migration & ETL Orchestrator  
**Status**: PRODUCTION READY - Active migration orchestration  
**Framework**: FLX Framework + Singer Protocol + dbt + LDAP Migration  
**Última Atualização**: 2025-06-26

**Referência Global**: `/home/marlonsc/CLAUDE.md` → Universal principles  
**Referência Workspace**: `../CLAUDE.md` → PyAuto workspace patterns  
**Referência Cross-Workspace**: `/home/marlonsc/CLAUDE.local.md` → Cross-workspace issues

---

## 🎯 PROJECT-SPECIFIC CONFIGURATION

### Virtual Environment Usage

```bash
# MANDATORY: Use workspace venv
source /home/marlonsc/pyauto/.venv/bin/activate
# NOT project-specific venv
```

### Agent Coordination

```bash
# Read workspace coordination first
cat /home/marlonsc/pyauto/.token | tail -5
# Use project .token only for project-specific coordination
```

### Project-Specific Environment Variables

```bash
# FLX LDAP specific configurations
export LDAP_TAP_HOST=source.ldap.com
export LDAP_TAP_PORT=636
export LDAP_TAP_BIND_DN="cn=service-account,ou=services,dc=company,dc=com"
export LDAP_TAP_PASSWORD=secure_tap_password
export LDAP_TAP_BASE_DN="dc=company,dc=com"
export LDAP_TARGET_HOST=target.ldap.com
export LDAP_TARGET_PORT=636
export LDAP_TARGET_BIND_DN="cn=admin,dc=target,dc=com"
export LDAP_TARGET_PASSWORD=secure_target_password
export LDAP_TARGET_BASE_DN="dc=target,dc=com"
export DBT_PROJECT_DIR=../dbt-ldap
export DBT_TARGET=dev
export FLX_LDAP_LOG_LEVEL=DEBUG
export FLX_LDAP_OUTPUT_PATH=./output
```

---

## 🏗️ FLX LDAP ARCHITECTURE

### **Purpose & Role**

- **Migration Orchestrator**: Complete LDAP-to-LDAP migration pipeline management
- **ETL Coordinator**: Orchestrates tap-ldap, dbt-ldap, and target-ldap components
- **Enterprise Directory Bridge**: Facilitates complex directory migrations and transformations
- **Integration Platform**: Unified interface for LDAP data operations across PyAuto ecosystem
- **Migration Planning Engine**: Advanced migration strategy and execution planning

### **Core Orchestration Components**

```python
# FLX LDAP orchestrator structure
src/flx_ldap/
├── cli.py               # Main CLI orchestrator interface
├── config.py            # Configuration management system
├── migrator.py          # Migration execution engine
├── orchestrator.py      # ETL pipeline orchestrator
├── migration_planner.py # Migration strategy planning
├── schema_analyzer.py   # LDAP schema analysis
└── utils.py             # Shared utilities and helpers
```

### **Integration Ecosystem Architecture**

- **tap-ldap Integration**: Source directory data extraction management
- **target-ldap Integration**: Target directory data loading orchestration
- **dbt-ldap Integration**: Data transformation pipeline coordination
- **algar-oud-mig Integration**: Complex migration scenario handling
- **Singer Protocol**: Complete ETL pipeline following Singer specifications

---

## 🔧 PROJECT-SPECIFIC TECHNICAL DETAILS

### **Development Commands**

```bash
# MANDATORY: Always from workspace venv
source /home/marlonsc/pyauto/.venv/bin/activate

# Core development workflow
make install-dev       # Install development dependencies with all extras
make test              # Run comprehensive test suite
make test-unit         # Unit tests only
make test-integration  # Integration tests with mock LDAP
make test-e2e          # End-to-end tests with Docker LDAP
make lint              # Code quality checks
make format            # Code formatting

# FLX LDAP CLI operations
python -m flx_ldap.cli validate
python -m flx_ldap.cli show-config --debug
python -m flx_ldap.cli sync --catalog catalog.json --state state.json
```

### **Migration Orchestration Testing**

```bash
# Test complete migration pipeline
flx-ldap migrate plan \
  --source-host source.ldap.com \
  --target-host target.ldap.com \
  --base-dn "dc=company,dc=com" \
  --output migration-plan.json

# Test ETL pipeline orchestration
flx-ldap sync \
  --catalog catalog.json \
  --state state.json \
  --dry-run \
  --log-level DEBUG

# Test individual component integration
flx-ldap extract --output test-output.jsonl
flx-ldap transform run --models dim_users,dim_groups
flx-ldap load --input test-output.jsonl --dry-run
```

### **Integration Testing Protocols**

```bash
# Test with algar-oud-mig integration
flx-ldap migrate run \
  --source-catalog source-catalog.json \
  --target-catalog target-catalog.json \
  --comparison-enabled

# Test dbt-ldap integration
flx-ldap transform run --full-refresh
flx-ldap transform test
flx-ldap transform snapshot
```

---

## 🚨 PROJECT-SPECIFIC KNOWN ISSUES

### **Orchestration Complexity Challenges**

- **Component Dependencies**: Complex dependency management between tap/target/dbt components
- **State Management**: Coordinating state across multiple Singer protocol components
- **Migration Rollback**: Limited rollback capabilities for complex multi-stage migrations
- **Performance Coordination**: Balancing performance across tap, transform, and target operations
- **Error Propagation**: Complex error handling across multiple integrated components

### **Enterprise Migration Considerations**

```python
# FLX LDAP specific orchestration patterns
class FLXLDAPOrchestrationPatterns:
    """Production patterns for LDAP migration orchestration."""

    def handle_multi_component_state_management(self):
        """Coordinate state across tap, dbt, and target components."""
        # Manage state consistency across pipeline
        state_coordinator = StateCoordinator()

        # Save state checkpoints at each stage
        tap_state = state_coordinator.save_tap_checkpoint(tap_output)
        dbt_state = state_coordinator.save_dbt_checkpoint(transform_results)
        target_state = state_coordinator.save_target_checkpoint(load_results)

        # Enable rollback to any checkpoint
        return state_coordinator.create_pipeline_checkpoint({
            "tap": tap_state,
            "dbt": dbt_state,
            "target": target_state
        })

    def coordinate_migration_with_validation(self, source_config, target_config):
        """Execute migration with comprehensive validation."""
        # Pre-migration validation
        source_validator = self.validate_source_connectivity(source_config)
        target_validator = self.validate_target_capacity(target_config)

        # Execute migration with monitoring
        migration_result = self.execute_monitored_migration(
            source_config=source_config,
            target_config=target_config,
            validation_rules=self.get_enterprise_validation_rules()
        )

        # Post-migration verification
        integrity_check = self.verify_migration_integrity(migration_result)
        return self.generate_migration_report(migration_result, integrity_check)
```

### **Production Integration Error Handling**

```bash
# Common FLX LDAP orchestration issues
1. Component Version Conflicts: Different Singer SDK versions across components
2. State File Corruption: Pipeline state inconsistency across components
3. Memory Management: Large directory migrations exceeding memory limits
4. Timeout Coordination: Different timeout settings across tap/target causing failures
5. Schema Evolution: Changes in source schema breaking dbt transformations
```

---

## 🎯 PROJECT-SPECIFIC SUCCESS METRICS

### **Migration Orchestration Efficiency**

- **End-to-End Migration Time**: <4 hours for directories with 100K+ entries
- **Component Integration Reliability**: 99.9% successful component coordination
- **State Management Accuracy**: 100% state consistency across pipeline stages
- **Migration Data Integrity**: 99.99% data accuracy in source-to-target migration
- **Rollback Capability**: <10 minutes to rollback failed migrations

### **Enterprise Integration Goals**

- **Multi-Domain Support**: Handle complex enterprise directory topologies
- **Schema Transformation Success**: 100% successful schema mapping execution
- **Incremental Migration Efficiency**: <30 minute sync cycles for directory changes
- **Validation Coverage**: 100% pre/post migration validation completion
- **Documentation Generation**: Automatic migration documentation and reporting

---

## 🔗 PROJECT-SPECIFIC INTEGRATIONS

### **FLX Framework Integration**

- **Core Patterns**: Uses FLX hexagonal architecture for orchestration layer
- **Configuration Management**: Follows FLX configuration conventions
- **Monitoring Integration**: Uses FLX monitoring patterns for pipeline visibility
- **Error Handling**: Implements FLX error handling patterns across components

### **PyAuto Ecosystem Integration**

- **tap-ldap**: Primary data extraction component integration
- **target-ldap**: Primary data loading component integration
- **dbt-ldap**: Data transformation engine integration
- **ldap-core-shared**: Shared LDAP models and utilities
- **algar-oud-mig**: Complex migration scenario handler

### **Singer Protocol Ecosystem**

```python
# Production Singer orchestration integration
class ProductionSingerOrchestration:
    """Production-grade Singer protocol orchestration."""

    def __init__(self):
        self.config = FLXLDAPConfig.from_env()
        self.state_manager = StateManager(self.config.state_path)
        self.catalog_manager = CatalogManager(self.config.catalog_path)

    async def execute_full_pipeline(self):
        """Execute complete Singer protocol pipeline."""
        # Phase 1: Discovery and catalog generation
        catalog = await self.discover_source_catalog()
        await self.catalog_manager.save_catalog(catalog)

        # Phase 2: Extract with state management
        tap_output = await self.execute_tap_extraction(
            catalog=catalog,
            state=self.state_manager.get_current_state()
        )

        # Phase 3: Transform with dbt
        dbt_results = await self.execute_dbt_transformations(tap_output)

        # Phase 4: Load to target
        load_results = await self.execute_target_loading(dbt_results)

        # Phase 5: Update state
        await self.state_manager.update_state(load_results.final_state)

        return PipelineResult(
            tap_results=tap_output,
            dbt_results=dbt_results,
            load_results=load_results,
            final_state=load_results.final_state
        )
```

---

## 📊 PROJECT-SPECIFIC MONITORING

### **Orchestration Pipeline Metrics**

```python
# Key metrics for FLX LDAP pipeline monitoring
FLX_LDAP_METRICS = {
    "pipeline_execution_time": "Total end-to-end pipeline duration",
    "component_coordination_success": "Success rate of component handoffs",
    "state_consistency_score": "State consistency across pipeline stages",
    "migration_throughput": "Records migrated per minute",
    "error_recovery_time": "Time to recover from pipeline failures",
    "validation_coverage": "Percentage of data passing validation checks",
}
```

### **Migration Health Monitoring**

```bash
# Comprehensive migration monitoring
flx-ldap validate --verbose --check-all-components
flx-ldap migrate plan --dry-run --output plan-check.json
flx-ldap show-config --validate-connections --check-permissions
```

---

## 📋 PROJECT-SPECIFIC MAINTENANCE

### **Regular Maintenance Tasks**

- **Daily**: Monitor pipeline execution performance and component health
- **Weekly**: Review state file integrity and catalog synchronization
- **Monthly**: Update component versions and test integration compatibility
- **Quarterly**: Performance optimization and migration strategy review

### **Component Integration Maintenance**

```bash
# Keep all Singer components updated
pip install --upgrade tap-ldap target-ldap dbt-ldap

# Validate component compatibility
flx-ldap validate --check-versions
singer-check-tap --tap tap-ldap --config tap-config.json
singer-check-target --target target-ldap --config target-config.json
```

### **Emergency Procedures**

```bash
# FLX LDAP emergency troubleshooting
1. Check component availability: flx-ldap validate --check-all-components
2. Reset pipeline state: rm state.json && flx-ldap sync --full-refresh
3. Test individual components: flx-ldap extract --dry-run, flx-ldap load --dry-run
4. Emergency rollback: flx-ldap migrate rollback --checkpoint latest
5. Debug pipeline execution: flx-ldap --log-level DEBUG sync --verbose
```

---

**PROJECT SUMMARY**: Orquestrador empresarial FLX para migrações LDAP complexas, coordenando tap-ldap, dbt-ldap e target-ldap em pipelines ETL completos com planejamento avançado de migração e validação integral.

**CRITICAL SUCCESS FACTOR**: Manter coordenação perfeita entre todos os componentes Singer do ecossistema PyAuto, garantindo migrações LDAP enterprise confiáveis e eficientes.

---

_Última Atualização: 2025-06-26_  
_Próxima Revisão: Semanal durante migrações empresariais ativas_  
_Status: PRODUCTION READY - Orquestração ativa de migrações LDAP complexas_
