# FLEXT Demo

Demonstration application showcasing FLEXT platform capabilities and best practices.

## Overview

The FLEXT Demo application provides practical examples of using the FLEXT data integration platform. It demonstrates real-world scenarios, integration patterns, and best practices for building data pipelines.

## Features

- **Complete Pipeline Examples**: End-to-end data pipeline demonstrations
- **Integration Patterns**: Common data integration scenarios
- **Best Practices**: Code examples following FLEXT conventions
- **Interactive Examples**: Hands-on demonstrations with real data
- **Performance Benchmarks**: Performance testing and optimization examples
- **Error Handling**: Robust error handling and recovery patterns

## Demo Scenarios

### 1. Basic Data Sync

Demonstrates simple data synchronization between systems:

```bash
# Run basic sync demo
./flext-demo sync --source postgres --target snowflake
```

### 2. Real-time Streaming

Shows real-time data streaming capabilities:

```bash
# Run streaming demo
./flext-demo stream --source kafka --target elasticsearch
```

### 3. Data Transformation

Demonstrates complex data transformation pipelines:

```bash
# Run transformation demo
./flext-demo transform --pipeline dbt-transform
```

### 4. Multi-tenant Architecture

Shows multi-tenant data processing:

```bash
# Run multi-tenant demo
./flext-demo multitenant --tenants 5 --concurrent
```

## Installation

### From Binary

```bash
# Download latest release
curl -LO https://github.com/flext-sh/flext/releases/latest/download/flext-demo
chmod +x flext-demo
```

### From Source

```bash
cd /home/marlonsc/flext/cmd/flext-demo
go build -o flext-demo main.go
```

## Usage

### Interactive Mode

```bash
# Start interactive demo
./flext-demo

# Available commands:
# help     - Show available demos
# list     - List all demo scenarios
# run      - Execute specific demo
# status   - Show demo status
# clean    - Clean up demo data
```

### Command Line Mode

```bash
# Show all available demos
./flext-demo list

# Run specific demo
./flext-demo run --demo data-sync

# Run with custom configuration
./flext-demo run --demo data-sync --config demo-config.yaml

# Enable verbose output
./flext-demo run --demo data-sync --verbose
```

## Demo Catalog

### Data Integration Demos

| Demo            | Description                         | Duration | Complexity   |
| --------------- | ----------------------------------- | -------- | ------------ |
| `basic-sync`    | Simple PostgreSQL to Snowflake sync | 5 min    | Beginner     |
| `streaming-etl` | Kafka to Elasticsearch streaming    | 10 min   | Intermediate |
| `dbt-transform` | DBT transformation pipeline         | 15 min   | Intermediate |
| `multi-source`  | Multiple sources to data warehouse  | 20 min   | Advanced     |

### Architecture Demos

| Demo             | Description                    | Duration | Complexity   |
| ---------------- | ------------------------------ | -------- | ------------ |
| `hexagonal-arch` | Hexagonal Architecture example | 10 min   | Intermediate |
| `ddd-patterns`   | Domain-Driven Design patterns  | 15 min   | Advanced     |
| `cqrs-example`   | CQRS with event sourcing       | 20 min   | Advanced     |
| `microservices`  | Microservices communication    | 25 min   | Expert       |

### Performance Demos

| Demo                 | Description                         | Duration | Complexity   |
| -------------------- | ----------------------------------- | -------- | ------------ |
| `bulk-processing`    | High-volume data processing         | 10 min   | Intermediate |
| `parallel-pipelines` | Parallel pipeline execution         | 15 min   | Advanced     |
| `optimization`       | Performance optimization techniques | 20 min   | Advanced     |

## Configuration

### Demo Configuration File

```yaml
# demo-config.yaml
demo:
  data_size: "1MB" # small, medium, large, or specific size
  duration: "5m" # Demo duration
  cleanup: true # Auto-cleanup after demo
  verbose: false # Verbose output

databases:
  postgres:
    host: localhost
    port: 5432
    database: demo_db

  snowflake:
    account: demo_account
    warehouse: demo_warehouse
    database: demo_db

streaming:
  kafka:
    bootstrap_servers: ["localhost:9092"]

  elasticsearch:
    hosts: ["http://localhost:9200"]
```

### Environment Variables

