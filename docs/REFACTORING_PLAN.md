# FLEXT Ecosystem Refactoring Plan - Complete Architecture Separation

**Status**: IN PROGRESS  
**Priority**: CRITICAL  
**Architecture Decision**: Separate FLEXT Service from FlexCore Runtime Container

## 🎯 Core Architecture Principle

**FLEXT Service** → **FlexCore (gRPC)** → **Runtime Plugins** (Meltano, Ray, K8s, Gopy, etc.)

- **FLEXT**: Business logic, API, Clean Architecture, knows NOTHING about runtime specifics
- **FlexCore**: Runtime container, plugin orchestration, manages ALL runtime execution
- **Communication**: ONLY via gRPC between FLEXT ↔ FlexCore

---

## 📋 PHASE 1: Analysis & Planning (COMPLETED)

### ✅ 1.1 Architecture Analysis

- [x] Identify current mixing of concerns between FLEXT and FlexCore
- [x] Map current dependencies and imports
- [x] Identify files that need to be moved/refactored/removed

### ✅ 1.2 Container Builder Implementation  

- [x] Implement generic container builder in `/pkg/container/builder.go`
- [x] Create FlexCore gRPC client interface
- [x] Add runtime plugin system architecture
- [x] Integrate Clean Architecture patterns

---

## 📋 PHASE 2: File Structure Reorganization (IN PROGRESS)

### 🔄 2.1 Move Runtime-Specific Code to FlexCore

**Files to MOVE from `/pkg/` to `/flexcore/pkg/`:**

- [ ] `/pkg/utils/gopy/meltano_adapter.go` → `/flexcore/pkg/runtimes/gopy/`
- [ ] `/pkg/domain/meltano/` → `/flexcore/pkg/runtimes/meltano/`
- [ ] All runtime-specific handlers and services
- [ ] Plugin execution logic

**Files to CREATE in FlexCore:**

- [ ] `/flexcore/pkg/runtimes/meltano/service.go`
- [ ] `/flexcore/pkg/runtimes/ray/service.go`
- [ ] `/flexcore/pkg/runtimes/windmill/service.go`
- [ ] `/flexcore/pkg/runtimes/kubernetes/service.go`
- [ ] `/flexcore/pkg/runtimes/gopy/bridge.go`
- [ ] `/flexcore/pkg/grpc/server.go` - gRPC server implementation
- [ ] `/flexcore/pkg/grpc/handlers.go` - Runtime execution handlers

### 🔄 2.2 Clean FLEXT Service Code

**Files to REMOVE from FLEXT:**

- [ ] `/pkg/interfaces/cli/commands/dbt_cli_commands.go` → Move to FlexCore
- [ ] `/pkg/interfaces/cli/commands/dbt_commands.go` → Move to FlexCore  
- [ ] `/pkg/interfaces/cli/commands/singer_commands.go` → Move to FlexCore
- [ ] All runtime-specific CLI commands
- [ ] Direct runtime integrations

**Files to REFACTOR in FLEXT:**

- [ ] `/cmd/flext/main.go` - Remove runtime dependencies, add FlexCore gRPC client
- [ ] `/pkg/container/container.go` - Remove runtime handlers, add gRPC client
- [ ] `/pkg/server/server.go` - Remove runtime endpoints, proxy to FlexCore
- [ ] Clean Architecture services - remove runtime specifics

### 🔄 2.3 Update Import Paths

**Global find/replace operations:**

- [ ] Update all FlexCore imports in FLEXT to use gRPC clients
- [ ] Remove direct runtime imports from FLEXT code
- [ ] Update go.mod dependencies
- [ ] Fix broken imports after file moves

---

## 📋 PHASE 3: gRPC Protocol Implementation

### 🔧 3.1 gRPC Protocol Definition

- [ ] Create `/flexcore/api/grpc/flexcore.proto`
- [ ] Define runtime execution service interface
- [ ] Define runtime management operations
- [ ] Generate Go gRPC code

### 🔧 3.2 FlexCore gRPC Server

- [ ] Implement gRPC server in `/flexcore/pkg/grpc/server.go`
- [ ] Create runtime routing logic
- [ ] Add health checks and status endpoints
- [ ] Implement authentication/authorization

### 🔧 3.3 FLEXT gRPC Client  

- [ ] Complete implementation in `/pkg/container/implementations.go`
- [ ] Add connection management and retry logic
- [ ] Implement runtime discovery
- [ ] Add error handling and logging

---

## 📋 PHASE 4: Runtime Plugin System (FlexCore)

### 🔧 4.1 Generic Runtime Interface

- [ ] Create `/flexcore/pkg/runtime/interface.go`
- [ ] Define common runtime lifecycle methods
- [ ] Add plugin discovery mechanism
- [ ] Implement runtime registry

### 🔧 4.2 Specific Runtime Implementations

- [ ] **Meltano Runtime**: `/flexcore/pkg/runtimes/meltano/`
  - [ ] Move from flext-meltano integration
  - [ ] Implement Meltano command execution
  - [ ] Add pipeline management
  - [ ] Singer tap/target integration

- [ ] **Gopy Runtime**: `/flexcore/pkg/runtimes/gopy/`
  - [ ] Python-Go bridge implementation
  - [ ] Process management
  - [ ] Data serialization

- [ ] **Ray Runtime**: `/flexcore/pkg/runtimes/ray/`
  - [ ] Ray cluster integration
  - [ ] Distributed task execution
  - [ ] Resource management

