# WORKSPACE.md - FLEXT WORKSPACE ORGANIZATION

**Hierarquia**: WORKSPACE-LEVEL - Organização do workspace flext
**Referência**: `/home/marlonsc/CLAUDE.md` → Metodologia universal
**Última Atualização**: 2025-01-25

---

## 🏗️ WORKSPACE STRUCTURE

```
/home/marlonsc/flext/
├── flext-api/           ← Main REST API service
├── flext-core/          ← Core libraries and patterns  
├── flext-grpc/          ← gRPC service layer
├── flext-auth/          ← Authentication service
├── flext-web/           ← Web frontend
├── flext-cli/           ← Command line interface
├── flext-quality/       ← Quality assurance tools
└── flext-observability/ ← Monitoring and logging
```

---

## 📋 PROJECT STATUS OVERVIEW

### ✅ COMPLETED PROJECTS (100% Quality Gates)
1. **flext-grpc** - gRPC service implementation
2. **flext-core** - Core patterns and libraries

### 🔄 ACTIVE DEVELOPMENT  
1. **flext-api** - REST API service (IN PROGRESS)
   - ✅ Lint: 0 errors
   - 🔄 TypeCheck: In progress
   - ⏳ Tests: Pending 100% coverage

### ⏳ PENDING PROJECTS
1. **flext-auth** - Authentication service
2. **flext-web** - Web frontend  
3. **flext-cli** - Command line interface
4. **flext-observability** - Monitoring

---

## 💡 WORKSPACE PATTERNS

### Universal Patterns (Apply to ALL projects)
1. **FlextLoggerFactory** from flext-core
2. **FlextResult** for all operation returns
3. **FlextXxx** naming conventions for classes
4. **Zero tolerance** for lint/mypy errors
5. **100% test coverage** requirement

### Project-Specific Documentation
- Each project has its own `CLAUDE.md` with specific patterns
- `QUALITY_GATES.md` for project status tracking
- `PATTERNS.md` for implementation guidelines

---

## 🚨 CRITICAL WORKSPACE RULES

### File Organization
- **NEVER** create files outside project boundaries
- **ALWAYS** use project-specific CLAUDE.md for guidance
- **MAINTAIN** clean separation between projects

### Quality Standards
- **ALL** projects must pass quality gates before completion
- **NO** project dependencies on non-compliant projects
- **ZERO** shared mocks/fallbacks between projects

### Development Flow
1. Check project CLAUDE.md for specific patterns
2. Run quality gates: `make lint && make type-check && make test`
3. Ensure FlextXxx naming compliance
4. Verify integration with flext-core patterns

---

**WORKSPACE PRINCIPLE**: Each project is independent but follows universal FLEXT patterns