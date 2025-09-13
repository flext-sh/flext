# FLEXT Build System Documentation

**Unified Build System for the FLEXT Ecosystem**

## Overview

The FLEXT workspace now uses a unified build system with standardized patterns across all 33 projects. This documentation describes the organized build structure, including centralized binaries, standardized Makefiles, and consolidated Docker configurations.

## Build Structure Changes

### Centralized Binary Management

**New `/bin` Directory Structure:**

```
/home/marlonsc/flext/bin/
├── flexcore                  # FlexCore runtime service
├── flext                     # Main FLEXT service
├── (other Go binaries...)    # All Go binaries consolidated here
```

**Benefits:**

- **Single Binary Location**: All executable binaries in one central location
- **Simplified Deployment**: Easy to copy all binaries for deployment
- **Consistent Naming**: Standardized binary naming across projects
- **Path Management**: Simplified PATH configuration for development

### Consolidated Docker Configuration

**Docker Directory Cleanup:**

- **Removed**: 11 duplicate and test Dockerfiles
- **Centralized**: All Docker configurations in `/docker` directory
- **Standardized**: Consistent environment variable naming and health checks
- **Organized**: Production, development, and testing configurations separated

### Unified Makefile Patterns

**Workspace-Level Makefile** (`/home/marlonsc/flext/Makefile`):

- **Build All**: `make build-all` builds both Python and Go projects
- **Quality Gates**: `make validate` runs complete validation pipeline
- **Centralized Management**: Consistent commands across all projects

**Project-Level Makefiles**:

- **Standardized Targets**: All projects have consistent `build`, `test`, `lint`, `validate` targets
- **Binary Management**: Projects build to centralized `/bin` directory
- **Local Development**: `build-local` target for project-specific builds

## Build Commands

### Workspace-Level Commands

```bash
# Complete workspace operations
make setup                    # Install all dependencies and tools
make build-all               # Build all Python and Go projects
make validate                # Run complete validation pipeline
make test-all                # Run tests on all projects
make clean                   # Clean all build artifacts

# Go-specific operations
make build-go                # Build all Go binaries to /bin
make build-python            # Build all Python packages

# Quality gates
make lint-all                # Lint all projects
make type-check-all
make security-all            # Security scan all projects
```

### FlexCore-Specific Commands

```bash
# FlexCore build operations (in /flexcore directory)
make build                   # Build to workspace /bin directory
make build-local             # Build to local flexcore/bin directory
make test                    # Run FlexCore tests with coverage
make validate                # Complete FlexCore validation
make clean                   # Clean FlexCore artifacts only

# FlexCore service operations
make run                     # Start FlexCore service locally
make service-health          # Check FlexCore health status
```

### FLEXT Service Commands

```bash
# FLEXT service operations (in /cmd/flext directory)
make build                   # Build to workspace /bin directory
make build-local             # Build to local cmd/flext/bin directory
make run                     # Start FLEXT service
make test                    # Run tests
make validate                # Complete validation pipeline
```

## Development Workflow

### Initial Setup

```bash
# 1. Setup complete development environment
cd /home/marlonsc/flext
make setup

# 2. Build all projects
make build-all

# 3. Verify build
ls -la bin/
# Should show: flexcore, flext, and other binaries
```

### Daily Development

```bash
# 1. Build specific project (e.g., FlexCore)
cd flexcore
make build                   # Builds to /home/marlonsc/flext/bin/

# 2. Test changes
make test

# 3. Validate before commit
make validate

# 4. Run service locally
/home/marlonsc/flext/bin/flexcore
```

### Quality Validation

```bash
# Complete workspace validation (before commits)
make validate               # Must pass before any commit
# Runs: lint-all + type-check-all + security-all + test-all

# Quick health check
make check                  # Fast validation: lint + type check

# Individual validation steps
make lint-all              # Code linting across all projects
make test-all              # Test execution across all projects
make security-all          # Security scanning across all projects
```

## Docker Operations

### Development Stack

```bash
# Start complete development environment
docker-compose up -d

# Services available:
# - FlexCore: http://localhost:8080
# - FLEXT Service: http://localhost:8081
# - PostgreSQL: localhost:5433
# - Redis: localhost:6380
# - Web Interface: http://localhost:5000
```

### Production Deployment

