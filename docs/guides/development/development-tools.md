# Development and Integration Tools Guide

> **Related Documentation:**
>
> - [Oracle Platform Resources](./oracle-platform-resources.md) - Oracle documentation and API specifications
> - [Integration Examples](./integration-examples-patterns.md) - Implementation patterns and examples
> - [WMS CLI Guide](./wms-cli-guide.md) - Oracle WMS command-line operations
> - [JWT Service Guide](./jwt-service-guide.md) - Authentication testing and setup

This guide covers practical tools, collections, and schemas that support development and testing of Oracle integrations within the PyAuto hexagonal architecture.

## Tool Categories

### Postman Collections (`/postman/`)

API testing and development tools:

- **Oracle Integration API Collections**: Complete OIC service test suites
- **WMS REST API Test Suites**: Oracle WMS endpoint validation
- **Authentication Examples**: OAuth2 and JWT flow testing
- **Environment Configurations**: Multi-environment setup templates

### Data Schemas (`/schemas/`)

Structure definitions and validation schemas:

- **JSON Schemas**: API payload validation and code generation
- **XML Schemas (XSD)**: SOAP service and data format definitions
- **Data Transformation Mappings**: Field-level mapping specifications
- **Validation Schemas**: Business rule and constraint definitions

### WMS Mappings (`/mappings/`)

Oracle WMS-specific data transformations:

- **Inventory Mapping Tables**: SKU and location transformations
- **Order Flow Transformations**: Order lifecycle data mappings
- **Shipment Confirmation Mappings**: Delivery and tracking data formats
- **Receipt Advice Formats**: Inbound logistics data structures

## Usage Guidelines

### Postman Collection Management

#### Setup Process

1. **Import Collections**: Load Oracle API collections into Postman workspace
2. **Configure Environments**: Set up variables for development, staging, production
3. **Update Authentication**: Configure OAuth2/JWT for current security standards
4. **Validate Endpoints**: Test API connectivity during adapter development

#### Environment Configuration

```json
{
  "oracle_base_url": "https://your-oracle-instance.com",
  "oauth_client_id": "{{client_id}}",
  "oauth_client_secret": "{{client_secret}}",
  "jwt_token": "{{bearer_token}}",
  "api_version": "v3"
}
```

#### Best Practices

- **Version Control**: Keep collections in git with environment templates
- **Security**: Never commit actual credentials or tokens
- **Documentation**: Maintain collection descriptions and test scenarios
- **Automation**: Use Newman for CI/CD integration testing

### Schema Management

#### Validation Workflow

1. **Define Schemas**: Create JSON/XML schemas for all Oracle interfaces
2. **Generate Code**: Use schemas to generate adapter interfaces and models
3. **Validate Data**: Implement schema validation at port boundaries
4. **Version Control**: Track schema evolution with Oracle API updates

#### Code Generation

```bash
# Generate TypeScript interfaces from JSON schema
quicktype --src oracle-wms-order.schema.json --out order-types.ts

# Generate Python models from OpenAPI spec
openapi-generator generate -i oracle-api.yaml -g python -o ./generated/
```

#### Integration with FLEXT

- **Port Definitions**: Use schemas to define port interface contracts
- **Adapter Validation**: Validate Oracle responses against schemas
- **Domain Models**: Generate domain entities from business schemas
- **Testing**: Use schemas for property-based testing

### Data Mapping Implementation

#### Mapping Strategy

1. **Reference Documentation**: Use mappings to understand Oracle data flows
2. **Adapt Requirements**: Modify mappings for current business requirements
3. **Domain Implementation**: Implement transformations in domain services
4. **Test with Real Data**: Validate mappings with actual Oracle data samples

#### Architecture Placement

```
Oracle Data → Adapter (Raw Transform) → Port → Domain Service (Business Transform) → Domain Model
```

#### Mapping Examples

```python
# Inventory mapping in domain service
class InventoryMappingService:
    def map_oracle_to_domain(self, oracle_item: dict) -> InventoryItem:
        return InventoryItem(
            sku=oracle_item.get("ITEM_CODE"),
            quantity=oracle_item.get("QTY_ON_HAND", 0),
            location=oracle_item.get("LOCATION_ID"),
            status=self._map_status(oracle_item.get("STATUS"))
        )
```

## Architecture Integration

### Hexagonal Architecture Support

#### Adapter Testing

- **Postman Collections**: Validate adapter implementations against Oracle APIs
- **Mock Services**: Use collections to create Oracle API mocks for testing
- **Contract Testing**: Verify adapter behavior matches expected Oracle responses
- **Integration Testing**: End-to-end validation of adapter connectivity

#### Port Interface Design

- **Schema Contracts**: Define clear data contracts using schemas
- **Validation Boundaries**: Implement schema validation at port boundaries
- **Error Mapping**: Map Oracle errors to domain exceptions using schemas
- **Version Management**: Handle Oracle API evolution through schema versioning

