# FLX Log Levels Guide

> **Related Documentation:**
>
> - [Development Standards](../development/standardization-plan.md) - Logging configuration standards
> - [JWT Service Guide](./jwt-service-guide.md) - Authentication logging patterns
> - [Quick Start](../getting-started/quickstart.md) - CLI usage examples

The FLX CLI supports 6 different log levels for controlling the verbosity of output. By default, the CLI runs with **TRACE** level enabled for maximum visibility.

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
