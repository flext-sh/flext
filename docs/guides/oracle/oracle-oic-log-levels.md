# 📊 Oracle OIC Log Levels Configuration Guide

> **Function**: Log level configuration for Oracle OIC CLI operations | **Audience**: DevOps engineers, developers | **Status**: Production-ready

**Complete guide for configuring and managing log levels in Oracle Integration Cloud CLI operations for optimal debugging and production monitoring**

---

## 🧭 **Navigation Context**

**🏠 Root**: [Documentation Home](../../index.md) → **📂 Hub**: [Guides Hub](../index.md) → **📂 Oracle**: [Oracle Hub](./index.md) → **📄 Current**: OIC Log Levels

### **📍 Learning Path Position**

```
[Oracle Hub](./index.md) → **[OIC Log Levels]** → [OIC Integration Guide](./oracle-integration-comprehensive-guide.md)
```

## Overview

The Oracle OIC CLI supports 6 different log levels for controlling the verbosity of output. By default, the CLI runs with **TRACE** level enabled for maximum visibility during development and troubleshooting.

## Available Log Levels

From most verbose to least verbose:

1. **TRACE** - Everything including detailed traces, configuration dumps, and method calls
2. **DEBUG** - Debug messages, useful for troubleshooting
3. **INFO** - Informational messages about what the CLI is doing
4. **WARNING** - Warning messages that might need attention
5. **ERROR** - Error messages when something goes wrong
6. **CRITICAL** - Only critical errors that prevent execution

## Setting Log Level

There are three ways to set the log level:

### 1. Command Line Flag

```bash
# Using --log-level flag
flext-oic --log-level INFO integration list
flext-oic --log-level ERROR config show
flext-oic --log-level=WARNING health check

# Shortcuts for common levels
flext-oic --debug version    # Same as --log-level DEBUG
flext-oic --trace version    # Same as --log-level TRACE
```

### 2. Environment Variable

```bash
# Set via environment variable
export LOG_LEVEL=WARNING
flext-oic integration list

# Or inline
LOG_LEVEL=ERROR flext-oic health check
```

### 3. Default (TRACE)

If no log level is specified, the CLI defaults to TRACE for maximum visibility.

```bash
flext-oic version  # Uses TRACE level by default
```

## Priority Order

The log level is determined in this order (highest priority first):

1. Command line flag (`--log-level`, `--debug`, `--trace`)
2. Environment variable (`LOG_LEVEL`)
3. Default value (`TRACE`)

## Examples by Level

### TRACE Level

Shows everything including:

- Configuration details (with sensitive data masked)
- Method entry/exit
- Detailed request/response information
- All debug and info messages

```bash
flext-oic --log-level TRACE integration list
```

### DEBUG Level

Shows:

- Debug messages
- Important method calls
- Configuration loading
- Error details with stack traces

```bash
flext-oic --debug config show
```

### INFO Level

Shows:

- What the CLI is doing
- Important status messages
- Success/failure notifications

```bash
flext-oic --log-level INFO auth login
```

### WARNING Level

Shows:

- Warning messages
- Potential issues
- Deprecation notices

```bash
flext-oic --log-level WARNING health check
```

### ERROR Level

Shows:

- Error messages only
- Failed operations
- Connection errors

```bash
flext-oic --log-level ERROR integration status INVALID_ID
```

### CRITICAL Level

Shows:

- Only critical failures
- System-level errors
- Unrecoverable errors

```bash
flext-oic --log-level CRITICAL config validate
```

## Best Practices

1. **Development**: Use TRACE or DEBUG for maximum visibility
2. **Testing**: Use INFO to see what's happening without too much detail
3. **Production**: Use WARNING or ERROR to reduce noise
4. **Automation**: Use ERROR or CRITICAL for scripts that parse output

## Output Channels

- **Log messages** go to STDERR
- **Command output** goes to STDOUT

This separation allows you to redirect them independently:

```bash
# Save output to file, show only logs on screen
flext-oic integration list > integrations.json

# Save logs to file, show only output on screen
flext-oic integration list 2> debug.log

# Save both to different files
flext-oic integration list > output.json 2> debug.log
```

## Environment-Specific Configuration

You can set different log levels for different environments:

```bash
# .env.development
LOG_LEVEL=TRACE

# .env.production
LOG_LEVEL=WARNING

# .env.test
LOG_LEVEL=INFO
```

Then use the appropriate .env file for your environment.

## 🔗 **Cross-References**

### **Prerequisites**

- [Oracle Hub](./index.md) - Understanding Oracle integration architecture before log configuration
- [Oracle OIC Guide](./oracle-integration-comprehensive-guide.md) - OIC CLI installation and basic setup
- [Development Guides](../development/index.md) - Development practices for logging and debugging

### **Next Steps**

- [Oracle OIC Integration Guide](./oracle-integration-comprehensive-guide.md) - Advanced OIC CLI operations using configured logging
- [Oracle Troubleshooting](./oracle-integration-api-guide.md) - Using logs for troubleshooting integration issues
- [Oracle Security Guide](./oracle-security-guide.md) - Security considerations for logging sensitive data

### **Related Topics**

- [Development Testing](../../development/testing/index.md) - Testing strategies using different log levels
- [Infrastructure Hub](../../infrastructure/index.md) - Production logging and monitoring infrastructure
- [API Reference Hub](../../api-reference/index.md) - CLI API documentation for logging configuration

---

## 📊 **Document Metrics**

- **Implementation Status**: ✅ Production Ready
- **Log Levels Supported**: 6 comprehensive levels (TRACE to CRITICAL)
- **Configuration Methods**: 3 (CLI flags, environment variables, defaults)
- **Environment Support**: Development, testing, production configurations
- **Last Updated**: June 11, 2025

---

**📂 Guide**: [Oracle Hub](./index.md) | **🏠 Root**: [Documentation Home](../../index.md) | **Framework**: FLX 0.4.0+ | **Updated**: 2025-06-11