#### Domain Service Support

- **Business Logic**: Mappings inform domain transformation implementations
- **Data Validation**: Business rule validation using enhanced schemas
- **Workflow Design**: Oracle process flows guide domain service orchestration
- **Performance Optimization**: Mapping analysis identifies optimization opportunities

### Testing Integration

#### Unit Testing

```python
def test_oracle_adapter_with_mock_data():
    # Use schema-validated mock data
    mock_response = load_mock_from_schema("oracle-order-response.json")
    adapter = OracleWmsAdapter()
    result = adapter.get_order(order_id="12345")
    assert_matches_schema(result, "domain-order.schema.json")
```

#### Integration Testing

```python
def test_oracle_integration_with_postman():
    # Run Postman collection tests via Newman
    result = newman.run(collection="oracle-wms-tests.json",
                       environment="test-env.json")
    assert result.success
```

#### Contract Testing

```python
def test_oracle_contract_compliance():
    # Verify Oracle API matches our expectations
    oracle_client = OracleWmsClient()
    response = oracle_client.get_inventory("ITEM001")
    validate(response, oracle_inventory_schema)
```

## Tool Configuration

### Development Environment Setup

#### Prerequisites

- **Postman**: Version 10+ with Newman CLI
- **JSON Schema Tools**: quicktype, ajv-cli for validation
- **Oracle Access**: Valid credentials for target Oracle instances
- **FLEXT Framework**: Local development environment with adapter interfaces

#### Installation

```bash
# Install Newman for CLI testing
npm install -g newman

# Install schema validation tools
npm install -g quicktype ajv-cli

# Install Oracle client libraries
pip install oracledb
```

#### Configuration Files

```yaml
# tools-config.yaml
postman:
  collections_dir: "./postman/collections"
  environments_dir: "./postman/environments"

schemas:
  source_dir: "./schemas"
  generated_dir: "./generated"

oracle:
  test_instance: "https://test-oracle.company.com"
  prod_instance: "https://prod-oracle.company.com"
```

### Continuous Integration

#### CI/CD Pipeline Integration

```yaml
# .github/workflows/oracle-integration-tests.yml
name: Oracle Integration Tests
on: [push, pull_request]

jobs:
  test-oracle-apis:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Postman Tests
        run: newman run postman/oracle-wms-tests.json
      - name: Validate Schemas
        run: ajv test --spec=draft7 schemas/*.schema.json
```

## Quality Standards

### Documentation Standards

- **English Language**: All tool documentation in clear English
- **Current Versions**: Support for latest Oracle Cloud versions (23c+)
- **Practical Examples**: Working configurations and usage examples
- **Architecture Alignment**: Demonstrate hexagonal architecture principles

### Maintenance Practices

- **Regular Updates**: Monthly review of tool compatibility with Oracle updates
- **Version Control**: Track all tool configurations and schemas in git
- **Team Training**: Regular training sessions on tool usage and best practices
- **Performance Monitoring**: Track tool performance and Oracle API response times

## Common Use Cases

### 1. New Adapter Development

1. **Start with Postman**: Test Oracle API endpoints manually
2. **Extract Schema**: Create JSON schema from API responses
3. **Generate Interfaces**: Use quicktype to generate adapter interfaces
4. **Implement Adapter**: Code adapter using generated interfaces
5. **Validate Implementation**: Run Postman tests against adapter

### 2. Oracle API Changes

1. **Update Collections**: Modify Postman collections for new API versions
2. **Schema Evolution**: Update schemas to match new Oracle responses
3. **Regenerate Code**: Update generated interfaces and models
4. **Test Compatibility**: Validate existing adapters against new APIs
5. **Deploy Changes**: Update production adapters with new implementations

### 3. Performance Optimization

1. **Baseline Testing**: Use Postman to establish performance baselines
2. **Identify Bottlenecks**: Analyze Oracle API response times and patterns
3. **Optimize Mappings**: Streamline data transformations based on analysis
4. **Validate Improvements**: Measure performance gains with updated tests
5. **Monitor Production**: Continuous monitoring of Oracle integration performance

## Metadata

- **Tool Compatibility**: Postman 10+, Newman CLI, JSON Schema Draft 7+
- **Oracle Versions**: WMS Cloud 24c+, OIC 3.0+, Database 23c+
- **Last Updated**: January 2025
- **Project Alignment**: FLEXT Framework, Hexagonal Architecture

## See Also

- [Oracle Platform Resources](./oracle-platform-resources.md) - Oracle documentation and specifications
- [Integration Examples](./integration-examples-patterns.md) - Implementation patterns and examples
- [WMS Operations Guide](./wms-operations-guide.md) - Oracle WMS specific operations
- [Testing Guidelines](../development/testing-standards.md) - Testing strategy and standards