| Variable           | Description                         | Default          |
| ------------------ | ----------------------------------- | ---------------- |
| `DEMO_CONFIG_PATH` | Path to demo configuration          | demo-config.YAML |
| `DEMO_DATA_SIZE`   | Demo data size (small/medium/large) | small            |
| `DEMO_CLEANUP`     | Auto-cleanup after demo             | true             |
| `DEMO_VERBOSE`     | Enable verbose output               | false            |

## Architecture

The demo application demonstrates:

### Clean Architecture

```
cmd/flext-demo/
├── main.go                     # Application entry point
├── demos/                      # Demo implementations
│   ├── data_sync/             # Data synchronization demos
│   ├── streaming/             # Streaming demos
│   ├── transformation/        # Data transformation demos
│   └── architecture/          # Architecture pattern demos
├── internal/
│   ├── config/               # Demo configuration
│   ├── data/                 # Demo data generators
│   └── utils/                # Demo utilities
└── examples/                 # Code examples
    ├── basic/               # Basic examples
    ├── intermediate/        # Intermediate examples
    └── advanced/           # Advanced examples
```

### Design Patterns

- **Repository Pattern**: Data access abstraction
- **Factory Pattern**: Demo creation and configuration
- **Observer Pattern**: Progress monitoring and notifications
- **Strategy Pattern**: Different demo execution strategies
- **Command Pattern**: Demo command execution

## Development

### Adding New Demos

1. Create demo implementation in `demos/` directory
2. Implement the `Demo` interface
3. Register demo in the demo registry
4. Add configuration and documentation
5. Include tests and examples

### Demo Interface

```go
type Demo interface {
    Name() string
    Description() string
    Duration() time.Duration
    Complexity() Complexity
    Setup(ctx context.Context) error
    Run(ctx context.Context) error
    Cleanup(ctx context.Context) error
}
```

### Building

```bash
# Build demo application
go build -o flext-demo main.go

# Build with all examples
make build-demo

# Build for multiple platforms
make build-demo-all
```

### Testing

```bash
# Run demo tests
go test ./...

# Test specific demo
go test -run TestDataSyncDemo

# Integration tests
go test -tags=integration ./...
```

## Demo Data

### Sample Data Sets

The demo includes various sample datasets:

- **E-commerce**: Orders, customers, products (100K records)
- **IoT**: Sensor data, device metrics (1M records)
- **Financial**: Transactions, accounts, balances (500K records)
- **Social**: Users, posts, interactions (2M records)

### Data Generators

```bash
# Generate sample data
./flext-demo generate --type ecommerce --size 100k

# Generate streaming data
./flext-demo generate --type iot --stream --rate 1000/sec
```

## Educational Content

### Learning Path

1. **Beginner**: Start with `basic-sync` demo
2. **Intermediate**: Progress to `streaming-etl` and `dbt-transform`
3. **Advanced**: Explore `multi-source` and architecture demos
4. **Expert**: Study `microservices` and performance demos

### Code Examples

Each demo includes:

- Complete source code
- Configuration examples
- Best practice explanations
- Common pitfall warnings
- Performance considerations

## Troubleshooting

### Common Issues

1. **Demo Data Not Found**: Run data generation first
2. **Connection Failed**: Check database/service connectivity
3. **Permission Denied**: Ensure proper access credentials
4. **Performance Issues**: Reduce data size for testing

### Debug Mode

```bash
# Enable debug output
./flext-demo run --demo data-sync --debug

# Trace execution
DEMO_TRACE=true ./flext-demo run --demo streaming-etl
```

## Contributing

### Guidelines

1. Follow Go conventions and best practices
2. Include comprehensive documentation
3. Add tests for all demo scenarios
4. Ensure demos are reproducible
5. Provide clear educational value

### Demo Standards

- Keep demos focused and concise
- Include real-world scenarios
- Provide multiple complexity levels
- Ensure reliable execution
- Document learning objectives

## License

MIT License - see [LICENSE](../../LICENSE) for details.

## Related

- [FLEXT CLI](../flext-cli/) - Command-line interface
- [FLEXT Server](../flext-server/) - API server
- [FLEXT Core](../../flext-core/) - Core framework library
- [Documentation](../../docs/) - Complete documentation
