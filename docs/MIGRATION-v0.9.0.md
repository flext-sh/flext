# FLEXT Ecosystem - Migration Guide v0.9.0

**Release Date**: 2025-07-30  
**Migration Priority**: MANDATORY for all FLEXT ecosystem projects  
**Breaking Changes**: YES - Version dependencies updated across entire ecosystem

---

## 🚨 CRITICAL MIGRATION REQUIREMENTS

### 1. Version Update Overview

Version 0.9.0 represents a major synchronization update across the entire FLEXT ecosystem:

- **33 Python projects** updated from mixed versions (0.8.0, 1.0.0, 2.0.0) to **0.9.0**
- **Go projects** (FlexCore) updated to version **0.9.0**
- **Cross-project dependencies** synchronized to reference **0.9.0**
- **Docker images** and configuration files updated
- **Documentation** and examples updated with consistent versioning

### 2. Projects Affected

**Core Libraries (2)**:

- flext-core: 0.8.0 → 0.9.0
- flext-observability: 0.8.0 → 0.9.0

**Foundation Libraries (6)**:

- flext-db-oracle: 0.8.0 → 0.9.0
- flext-ldap: 0.8.0 → 0.9.0
- flext-ldif: 0.8.0 → 0.9.0
- flext-oracle-wms: 0.8.0 → 0.9.0
- flext-grpc: 0.8.0 → 0.9.0
- flext-meltano: 0.8.0 → 0.9.0

**Application Services (5)**:

- flext-api: 1.0.0 → 0.9.0
- flext-auth: 1.0.0 → 0.9.0
- flext-web: 1.0.0 → 0.9.0
- flext-quality: 0.8.0 → 0.9.0
- flext-cli: 0.8.0 → 0.9.0

**Singer Ecosystem (15)**:

- All flext-tap-\* projects: 0.8.0 → 0.9.0
- All flext-target-\* projects: 0.8.0 → 0.9.0
- All flext-dbt-\* projects: 0.8.0 → 0.9.0
- flext-oracle-oic-ext: 0.8.0 → 0.9.0

**Plugin System (1)**:

- flext-plugin: 0.8.0 → 0.9.0

**Legacy/Specialized (2)**:

- client-a-oud-mig: 2.0.0 → 0.9.0
- client-b-meltano-native: 1.0.0 → 0.9.0

**Go Services**:

- FlexCore: 0.8.0 → 0.9.0
- FLEXT Service: 0.8.0 → 0.9.0

---

## 🛠️ MIGRATION STEPS

### Step 1: Environment Preparation

1. **Backup Current Environment** (MANDATORY):

```bash
# Create backup of current workspace
cp -r /path/to/flext /path/to/flext-backup-pre-0.9.0
cd /path/to/flext
git stash  # Stash any uncommitted changes
```

2. **Update Git Repository**:

```bash
git fetch origin
git checkout main
git pull origin main
```

### Step 2: Dependency Updates

1. **Update Python Dependencies**:

```bash
# For each Python project, update pyproject.toml dependencies
# Example for flext-api:
cd flext-api
# Check if flext-core dependency needs updating
grep -n "flext-core" pyproject.toml
# Update if using local file reference: flext-core = {path = "../flext-core", develop = true}
```

2. **Update Go Dependencies**:

```bash
cd flexcore
go mod tidy
go mod download
```

### Step 3: Version Verification

1. **Verify Python Package Versions**:

```bash
# Run this script to verify all projects have correct version
for project in flext-*/ client-a-*/ client-b-*/; do
  if [ -f "$project/pyproject.toml" ]; then
    echo "=== $project ==="
    grep -n "^version" "$project/pyproject.toml"
  fi
done
```

2. **Verify Go Package Versions**:

```bash
cd flexcore && grep -n "version" config.yaml
cd flexcore && grep -n "version" flexcore-node.yaml
```

### Step 4: Build Verification

1. **Test Python Projects**:

```bash
# Test core library first
cd flext-core
make validate  # Must pass completely
make build

# Test dependent projects
cd ../flext-api
make validate
make build

# Continue for other projects...
```

2. **Test Go Services**:

```bash
cd flexcore
go build .
go test ./...

cd ../cmd/flext
go build .
```

### Step 5: Integration Testing

1. **Start Services and Test Integration**:

```bash
# Start FlexCore service
cd flexcore && ./flexcore &

# Start FLEXT service
cd cmd/flext && ./flext &

# Test health endpoints
curl http://localhost:8080/health  # FlexCore
curl http://localhost:8081/health  # FLEXT Service
```

---

## ⚠️ BREAKING CHANGES

### 1. Version Synchronization

**BREAKING**: Projects using hardcoded version references in code must be updated.

**Before**:

```python
# In various files
VERSION = "0.8.0"
__version__ = "1.0.0"
version = "2.0.0"
```

**After**:

```python
# All projects now use
VERSION = "0.9.0"
__version__ = "0.9.0"
version = "0.9.0"
```

**Action Required**: Update any hardcoded version references in your custom code.

### 2. Cross-Project Dependencies