```bash
# Build production images
docker build -f docker/Dockerfile.flext -t flext:production .

# Deploy with orchestration
docker-compose -f docker-compose.yml up -d
```

## Project Structure

### Workspace Organization

```
/home/marlonsc/flext/
├── bin/                     # All executable binaries
├── cmd/                     # Go CLI applications
│   ├── flext/              # Main FLEXT service
│   ├── flext-cli/          # CLI tools
│   └── ...                 # Other CLI apps
├── flexcore/               # FlexCore runtime service
├── docker/                 # Centralized Docker configurations
├── flext-*/                # Python libraries and services
├── Makefile               # Workspace-level build commands
├── docker-compose.yml     # Development orchestration
└── BUILD_SYSTEM.md        # This documentation
```

### Binary Management

**Centralized Binaries** (`/bin`):

- All Go binaries built to this location
- Consistent naming and permissions
- Single location for deployment packaging
- Simplified PATH management

**Local Builds** (project-specific):

- Available via `make build-local` in each project
- Useful for development and testing
- Does not interfere with workspace binaries

## Migration from Old Structure

### Binary Location Changes

**Before:**

```
/home/marlonsc/flext/cmd/flext/flext              # Scattered
/home/marlonsc/flext/flexcore/flexcore            # Scattered
/home/marlonsc/flext/flext-demo                   # Root level
/home/marlonsc/flext/flext-service                # Root level
```

**After:**

```
/home/marlonsc/flext/bin/flext                    # Centralized
/home/marlonsc/flext/bin/flexcore                 # Centralized
/home/marlonsc/flext/bin/flext-demo              # Centralized
/home/marlonsc/flext/bin/flext-service           # Centralized
```

### Makefile Standardization

**Key Changes:**

- All projects use consistent target names
- Centralized binary building to `/bin`
- Unified quality gate commands
- Standardized help and documentation
- Consistent error handling and output

### Docker Consolidation

**Removed Duplicates:**

- Test-specific Dockerfiles removed
- Simple/demo variants consolidated
- Deployment configurations centralized
- Environment variable naming standardized

## Troubleshooting

### Build Issues

**Binary Permissions:**

```bash
# If binaries are not executable
chmod +x /home/marlonsc/flext/bin/*
```

**Go Module Issues:**

```bash
# Clean and rebuild
cd flexcore
make clean-all
make setup
make build
```

**Path Issues:**

```bash
# Add FLEXT binaries to PATH
export PATH="/home/marlonsc/flext/bin:$PATH"
```

### Common Problems

**"Binary not found":**

- Check that `make build-go` completed successfully
- Verify binaries exist in `/home/marlonsc/flext/bin/`
- Ensure binaries have execute permissions

**"Make target not found":**

- Use `make help` in any project to see available targets
- Ensure you're in the correct directory
- Check that the project has a Makefile

**Docker build failures:**

- Check that Docker daemon is running
- Verify Docker configurations in `/docker` directory
- Ensure all required files are present

## Integration with Development Tools

### IDE Configuration

**VS Code:**

```json
{
  "go.toolsGopath": "/home/marlonsc/flext/bin",
  "go.buildOnSave": "workspace",
  "tasks": [
    {
      "label": "Build All",
      "command": "make",
      "args": ["build-all"],
      "group": "build"
    }
  ]
}
```

### CI/CD Integration

**GitHub Actions Example:**

```yaml
- name: Setup FLEXT Build Environment
  run: make setup

- name: Build All Projects
  run: make build-all

- name: Run Quality Gates
  run: make validate

- name: Package Binaries
  run: tar -czf flext-binaries.tar.gz bin/
```

## Performance Optimizations

### Build Performance

- **Parallel Builds**: Go projects build in parallel where possible
- **Incremental Builds**: Only rebuild changed components
- **Shared Dependencies**: Common dependencies cached

### Resource Management

- **Memory Usage**: Optimized build processes for large workspace
- **Disk Space**: Centralized builds reduce duplication
- **Network**: Cached dependencies for faster builds

## Security Considerations

### Binary Security

- All binaries built with security flags
- Regular security scanning via `make security-all`
- Dependency vulnerability checking

### Access Control

- Binaries have appropriate permissions
- Development vs production configurations separated
- Secrets management integrated with Docker

---

**This build system provides a unified, efficient, and maintainable approach to developing and deploying the entire FLEXT ecosystem.**