- [ ] **Windmill Runtime**: `/flexcore/pkg/runtimes/windmill/`
  - [ ] Windmill API integration
  - [ ] Workflow execution
  - [ ] Job scheduling

- [ ] **Kubernetes Runtime**: `/flexcore/pkg/runtimes/kubernetes/`
  - [ ] K8s job management
  - [ ] Pod lifecycle
  - [ ] Resource allocation

### 🔧 4.3 Runtime Plugin Registration

- [ ] Dynamic plugin loading system
- [ ] Runtime health monitoring
- [ ] Plugin versioning and compatibility
- [ ] Configuration management per runtime

---

## 📋 PHASE 5: Configuration & Environment

### ⚙️ 5.1 FlexCore Configuration

- [ ] Move runtime configs from FLEXT to FlexCore
- [ ] Update `/flexcore/pkg/config/config.go`
- [ ] Add gRPC server configuration
- [ ] Runtime-specific configurations

### ⚙️ 5.2 FLEXT Configuration Cleanup

- [ ] Remove runtime configurations
- [ ] Add FlexCore gRPC endpoint config
- [ ] Update environment variables
- [ ] Clean feature flags

### ⚙️ 5.3 Docker & Deployment

- [ ] Update `/docker-compose.yml` with FlexCore service
- [ ] Separate FlexCore and FLEXT containers
- [ ] Update environment variables
- [ ] Network configuration for gRPC

---

## 📋 PHASE 6: Documentation Updates

### 📝 6.1 Architecture Documentation

- [ ] Update `/docs/architecture/ecosystem-architecture.md`
- [ ] Create `/docs/architecture/grpc-communication.md`
- [ ] Update `/docs/architecture/service-architecture.md`  
- [ ] Add runtime plugin documentation

### 📝 6.2 API Documentation

- [ ] Generate gRPC API documentation
- [ ] Update REST API docs (remove runtime endpoints)
- [ ] Create FlexCore API reference
- [ ] Update client SDK documentation

### 📝 6.3 Development Documentation

- [ ] Update `/CLAUDE.md` with new architecture
- [ ] Update `/flexcore/CLAUDE.md` with runtime development
- [ ] Create runtime plugin development guide
- [ ] Update deployment guides

### 📝 6.4 README Updates

- [ ] Update main `/README.md`
- [ ] Update `/flexcore/README.md`
- [ ] Update all subproject READMEs
- [ ] Add migration guide

---

## 📋 PHASE 7: Code Quality & Testing

### 🧪 7.1 Testing Strategy

- [ ] Unit tests for gRPC communication
- [ ] Integration tests FLEXT ↔ FlexCore
- [ ] Runtime plugin tests
- [ ] End-to-end workflow tests

### 🧪 7.2 Quality Gates

- [ ] Update linting rules for new structure
- [ ] Fix all import issues
- [ ] Run comprehensive test suite
- [ ] Security audit for gRPC communication

### 🧪 7.3 Performance Testing

- [ ] gRPC communication benchmarks
- [ ] Runtime plugin performance tests
- [ ] Load testing distributed execution
- [ ] Memory usage analysis

---

## 📋 PHASE 8: Migration & Validation

### 🔄 8.1 Legacy Code Cleanup

- [ ] Remove deprecated files
- [ ] Clean up unused dependencies
- [ ] Update go.mod files
- [ ] Remove old build artifacts

### 🔄 8.2 Backwards Compatibility

- [ ] Create migration scripts
- [ ] Add deprecation warnings
- [ ] Provide compatibility layer if needed
- [ ] Update upgrade documentation

### 🔄 8.3 Final Validation

- [ ] Full ecosystem test
- [ ] All examples working
- [ ] Documentation accuracy
- [ ] Performance benchmarks

---

## 🎯 Success Criteria

### ✅ **Architecture Separation Complete**

- FLEXT service has NO direct runtime dependencies
- All runtime execution goes through FlexCore gRPC
- Clean separation of concerns maintained

### ✅ **Functionality Preserved**  

- All current features working via new architecture
- Performance maintained or improved  
- Error handling robust

### ✅ **Developer Experience**

- Clear development workflows
- Comprehensive documentation
- Easy plugin development
- Simple deployment process

### ✅ **Production Ready**

- Scalable gRPC communication
- Robust error handling
- Monitoring and observability
- Security validated

---

## 📈 Execution Timeline

- **Phase 1**: ✅ COMPLETED
- **Phase 2**: 🔄 IN PROGRESS (3 days)
- **Phase 3**: ⏳ PLANNED (2 days)  
- **Phase 4**: ⏳ PLANNED (4 days)
- **Phase 5**: ⏳ PLANNED (1 day)
- **Phase 6**: ⏳ PLANNED (2 days)
- **Phase 7**: ⏳ PLANNED (2 days)
- **Phase 8**: ⏳ PLANNED (1 day)

**Total Estimated Time**: 15 days

---

## 🚨 Critical Dependencies

1. **gRPC Protocol Definition** - Blocks all communication
2. **Runtime Interface Design** - Blocks plugin implementations  
3. **File Movement Coordination** - Avoid breaking builds
4. **Import Path Updates** - Must be coordinated across files

---

## 📝 Notes

- This refactoring touches almost every major component
- Requires careful coordination to avoid breaking builds
- All changes should be backwards compatible where possible
- Extensive testing required due to architectural changes

**Last Updated**: 2025-08-04
**Assigned**: Claude Code Assistant  
**Status**: Active Development