**BREAKING**: Local file references between projects may need updates if paths changed.

**Before**:

```toml
[tool.poetry.dependencies]
flext-core = {path = "../flext-core", develop = true}
```

**After**:
Same pattern, but ensure paths are correct and both projects are on v0.9.0.

**Action Required**: Verify all local file references in your pyproject.toml files.

### 3. Docker Image Tags

**BREAKING**: Docker images now tagged with v0.9.0.

**Before**:

```dockerfile
LABEL version="0.8.0"
FROM flext/base:0.8.0
```

**After**:

```dockerfile
LABEL version="0.9.0"
FROM flext/base:0.9.0
```

**Action Required**: Update any custom Docker files referencing FLEXT images.

### 4. API Version Headers

**BREAKING**: API services may include version in response headers.

**Before**:

```http
X-API-Version: 0.8.0
```

**After**:

```http
X-API-Version: 0.9.0
```

**Action Required**: Update any client code that validates API version headers.

---

## 🔄 COMPATIBILITY NOTES

### Backward Compatibility

- **Python APIs**: No breaking changes in public APIs
- **Go APIs**: No breaking changes in public interfaces
- **Database Schemas**: No migrations required
- **Configuration Files**: No breaking changes in config format
- **Plugin Interfaces**: Maintained backward compatibility

### Forward Compatibility

- Version 0.9.0 is forward-compatible with planned v1.0.0 release
- Deprecation warnings added for features planned for removal in v1.0.0
- New features added are opt-in and don't affect existing functionality

---

## 🧪 TESTING MIGRATION

### 1. Unit Tests

```bash
# Run tests for each project to ensure compatibility
make test-all  # From workspace root
```

### 2. Integration Tests

```bash
# Test service integration
cd flexcore && ./flexcore &
cd cmd/flext && ./flext &

# Run integration test suite (if available)
make test-integration
```

### 3. End-to-End Tests

```bash
# Run E2E tests with Docker
docker-compose -f docker/docker-compose.e2e.yml up --abort-on-container-exit
```

---

## 🚨 ROLLBACK PROCEDURE

If issues are encountered during migration:

### Quick Rollback

```bash
# Stop services
pkill -f flexcore
pkill -f flext

# Restore backup
rm -rf /path/to/flext
mv /path/to/flext-backup-pre-0.9.0 /path/to/flext
cd /path/to/flext

# Restart services with previous version
# ... follow previous startup procedure
```

### Git Rollback

```bash
# If changes were committed
git log --oneline -10  # Find commit before version update
git reset --hard <commit-hash>

# Or revert specific version update commits
git revert <version-update-commit-hash>
```

---

## 📋 POST-MIGRATION CHECKLIST

- [ ] All Python projects build successfully (`make build`)
- [ ] All Go projects build successfully (`go build`)
- [ ] Unit tests pass for all projects (`make test`)
- [ ] Integration tests pass (`make test-integration`)
- [ ] Services start without errors
- [ ] Health checks return 200 OK
- [ ] API endpoints respond correctly
- [ ] Plugin system loads plugins without errors
- [ ] Database connections work
- [ ] Cache systems (Redis) accessible
- [ ] Logging systems functional
- [ ] Monitoring/observability working
- [ ] Documentation reflects new version
- [ ] CI/CD pipelines pass

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue 1: Build Failures

**Symptom**: `make build` fails with dependency errors
**Solution**:

```bash
# Clean and reinstall dependencies
make clean-all
make install-dev
make build
```

### Issue 2: Import Errors

**Symptom**: Python import errors for flext modules
**Solution**:

```bash
# Verify installations
cd flext-core && poetry install
cd ../flext-api && poetry install
# Check PYTHONPATH if needed
```

### Issue 3: Service Startup Failures

**Symptom**: FlexCore or FLEXT services fail to start
**Solution**:

```bash
# Check configuration files
cd flexcore && grep -n "version" config.yaml
# Verify database connectivity
docker-compose up -d postgres redis
```

### Issue 4: Version Mismatch Errors

**Symptom**: Services report version conflicts
**Solution**:

```bash
# Verify all projects are on 0.9.0
find . -name "pyproject.toml" -exec grep -l "version.*0.9.0" {} \;
# Update any remaining projects
```

---

## 📞 SUPPORT

If you encounter issues during migration:

1. **Check logs**: Enable debug logging (`LOG_LEVEL=DEBUG`)
2. **Verify checklist**: Ensure all post-migration items completed
3. **Review common issues**: Check solutions above
4. **Rollback if needed**: Use rollback procedure if critical issues
5. **Get help**: Contact FLEXT team with specific error details

---

## 📈 NEXT STEPS

After successful migration to v0.9.0:

1. **Monitor systems** for 24-48 hours
2. **Update monitoring dashboards** with new version tags
3. **Update documentation** links and references
4. **Plan for v1.0.0** (stable release coming soon)
5. **Update deployment scripts** with new version references

---

**Migration completed successfully!** 🎉

The FLEXT ecosystem is now synchronized on version 0.9.0 with improved consistency and reduced maintenance overhead.
